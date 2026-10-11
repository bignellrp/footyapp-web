"""Provision separate dev or production Watch OAuth objects; read token from .env."""
import argparse
import json
import secrets
from pathlib import Path

import requests
from dotenv import dotenv_values, set_key

BASE = 'https://authentik.richardbignell.co.uk'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--environment', choices=('dev', 'prod'), default='dev')
    environment = parser.parse_args().environment
    slug = 'footyapp-watch-' + environment
    label = 'dev' if environment == 'dev' else 'production'
    settings = dotenv_values('.env')
    session = requests.Session()
    session.headers['Authorization'] = 'Bearer ' + settings['AUTHENTIK_TOKEN']

    def call(method, path, payload=None):
        response = session.request(method, BASE + '/api/v3/' + path,
                                   json=payload, timeout=20, allow_redirects=False)
        if not response.ok:
            raise RuntimeError('{} {} failed: HTTP {}'.format(method, path, response.status_code))
        return response.json() if response.content else {}

    def rows(path):
        result = call('GET', path + '?page_size=100')
        if result.get('pagination', {}).get('next'):
            raise RuntimeError('Unexpected pagination; inspect before provisioning.')
        return result.get('results', [])

    owner = call('GET', 'core/users/me/')['user']['pk']
    flows = {row['slug']: row for row in rows('flows/instances/')}
    device = flows.get(slug + '-device')
    if not device:
        device = call('POST', 'flows/instances/', {
            'name': 'FootyApp ' + label + ' Watch device login', 'slug': slug + '-device',
            'title': 'Authorize your FootyApp Watch',
            'designation': 'stage_configuration', 'authentication': 'require_authenticated',
        })
    mappings = rows('propertymappings/provider/scope/')
    mapping_ids = []
    for scope in ('footyapp:pull', 'footyapp:push'):
        name = 'FootyApp ' + label + ' Watch ' + scope.split(':')[1]
        mapping = next((m for m in mappings if m['name'] == name), None)
        if not mapping:
            mapping = call('POST', 'propertymappings/provider/scope/', {
                'name': name, 'scope_name': scope, 'expression': 'return {}',
                'description': 'Permission for the ' + label + ' FootyApp Watch ' + scope.split(':')[1],
            })
        mapping_ids.append(mapping['pk'])
    for scope in ('openid', 'offline_access'):
        mapping_ids.append(next(m['pk'] for m in mappings if m['scope_name'] == scope))
    providers = rows('providers/oauth2/')
    provider = next((p for p in providers if p['name'] == 'FootyApp ' + label + ' Watch'), None)
    if not provider:
        key = next(k for k in rows('crypto/certificatekeypairs/')
                   if k['name'] == 'authentik Self-signed Certificate')
        provider = call('POST', 'providers/oauth2/', {
            'name': 'FootyApp ' + label + ' Watch', 'client_type': 'public',
            'client_id': secrets.token_urlsafe(24), 'redirect_uris': [],
            'authorization_flow': flows['default-provider-authorization-explicit-consent']['pk'],
            'invalidation_flow': flows['default-provider-invalidation-flow']['pk'],
            'authentication_flow': flows['default-authentication-flow']['pk'],
            'grant_types': ['urn:ietf:params:oauth:grant-type:device_code', 'refresh_token'],
            'property_mappings': mapping_ids, 'signing_key': key['pk'],
            'issuer_mode': 'per_provider', 'access_token_validity': 'minutes=10',
            'refresh_token_validity': 'days=7', 'include_claims_in_id_token': False,
        })
    applications = rows('core/applications/')
    application = next((a for a in applications if a['slug'] == slug), None)
    if not application:
        application = call('POST', 'core/applications/', {
            'name': 'FootyApp Watch (' + label + ')', 'slug': slug, 'provider': provider['pk'],
            'meta_description': label + ' Watch Pull and Push', 'policy_engine_mode': 'all',
        })
    bindings = rows('policies/bindings/')
    if not any(b['target'] == application['pk'] and b.get('user') == owner for b in bindings):
        call('POST', 'policies/bindings/', {
            'target': application['pk'], 'user': owner, 'order': 0,
            'enabled': True, 'failure_result': False,
        })
    brand = next(b for b in rows('core/brands/')
                 if b['domain'] == 'authentik.richardbignell.co.uk')
    previous_device_flow = brand.get('flow_device_code')
    if not previous_device_flow:
        call('PATCH', 'core/brands/{}/'.format(brand['brand_uuid']),
             {'flow_device_code': device['pk']})
    issuer = BASE + '/application/o/' + slug + '/'
    # Use an unauthenticated session so the admin token never reaches discovery.
    discovery_response = requests.get(issuer + '.well-known/openid-configuration', timeout=15)
    discovery_response.raise_for_status()
    discovery = discovery_response.json()
    jwks_response = requests.get(discovery['jwks_uri'], timeout=15)
    jwks_response.raise_for_status()
    if not any(k.get('kty') == 'RSA' for k in jwks_response.json().get('keys', [])):
        raise RuntimeError('Provider has no RSA signing key; refuse to configure web.')
    public = {
        'WATCH_OIDC_ISSUER': discovery['issuer'],
        'WATCH_OIDC_CLIENT_ID': provider['client_id'],
        'WATCH_OIDC_JWKS_URL': discovery['jwks_uri'],
        'WATCH_PULL_URL': ('https://footyappdev.richardbignell.co.uk' if environment == 'dev' else 'https://footyapp.richardbignell.co.uk') + '/watch/score-json',
    }
    if environment == 'dev':
        for name, value in public.items():
            set_key('.env', name, value)
    snapshot = dict(public, provider_id=provider['pk'], application_id=application['pk'],
                    allowed_user_id=owner, device_flow_id=device['pk'],
                    previous_brand_device_flow=previous_device_flow)
    Path('docs/watch-authentik-' + environment + '.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    print('Configured ' + label + ' Watch application. Public configuration:')
    print(json.dumps(snapshot, indent=2))


if __name__ == '__main__':
    main()
