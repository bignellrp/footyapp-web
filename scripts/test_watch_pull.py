"""Manually authorize a device and pull game JSON; never write to the API.

Run: python scripts/test_watch_pull.py --env-file .env.watch.local
Access and refresh tokens stay in memory and are never printed or saved.
"""

import argparse
import json
import sys
import time
from urllib.parse import urlsplit

import requests
from dotenv import dotenv_values


def https_url(value):
    try:
        parsed = urlsplit(value)
        parsed.port
        valid = (parsed.scheme == 'https' and parsed.hostname
                 and not parsed.username and not parsed.password
                 and not parsed.fragment)
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise RuntimeError('All configured and discovered endpoints must use HTTPS.')
    return value


def request_json(session, method, url, **kwargs):
    response = session.request(method, https_url(url), timeout=15,
                               allow_redirects=False, **kwargs)
    if 300 <= response.status_code < 400:
        raise RuntimeError('Unexpected redirect. Check the NPM Watch route exception.')
    try:
        body = response.json()
    except ValueError:
        raise RuntimeError('Expected JSON. Check the Authentik/NPM configuration.') from None
    if not isinstance(body, dict):
        raise RuntimeError('Expected a JSON object.')
    return response, body


def require_success(response, body, operation):
    if not response.ok:
        # Never print entire error bodies: an upstream service might echo tokens.
        raise RuntimeError('{} failed (HTTP {}). Check the provider settings.'.format(
            operation, response.status_code))
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', required=True)
    args = parser.parse_args()
    settings = dotenv_values(args.env_file)
    issuer = settings.get('WATCH_OIDC_ISSUER', '')
    client_id = settings.get('WATCH_OIDC_CLIENT_ID', '')
    pull_url = settings.get('WATCH_PULL_URL', '')
    if not issuer or not client_id or not pull_url:
        raise RuntimeError('Set WATCH_OIDC_ISSUER, WATCH_OIDC_CLIENT_ID and WATCH_PULL_URL.')
    https_url(issuer)
    https_url(pull_url)

    with requests.Session() as session:
        response, discovery = request_json(
            session, 'GET', issuer.rstrip('/') + '/.well-known/openid-configuration')
        require_success(response, discovery, 'OIDC discovery')
        if discovery.get('issuer') != issuer:
            raise RuntimeError('WATCH_OIDC_ISSUER must exactly match discovery issuer.')
        token_url = discovery.get('token_endpoint')
        device_url = discovery.get('device_authorization_endpoint')
        if not device_url:
            # Authentik versions without this discovery field use this fixed path.
            origin = urlsplit(issuer)
            device_url = '{}://{}/application/o/device/'.format(origin.scheme, origin.netloc)
        https_url(token_url)
        https_url(device_url)
        response, device = request_json(session, 'POST', device_url, data={
            'client_id': client_id,
            'scope': 'openid offline_access footyapp:pull',
        })
        require_success(response, device, 'Device authorization')
        verification_uri = https_url(device.get('verification_uri'))
        device_code = device.get('device_code')
        user_code = device.get('user_code')
        if not device_code or not user_code:
            raise RuntimeError('Authentik did not return a device code and user code.')
        print('Open this address on your phone or computer: {}'.format(verification_uri))
        print('Enter this temporary code: {}'.format(user_code), flush=True)
        interval = max(5, int(device.get('interval', 5)))
        deadline = time.monotonic() + int(device.get('expires_in', 600))
        tokens = None
        while time.monotonic() + interval < deadline:
            time.sleep(interval)
            response, result = request_json(session, 'POST', token_url, data={
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                'client_id': client_id,
                'device_code': device_code,
            })
            if response.ok and result.get('access_token'):
                tokens = result
                break
            error = result.get('error')
            if response.status_code == 400 and error == 'authorization_pending':
                continue
            if response.status_code == 400 and error == 'slow_down':
                interval += 5
                continue
            if error == 'access_denied':
                raise RuntimeError('Device login was denied.')
            if error == 'expired_token':
                raise RuntimeError('Device login expired; run the script again.')
            raise RuntimeError('Token request failed (HTTP {}). Check the device grant and scopes.'.format(
                response.status_code))
        if tokens is None:
            raise RuntimeError('Device login expired; run the script again.')
        if tokens.get('token_type', '').lower() != 'bearer':
            raise RuntimeError('Authentik did not return a Bearer access token.')
        print('Login successful. Refresh token received: {}.'.format(
            'yes' if tokens.get('refresh_token') else 'no'))
        response, game = request_json(session, 'GET', pull_url, headers={
            'Authorization': 'Bearer {}'.format(tokens['access_token']),
        })
        require_success(response, game, 'Watch pull')
        required = {'date', 'teamA', 'teamB', 'colourTeamA', 'colourTeamB'}
        if not required.issubset(game):
            raise RuntimeError('Pull returned JSON but not the expected game fields.')
        print('Watch pull succeeded:')
        print(json.dumps({key: game[key] for key in sorted(required)}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled.', file=sys.stderr)
        sys.exit(1)
    except requests.RequestException:
        print('Connection failed. Check HTTPS certificates and endpoint availability.', file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, ValueError, TypeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
