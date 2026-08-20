---
name: gcloud-auth-doctor
description: >-
  Fixes recurring gcloud "Reauthentication required" loops in one pass: triages WHICH
  credential died (CLI cred vs ADC vs impersonation chain), applies the one-command fast
  path, and drives the durable fixes -- session-control policy tuning in the Subastop
  Workspace admin console and SA impersonation for builder/automation surfaces. Use
  whenever gcloud, gsutil, firebase, or terraform demands a re-login: "Reauthentication
  required", "reauthenticate", "gcloud asking me to log in again", "auth expired",
  "invalid_grant", "token expired or revoked", "could not find default credentials",
  "gcloud login loop", "ADC expired", or a builder session stalling on an
  auth prompt mid-build. Also trigger BEFORE any long build or deploy that depends on
  gcloud auth -- the pre-flight belongs at session start, not at failure time.
  Context: the subastop.com Workspace org is self-administered, so the session policy is
  editable. NOT gcp-iam-resolver (maps PERMISSION_DENIED to a role): this fixes expired
  or looping credentials.
metadata:
  intent: diagnose
---

# gcloud Auth Doctor

Re-auth loops get solved by identifying WHICH of three credentials died, fixing it with one
command, then removing the cause so it stops recurring. The failure pattern this replaces:
gcloud asks for re-login, the user runs `gcloud auth login`, the CLI works again, then an
hour later a builder session dies on ADC (a different credential the login never touched),
and next week the whole loop repeats because nobody changed the policy that expires the
session in the first place.

## The Three Credentials

Every machine has up to three independent credentials. "I re-authenticated" is meaningless
until you know which one you refreshed:

| Credential | Used by | Lives at | Check (no browser) |
|---|---|---|---|
| gcloud CLI cred | `gcloud`, `gsutil`, `bq` | `~/.config/gcloud/` | `gcloud auth print-access-token >/dev/null` |
| ADC | client libraries, terraform, firebase-admin, builders | `~/.config/gcloud/application_default_credentials.json` | `gcloud auth application-default print-access-token >/dev/null` |
| Impersonation chain | anything configured to act as a SA | config + the user cred underneath | same checks -- it dies when the user cred dies |

## Step 1 -- Triage: which credential died

```bash
gcloud auth list
gcloud auth print-access-token >/dev/null 2>&1 && echo "CLI OK" || echo "CLI DEAD"
gcloud auth application-default print-access-token >/dev/null 2>&1 && echo "ADC OK" || echo "ADC DEAD"
```

Symptom map: `Reauthentication required` = session-control policy expired the user token
(Step 3 is the real fix). `invalid_grant` / `token has been expired or revoked` = refresh
token dead (password change, revocation, or expiry) -- re-login required. `Could not find
default credentials` = ADC never existed on this machine/session -- setup, not re-auth.

## Step 2 -- Fast path: fix both in ONE browser roundtrip

```bash
gcloud auth login --update-adc
```

`--update-adc` writes the new credential to the ADC well-known location too. Never run
`gcloud auth login` and `gcloud auth application-default login` as two separate browser
trips -- that is the half-fix that leaves builders dying on stale ADC an hour later.
Headless machine: add `--no-browser` and complete the flow from a machine that has one.

## Step 3 -- Root cause: the session-control policy (you own it)

`Reauthentication required` on a schedule is not gcloud misbehaving -- it is the **Google
Cloud session control** policy expiring the session. The subastop.com Workspace org is
self-administered, so the policy is yours to set:

**Admin console -> Security -> Access and data control -> Google Cloud session control**

- Reauth frequency range is 1-24 hours. If a short session is set, move it to 24 hours --
  or remove the policy if forced expiry is not wanted at all.
- Set reauth method to **Password**, not Security key -- key-based reauth is the known
  cause of every-command reauth loops in gsutil.
- The **Exempt trusted apps** checkbox releases designated apps from session length
  constraints while keeping controls on everything else.

One policy edit here removes more re-auth prompts than any amount of client-side tooling.

## Step 4 -- Builders and automation: impersonation + pre-flight

Automation surfaces (Claude Code / Codex builders, deploy scripts) should act as a service
account, not as the human -- stable identity, no key files on disk:

```bash
gcloud config set auth/impersonate_service_account deploy-sa@PROJECT.iam.gserviceaccount.com
gcloud auth application-default login --impersonate-service-account=deploy-sa@PROJECT.iam.gserviceaccount.com
```

The SA needs `roles/iam.serviceAccountTokenCreator` granted TO your user ON the SA --
validate with [[gcp-iam-resolver]] before binding.

**Honest limit:** impersonation mints SA tokens THROUGH your user credential. If session
control expires the user cred, impersonated calls die with it. Impersonation buys stable
identity and keylessness -- Step 3 is what buys duration. Do both.

**Builder pre-flight (mandatory at session start, before any long build):**

```bash
gcloud auth print-access-token >/dev/null 2>&1 || { echo "AUTH DEAD -- run on the machine: gcloud auth login --update-adc"; exit 1; }
```

Fail at minute zero with the exact fix command, not at minute forty mid-deploy. The
re-login itself must run on the machine with a browser and the user's keychain -- never
inside the sandbox ([[machine-bridge]]).

## Principles

- **Name the dead credential before touching anything.** Most wasted loops come from
  refreshing the credential that was still alive.
- **One browser roundtrip, both credentials.** `--update-adc` always.
- **Fix the policy, not just the token.** A re-login without the Step 3 policy check is
  scheduled to fail again tomorrow.
- **Automation never rides the human credential bare.** Impersonation for identity,
  pre-flight for early failure.

## Edge Cases

- **Reauth demanded on nearly every command:** reauth method is Security key -- switch the
  policy to Password (Step 3), or the session length is set to the 1h minimum.
- **`invalid_grant` right after a password change:** expected -- password changes revoke
  refresh tokens. Straight to Step 2.
- **Fixed the CLI but terraform/firebase still fails:** you refreshed the CLI cred only;
  ADC is separate. Step 2 exists for this.
- **Sensitive actions (billing, IAM) prompt despite a live session:** console-side 15-minute
  reauth for privileged users -- by design, not a broken credential. Do not chase it.
- **ADC works locally but a builder sees nothing:** builder runs as a different OS user or
  in a sandbox without `~/.config/gcloud` -- run the pre-flight there, not on your shell.
