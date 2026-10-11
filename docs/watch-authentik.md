# Watch token authentication

The dev provider is now configured and both Pull and Push are implemented.
See [the release and testing guide](watch-release.md) for the deployed settings,
Nginx routes, upload contract and known recovery limitations.

## Validation

`GET /watch/score-json` accepts an Authentik access token with `footyapp:pull`.
`POST /watch/results` requires `footyapp:push` and a valid game submission.
The existing `/score-json` remains a browser page protected by NPM/Authentik.

Flask verifies RS256 signature, exact issuer, client audience, expiry, issue time,
subject, granted scopes and Authentik's access-token-only `uid` and `azp` claims.
It ignores browser cookies and proxy identity headers. ID tokens are not valid
API credentials. Public signing keys are cached for five minutes and refreshed
on a new key ID. Invalid/missing tokens return JSON 401, insufficient scope 403,
and unavailable configuration/signing keys 503. Access tokens remain valid until
expiry (with 30 seconds clock tolerance) even after refresh-token revocation.

## Manual login-and-pull check

Copy `.env.watch.example` to `.env.watch.local` and run:

```sh
python scripts/test_watch_pull.py --env-file .env.watch.local
```

Open the displayed address, sign in and approve the temporary code. The script
uses the resulting access token to read the dev game. Tokens stay in memory and
are not printed or saved. This script does not push or change database data.

## References

- [Authentik OAuth provider settings](https://docs.goauthentik.io/add-secure-apps/providers/oauth2/)
- [Refresh token setup](https://docs.goauthentik.io/add-secure-apps/providers/oauth2/create-oauth2-provider/)
- [Device code flow](https://docs.goauthentik.io/add-secure-apps/providers/oauth2/device_code/)
- [Authentik 2026.8.1 access-token claims](https://github.com/goauthentik/authentik/blob/version/2026.8.1/authentik/providers/oauth2/id_token.py)
