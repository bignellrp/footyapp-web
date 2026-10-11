# Production Watch release

Production: https://footyapp.richardbignell.co.uk

## Release safety

The production Watch OAuth application is separate from dev; public configuration
is in `watch-authentik-prod.json`. Only your Authentik account (user ID 6) is
bound to the application. Access tokens last 10 minutes and refresh tokens 7 days.
Production web deployments load this provider automatically on `main`.
Dev continues to use the dev provider on `dev`.

The production submission journal is persisted in
`/mnt/docker/footyapp-web-main/watch-data/submissions.sqlite3`, separately from dev.
Keep this directory in backups and across deployments. The same validation,
locked receipts and uncertain-upload protections used in dev apply in production.
Only `main` and `dev` with `WATCH_PUSH_ENABLED=true` may submit a result.

API startup no longer inserts sample rows or creates indexes. This release needs
no MongoDB migration. Do not initialize or reset the live database.

## Nginx setup (your remaining server step)

In **the production proxy host** Advanced tab, add these blocks at server level,
outside existing location blocks, beside the existing Authentik configuration:

```nginx
location = /watch/score-json {
    auth_request off;
    proxy_intercept_errors off;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Authorization $http_authorization;
    proxy_pass $forward_scheme://$server:$port;
}
location = /watch/results {
    auth_request off;
    proxy_intercept_errors off;
    client_max_body_size 16k;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Authorization $http_authorization;
    proxy_pass $forward_scheme://$server:$port;
}
```

Save. Opening `/watch/score-json` without a token should return JSON
`authentication_required` (HTTP 401). The normal website and `/score-json` should
still require Authentik browser login. Only these exact Watch paths bypass browser
redirects; Flask independently validates their access tokens and scopes.

## Install the production app

Open `/Users/rikbignell/Web/footywatchapp/FootyWatch.xcodeproj` in Xcode.
Choose **FootyWatch Prod**, choose your paired Watch, then Run.
This uses Release, the green icon, production URL and production client ID.
The bundle ID is `com.rikbignell.FootyWatch`. If the old app has the same ID,
installation replaces it; otherwise delete the old app from the Watch app grid
(touch and hold, Edit Apps, delete) once the new app is installed.
The blue **FootyWatch Dev** is separate and may also be deleted if no longer needed.
Deleting a Watch app only removes its local app data, not server game records.

Production and dev have separate stored matches and Keychain accounts.
Sign in again in the green app and authorize the production Watch in Authentik.
**Pull only before the live game.** It should load `2026-10-14`:

- Team A (white): Martin, Sam, MarkE, Rik, Phil
- Team B (black): Chris, Pete, Liam, Simon, BradE

Do not submit a test result. Use Push after Wednesday's actual game. A successful
Push locks this date against another submission. If an upload reports that it
needs review, stop and reconcile the journal against the server before retrying.
Do not enter the same result on the web while uploading from the Watch.

## Rollback

The previous web image was
`ghcr.io/bignellrp/footyapp-web:f7627adb0f735ee03e2128e1e910a6c602bb6058`.
Set the production web stack `IMAGE_TAG` back to that SHA and redeploy if necessary.
Retain the journal volume. Remove the two Nginx Watch exceptions when rolling back
to a web build without token validation. Existing browser login stays protected.
Disabling `WATCH_PUSH_ENABLED` blocks new submissions while retaining Pull.
Reverting application code cannot undo scores/goals already accepted by the API.
