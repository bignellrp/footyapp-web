"""Offline tests: no live API, Authentik or MongoDB connections."""
import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

import jwt
import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask

from services import watch_auth, watch_push


def load_route():
    # Avoid routes/__init__.py, which imports unrelated legacy modules.
    spec = importlib.util.spec_from_file_location('watch_route_test', 'routes/watch.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TokenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def setUp(self):
        self.env = patch.dict(os.environ, {
            'WATCH_OIDC_ISSUER': 'https://auth.example/application/o/watch/',
            'WATCH_OIDC_CLIENT_ID': 'watch-client',
            'WATCH_OIDC_JWKS_URL': 'https://auth.example/application/o/watch/jwks/',
        }, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.keys = patch.object(watch_auth, '_jwks_client')
        self.mock_keys = self.keys.start()
        self.addCleanup(self.keys.stop)
        self.mock_keys.return_value.get_signing_key_from_jwt.return_value = SimpleNamespace(key=self.key.public_key())
        self.app = Flask(__name__)

        @self.app.route('/pull')
        @watch_auth.watch_token_required('footyapp:pull')
        def pull():
            return {'date': '2026-06-17'}

        self.app.register_blueprint(load_route().watch_blueprint)
        self.client = self.app.test_client()

    def token(self, changes=None, omit=None, key=None):
        now = int(time.time())
        claims = {'iss': os.environ['WATCH_OIDC_ISSUER'], 'aud': 'watch-client',
                  'sub': 'user-6', 'iat': now, 'exp': now + 600,
                  'azp': 'watch-client', 'uid': 'access-token-id', 'scope': 'footyapp:pull footyapp:push'}
        claims.update(changes or {})
        if omit:
            claims.pop(omit)
        return jwt.encode(claims, key or self.key, algorithm='RS256', headers={'kid': 'known-key'})

    def pull(self, token):
        return self.client.get('/pull', headers={'Authorization': 'Bearer ' + token})

    def test_valid_token_and_no_cache(self):
        response = self.pull(self.token())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'date': '2026-06-17'})
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.mock_keys.assert_called_with(os.environ['WATCH_OIDC_JWKS_URL'])

    def test_no_cookie_or_proxy_header_bypass(self):
        response = self.client.get('/pull', headers={'X-authentik-username': 'akadmin', 'Cookie': 'session=anything'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Bearer', response.headers['WWW-Authenticate'])

    def test_bad_claims(self):
        for changes in ({'exp': int(time.time()) - 90}, {'iss': 'https://other.example/'},
                        {'aud': 'another-client'}, {'azp': 'another-client'}, {'sub': ''},
                        {'scope': 2}, {'iat': int(time.time()) + 90}):
            with self.subTest(changes=changes):
                self.assertEqual(self.pull(self.token(changes)).status_code, 401)
        for omitted in ('exp', 'scope', 'uid', 'azp'):
            self.assertEqual(self.pull(self.token(omit=omitted)).status_code, 401)

    def test_wrong_signature(self):
        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.assertEqual(self.pull(self.token(key=other)).status_code, 401)

    def test_wrong_algorithm_and_malformed_bearer(self):
        token = jwt.encode({'sub': 'user'}, 'shared-secret', algorithm='HS256', headers={'kid': 'known-key'})
        self.assertEqual(self.pull(token).status_code, 401)
        for header in ('Basic abc', 'Bearer a b', 'Bearer ' + 'x' * 17000):
            self.assertEqual(self.client.get('/pull', headers={'Authorization': header}).status_code, 401)

    def test_scope_is_required(self):
        self.assertEqual(self.pull(self.token({'scope': 'openid'})).status_code, 403)

    def test_bad_config_and_jwks_failure_fail_closed(self):
        for url in ('', 'http://auth.example/', 'https://[broken'):
            with patch.dict(os.environ, {'WATCH_OIDC_ISSUER': url}):
                self.assertEqual(self.pull(self.token()).status_code, 503)
        self.mock_keys.return_value.get_signing_key_from_jwt.side_effect = jwt.PyJWKClientConnectionError('offline')
        self.assertEqual(self.pull(self.token()).status_code, 503)

    def test_pull_scope_cannot_push(self):
        with patch('services.watch_push.requests.put') as writes:
            response = self.client.post('/watch/results', json={}, headers={
                'Authorization': 'Bearer ' + self.token({'scope': 'footyapp:pull'})})
            self.assertEqual(response.status_code, 403)
            writes.assert_not_called()


class PushTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = patch.dict(os.environ, {
            'GIT_BRANCH': 'dev', 'WATCH_PUSH_ENABLED': 'true',
            'WATCH_PUSH_JOURNAL': str(Path(self.temp.name) / 'journal.sqlite3'),
            'API_URL': 'http://private-api.invalid', 'API_TOKEN': 'fake-test-token',
        }, clear=True)
        self.env.start(); self.addCleanup(self.env.stop)
        self.body = {'submissionId': str(uuid4()), 'date': '2026-06-17',
                     'teamA': ['Alice', 'Anne'], 'teamB': ['Bob', 'Ben'],
                     'scoreTeamA': 4, 'scoreTeamB': 2,
                     'goals': {'Alice': 2, 'Anne': 2, 'Bob': 1, 'Ben': 1}}
        self.game = {k: self.body[k] for k in ('date', 'teamA', 'teamB')}
        self.game.update(scoreTeamA=None, scoreTeamB=None)
        self.get = patch.object(watch_push.requests, 'get')
        self.put = patch.object(watch_push.requests, 'put')
        self.read = self.get.start(); self.addCleanup(self.get.stop)
        self.write = self.put.start(); self.addCleanup(self.put.stop)
        self.read.return_value = Mock(status_code=200, json=lambda: [self.game])
        self.write.return_value = Mock(status_code=200)

    def assert_error(self, code, payload=None):
        with self.assertRaises(watch_push.PushError) as raised:
            watch_push.submit(self.body if payload is None else payload, 'user')
        self.assertEqual(raised.exception.code, code)

    def test_submission_and_duplicate_receipt(self):
        result = watch_push.submit(self.body, 'user')
        self.assertFalse(result['replayed'])
        self.assertEqual(self.write.call_count, 5)
        result = watch_push.submit(self.body, 'user')
        self.assertTrue(result['replayed'])
        self.assertEqual(self.write.call_count, 5)
        self.body['submissionId'] = str(uuid4())
        self.assertTrue(watch_push.submit(self.body, 'user')['replayed'])
        self.assertEqual(self.write.call_count, 5)

    def test_different_payload_cannot_add_goals_again(self):
        watch_push.submit(self.body, 'user')
        self.body['goals']['Alice'] = 1
        self.assert_error('submission_conflict')
        self.assertEqual(self.write.call_count, 5)

    def test_uncertain_score_is_never_resent(self):
        self.write.side_effect = requests.Timeout()
        self.assert_error('submission_needs_review')
        self.assert_error('submission_needs_review')
        self.assertEqual(self.write.call_count, 1)

    def test_partial_goal_failure_blocks_retry(self):
        self.write.side_effect = [Mock(status_code=200), Mock(status_code=200), requests.Timeout()]
        self.assert_error('submission_needs_review')
        self.assert_error('submission_needs_review')
        self.assertEqual(self.write.call_count, 3)

    def test_existing_score_and_changed_roster_rejected(self):
        self.game['scoreTeamA'] = 1
        self.assert_error('score_exists')
        self.game['scoreTeamA'] = None
        self.game['teamA'] = ['New Player']
        self.assert_error('teams_changed')
        self.write.assert_not_called()

    def test_validation_and_dev_only_switch(self):
        self.body['goals']['Alice'] = True
        self.assert_error('invalid_submission')
        self.body['goals']['Alice'] = 2
        with patch.dict(os.environ, {'GIT_BRANCH': 'main'}):
            self.assert_error('push_disabled')
        self.read.assert_not_called(); self.write.assert_not_called()


if __name__ == '__main__':
    unittest.main()
