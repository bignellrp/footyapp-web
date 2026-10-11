"""Guard Watch submissions and journal each non-idempotent backend operation.

The existing API cannot atomically update a score and ten players. If a request
may have taken effect, leave the receipt blocked for manual reconciliation.
Never automatically repeat an uncertain increment.
"""
import hashlib
import json
import os
import sqlite3
from datetime import date
from pathlib import Path
from urllib.parse import quote
from uuid import UUID

import requests


class PushError(Exception):
    def __init__(self, code, message, status):
        self.code, self.message, self.status = code, message, status


def validate(payload):
    if not isinstance(payload, dict) or set(payload) != {
        'submissionId', 'date', 'teamA', 'teamB', 'scoreTeamA', 'scoreTeamB', 'goals'
    }:
        raise PushError('invalid_submission', 'Expected a complete game submission.', 400)
    try:
        UUID(payload['submissionId'])
        if date.fromisoformat(payload['date']).isoformat() != payload['date']:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise PushError('invalid_submission', 'Use a UUID submissionId and YYYY-MM-DD date.', 400)
    all_names = []
    for team in ('teamA', 'teamB'):
        names = payload[team]
        if (not isinstance(names, list) or not names or len(names) > 20
                or any(not isinstance(n, str) or not n.strip() or len(n) > 120 for n in names)):
            raise PushError('invalid_submission', 'Each team must contain valid player names.', 400)
        all_names += names
    if len(set(all_names)) != len(all_names):
        raise PushError('invalid_submission', 'A player may only appear once.', 400)
    goals = payload['goals']
    if not isinstance(goals, dict) or set(goals) != set(all_names):
        raise PushError('invalid_submission', 'Provide goals for every player in these teams.', 400)
    for value in [payload['scoreTeamA'], payload['scoreTeamB']] + list(goals.values()):
        if type(value) is not int or not 0 <= value <= 99:
            raise PushError('invalid_submission', 'Scores and goals must be integers from 0 to 99.', 400)
    for team, score in (('teamA', 'scoreTeamA'), ('teamB', 'scoreTeamB')):
        if sum(goals[name] for name in payload[team]) > payload[score]:
            raise PushError('invalid_submission', 'Player goals cannot exceed the team score.', 400)
    return payload


def submit(payload, subject):
    payload = validate(payload)
    if os.getenv('GIT_BRANCH') not in ('dev', 'main') or os.getenv('WATCH_PUSH_ENABLED', '').lower() != 'true':
        raise PushError('push_disabled', 'Watch Push has not been enabled for this deployment.', 503)
    journal_path = os.getenv('WATCH_PUSH_JOURNAL', '')
    if not journal_path or not Path(journal_path).is_absolute():
        raise PushError('push_unavailable', 'The persistent submission journal is not configured.', 503)
    api = os.getenv('API_URL', '').rstrip('/')
    token = os.getenv('API_TOKEN', '')
    if not api or not token:
        raise PushError('push_unavailable', 'The private API is not configured.', 503)
    # Ignore submission ID when comparing an identical retry; one result per game.
    content = {k: v for k, v in payload.items() if k != 'submissionId'}
    digest = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    game_key = api + '/' + payload['date']
    Path(journal_path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(journal_path, timeout=5)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA synchronous=FULL')
        db.execute('''CREATE TABLE IF NOT EXISTS submissions (
            game TEXT PRIMARY KEY, submission_id TEXT UNIQUE NOT NULL,
            digest TEXT NOT NULL, subject TEXT NOT NULL, status TEXT NOT NULL,
            step TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        db.commit()
        db.execute('BEGIN IMMEDIATE')
        existing = db.execute('SELECT * FROM submissions WHERE game=? OR submission_id=?',
                              (game_key, payload['submissionId'])).fetchone()
        if existing:
            db.rollback()
            if existing['game'] != game_key or existing['digest'] != digest or existing['subject'] != subject:
                raise PushError('submission_conflict', 'A different submission already exists for this game.', 409)
            if existing['status'] == 'complete':
                return {'status': 'complete', 'date': payload['date'],
                        'submissionId': existing['submission_id'], 'replayed': True}
            raise PushError('submission_needs_review',
                            'This upload is in progress or needs review. Do not submit it again.', 409)
        # Hold the transaction while checking the source game, before any writes.
        headers = {'Authorization': 'Bearer ' + token}
        response = requests.get(api + '/games/most_recent_game', headers=headers,
                                timeout=10, allow_redirects=False)
        if response.status_code != 200:
            raise PushError('api_unavailable', 'Unable to read the game from the private API.', 503)
        games = response.json()
        if not isinstance(games, list) or any(not isinstance(g, dict) for g in games):
            raise PushError('api_unavailable', 'The private API returned invalid game data.', 503)
        game = next((g for g in games if g.get('date') == payload['date']), None)
        if not game:
            raise PushError('game_not_found', 'The game date was not found.', 404)
        if not {'teamA', 'teamB', 'scoreTeamA', 'scoreTeamB'}.issubset(game):
            raise PushError('api_unavailable', 'The private API returned incomplete game data.', 503)
        if game.get('teamA') != payload['teamA'] or game.get('teamB') != payload['teamB']:
            raise PushError('teams_changed', 'The teams have changed. Pull the game again.', 409)
        if game.get('scoreTeamA') is not None or game.get('scoreTeamB') is not None:
            raise PushError('score_exists', 'This game already has a saved result.', 409)
        db.execute('INSERT INTO submissions (game,submission_id,digest,subject,status,step) VALUES (?,?,?,?,?,?)',
                   (game_key, payload['submissionId'], digest, subject, 'pending', 'ready'))
        db.commit()

        def write(path, body, step):
            # Persist intent before sending: a crash or lost response stays blocked.
            db.execute('UPDATE submissions SET step=? WHERE game=?', (step + ':sending', game_key))
            db.commit()
            result = requests.put(api + path, headers=headers, json=body,
                                  timeout=15, allow_redirects=False)
            if result.status_code != 200:
                raise PushError('submission_needs_review',
                                'The API rejected part of this upload. Check the receipt before retrying.', 409)
            db.execute('UPDATE submissions SET step=? WHERE game=?', (step + ':confirmed', game_key))
            db.commit()

        try:
            write('/games/updatescore/' + payload['date'],
                  {k: payload[k] for k in ('scoreTeamA', 'scoreTeamB')}, 'score')
            for name, goals in payload['goals'].items():
                if goals:
                    write('/players/goals/' + quote(name, safe=''), {'goals': goals}, 'goals:' + name)
            db.execute("UPDATE submissions SET status='complete',step='complete' WHERE game=?", (game_key,))
            db.commit()
        except (requests.RequestException, PushError):
            db.execute("UPDATE submissions SET status='needs_review' WHERE game=?", (game_key,))
            db.commit()
            raise PushError('submission_needs_review',
                            'The upload may be partly saved. Review it before making further changes.', 409)
        return {'status': 'complete', 'date': payload['date'],
                'submissionId': payload['submissionId'], 'replayed': False}
    except (requests.RequestException, ValueError):
        db.rollback()
        raise PushError('api_unavailable', 'Unable to read the private API.', 503)
    finally:
        db.close()
