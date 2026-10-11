"""Validate Authentik OAuth access tokens for the Watch's JSON endpoints."""

import os
from functools import lru_cache, wraps
from urllib.parse import urlsplit

import jwt
from flask import current_app, g, jsonify, make_response, request


def _https_url(value):
    try:
        parsed = urlsplit(value)
        parsed.port  # Reject malformed ports as well as malformed hostnames.
        return (
            parsed.scheme == 'https' and bool(parsed.hostname)
            and not parsed.username and not parsed.password
            and not parsed.query and not parsed.fragment
        )
    except ValueError:
        return False


@lru_cache(maxsize=8)
def _jwks_client(url):
    # Cache public signing keys for five minutes; refresh for a new key ID.
    return jwt.PyJWKClient(url, lifespan=300, timeout=5)


def _error(code, message, status, scope=None):
    response = jsonify({'error': code, 'message': message})
    response.status_code = status
    response.headers['Cache-Control'] = 'no-store'
    if status in (401, 403):
        challenge = 'Bearer realm="footyapp-watch"'
        if code in ('invalid_token', 'insufficient_scope'):
            challenge += ', error="{}"'.format(code)
        if scope:
            challenge += ', scope="{}"'.format(scope)
        response.headers['WWW-Authenticate'] = challenge
    return response


def watch_token_required(required_scope):
    """Require a signed access token with the specified Watch permission.

    Only RS256 keys from the configured Authentik JWKS endpoint are trusted.
    Neither upstream identity headers nor a website cookie authorize this route.
    """
    def decorate(view):
        @wraps(view)
        def authenticated(*args, **kwargs):
            authorization = request.headers.get('Authorization', '')
            if not authorization:
                return _error('authentication_required', 'A Watch access token is required.', 401)
            parts = authorization.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer' or len(parts[1]) > 16384:
                return _error('invalid_token', 'The access token is invalid or expired.', 401)
            token = parts[1]

            issuer = os.getenv('WATCH_OIDC_ISSUER', '').strip()
            client_id = os.getenv('WATCH_OIDC_CLIENT_ID', '').strip()
            jwks_url = os.getenv('WATCH_OIDC_JWKS_URL', '').strip()
            if not jwks_url and issuer:
                jwks_url = issuer.rstrip('/') + '/jwks/'
            if not client_id or not _https_url(issuer) or not _https_url(jwks_url):
                current_app.logger.warning('Watch OAuth configuration is missing or invalid')
                return _error('authentication_unavailable', 'Watch authentication is not configured.', 503)

            try:
                header = jwt.get_unverified_header(token)
                if header.get('alg') != 'RS256' or not isinstance(header.get('kid'), str) or not header['kid']:
                    raise jwt.InvalidTokenError('Unsupported token header')
                # Never use a key URL or algorithm supplied by the token itself.
                signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
                claims = jwt.decode(
                    token, signing_key.key, algorithms=['RS256'],
                    issuer=issuer, audience=client_id, leeway=30,
                    options={'require': ['exp', 'iat', 'iss', 'aud', 'sub', 'scope', 'uid', 'azp']},
                )
                # Authentik adds uid and azp to access tokens, not ID tokens.
                if claims['azp'] != client_id or not isinstance(claims['uid'], str) or not claims['uid']:
                    raise jwt.InvalidTokenError('Invalid access token')
                if not isinstance(claims['sub'], str) or not claims['sub'].strip():
                    raise jwt.InvalidTokenError('Invalid subject')
                scopes = claims['scope']
                if isinstance(scopes, str):
                    scopes = scopes.split()
                elif not isinstance(scopes, list) or not all(isinstance(s, str) for s in scopes):
                    raise jwt.InvalidTokenError('Invalid scope claim')
            except (jwt.PyJWKClientConnectionError, jwt.PyJWKSetError, ValueError):
                current_app.logger.warning('Authentik signing keys are unavailable')
                return _error('authentication_unavailable', 'Watch authentication is temporarily unavailable.', 503)
            except (jwt.InvalidTokenError, jwt.PyJWKClientError, jwt.PyJWKError):
                return _error('invalid_token', 'The access token is invalid or expired.', 401)

            if required_scope not in scopes:
                return _error('insufficient_scope', 'This token does not permit this operation.', 403, required_scope)
            g.watch_claims = claims
            response = make_response(view(*args, **kwargs))
            response.headers['Cache-Control'] = 'no-store'
            return response
        return authenticated
    return decorate
