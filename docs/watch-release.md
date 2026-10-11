# Dev Watch integration

## Configured in Authentik

The public provider settings and object IDs are recorded in
`watch-authentik-dev.json`. Application: **FootyApp Watch (dev)**, provider ID 3.
It uses RSA signing, a public client, device authorization and refresh grants,
10-minute access tokens and 7-day refresh tokens. The application is bound only
to user ID 6 (`akadmin`). The existing browser proxy provider remains in place.

Two custom scope mappings were created: `footyapp:pull` and `footyapp:push`.
The brand had no device code flow; its `flow_device_code` now references the new
dev Watch flow. This brand setting supplies the device-code screen for clients
using that hostname; it does not replace browser authentication.

## Deployment settings

Deploy the web `dev` revision. The dev GitHub deployment action automatically supplies these Portainer stack environment values
(used by the compose file) from `watch-authentik-dev.json` (manual deployments should supply them too):

- `WATCH_OIDC_ISSUER`
- `WATCH_OIDC_CLIENT_ID`
- `WATCH_OIDC_JWKS_URL`
- `WATCH_PUSH_ENABLED=true`

The compose file mounts `/mnt/docker/footyapp-web-dev/watch-data` and stores the
upload journal there. Preserve that folder across upgrades and backups. Push
also requires the existing `GIT_BRANCH=dev` setting. Missing configuration or an
unwritable journal fails closed. Do not mount this folder on multiple web hosts;
this journal supports one web deployment with local persistent storage.

## Nginx Proxy Manager

After the guarded routes are deployed, add these exact locations at server
level in the dev proxy host Advanced settings, beside the Authentik locations:

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

Keep the existing `location /` browser protection. Without a token both Watch
routes must return JSON `401`; `/score-json` must still require browser login.

## Push contract

Send `POST /watch/results` with an access token granting `footyapp:push`:

```json
{
  "submissionId": "25b69fc0-e401-4aec-aa96-c7ccb18fbd3e",
  "date": "2026-06-17",
  "teamA": ["Alice", "Anne"],
  "teamB": ["Bob", "Ben"],
  "scoreTeamA": 4,
  "scoreTeamB": 2,
  "goals": {"Alice": 2, "Anne": 2, "Bob": 1, "Ben": 1}
}
```

This is an illustrative fixture, not a request to update the June 17 game. The
actual date and teams must exactly match an existing unscored game. Scores and
goals are integers 0–99. Include every player's goals, including zeros. Goals
may sum to less than the team score (the scoreboard allows unattributed goals),
but never more. The Watch freezes the payload before sending and preserves it
and its UUID for a retry. A successful response has `status=complete` and the
game date. Identical retries return the receipt without repeating any writes;
a different submission for the same game is rejected.

The private API's score and goal updates are separate, non-transactional
operations. Before each request the web server durably records intent. A timeout,
process crash or partial failure leaves the game blocked for review. This
prevents automatic repeated increments, but does not make the existing API
atomic. The receipt records the last operation (`step`) and status; compare it
with the actual game/player totals before correcting anything. Never delete a
pending receipt and blindly retry. Do not enter a result on the web or through
another client while uploading that same game from the Watch. Stronger cross-
client concurrency protection would require an idempotent API submission route.

## Watch repo and testing

The current Xcode project was imported into `/Users/rikbignell/Web/footywatchapp`
on `dev`, replacing the old root ContentView. The baseline commit preserves the
imported source. Dev installs use `com.rikbignell.FootyWatch.dev` and display
**FootyWatch Dev**, allowing the existing app to remain installed.

Open `FootyWatch.xcodeproj`, scheme `FootyWatch`. Swipe to the menu and choose
**Sign In**. Open the displayed Authentik address on your phone, enter the code
and authorize the dev Watch. Pull fetches names, date and colours; it asks before
resetting a nonzero local score. Score via the team buttons or player buttons.
Push asks for confirmation before saving a final result. Successful uploads are
locked against further scoring/uploading for that date. Local match data and
unfinished submissions survive app restarts. Refresh tokens use Keychain with
`AfterFirstUnlockThisDeviceOnly`; access tokens remain in memory. Sign Out clears
local credentials and attempts refresh-token revocation. Already issued access
tokens expire naturally; offline sign-out may not reach the revocation endpoint.

Validation completed locally: web tests use a fake private API and temporary
SQLite storage, with generated RSA keys. No MongoDB data was changed. The Watch
build and simulator launch are checked separately. A real user device login and
live Push require the proxy and deployment settings above; choose an unscored
dev game when testing writes.

The temporary Authentik admin token is only used by the provisioning script. It
is excluded from Git, Docker images and the Watch. Revoke it after setup.
