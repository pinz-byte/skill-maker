---
name: gcp-iam-resolver
description: >
  Resolves GCP IAM permission errors in one pass instead of guessing roles by trial and
  error. The Subastop/Herald stack is GCP-heavy (Cloud Run, Secret Manager, Firestore,
  scheduler), and permission tasks have repeatedly burned multiple round-trips guessing
  role names that do not exist or are too narrow (e.g. trying secretCreator, then
  secretVersionAdder, before landing on the role that actually grants the permission).
  Use this skill whenever you hit "PERMISSION_DENIED", a 403 on a GCP call, "what role do
  I need", "add iam binding", "secretmanager permission", "service account can't", "grant
  access to", "role ... is not supported for this resource", or any gcloud IAM task. Also
  trigger before suggesting any add-iam-policy-binding so the role string is validated
  first. Fire on "gcp says denied", "permission denied on resource", or "which role grants
  X". Default project context: subastop-herald and related Subastop GCP projects.
---

# GCP IAM Resolver

Permission errors get solved by mapping the missing PERMISSION to the correct ROLE in one
step, then validating the role exists before running the binding. The failure pattern this
replaces: reading "PERMISSION_DENIED", guessing a plausible role name, running the binding,
getting "role is not supported for this resource", guessing again. Each guess is a wasted
round-trip with the user copy-pasting between terminal and chat.

## The Method

### Step 1 — Extract the exact permission from the error

GCP errors name the permission, not the role. Pull it verbatim:

```
PERMISSION_DENIED: Permission 'secretmanager.secrets.create' denied on resource ...
```

The permission is `secretmanager.secrets.create`. That string is your key. Do not start
from a role name.

### Step 2 — Map permission to the minimal role that contains it

Known mappings for this stack (verify with Step 3 before applying):

| Permission needed | Correct role | Common wrong guess |
|---|---|---|
| `secretmanager.secrets.create` | `roles/secretmanager.admin` | `secretCreator` (does not exist), `secretVersionAdder` (only adds versions to existing secrets) |
| `secretmanager.versions.add` | `roles/secretmanager.secretVersionAdder` | `secretmanager.admin` (too broad) |
| `secretmanager.versions.access` | `roles/secretmanager.secretAccessor` | `admin` (too broad) |
| `run.services.invoke` | `roles/run.invoker` | `run.developer` (too broad) |
| `run.services.update` / deploy | `roles/run.developer` | `run.admin` (too broad) |
| `datastore.entities.*` (Firestore RW) | `roles/datastore.user` | `datastore.owner` |
| `cloudscheduler.jobs.*` | `roles/cloudscheduler.admin` | — |
| `iam.serviceAccounts.actAs` | `roles/iam.serviceAccountUser` | `serviceAccountAdmin` |

Rule of thumb: `.create` on a resource container usually lives only in that service's
`admin` role; version/access verbs have their own narrow roles. Prefer the narrowest role
that contains the permission, but do not invent a narrow role that does not exist.

### Step 3 — Validate the role string EXISTS before binding

Never run a binding with an unverified role. Check first:

```bash
gcloud iam roles describe roles/secretmanager.admin 2>&1 | head -3
# or list what matches:
gcloud iam roles list --filter="name:secretmanager" --format="value(name)"
```

If `describe` errors, the role name is wrong — do not run the binding.

### Step 4 — Apply, then re-run the original call

```bash
gcloud projects add-iam-policy-binding subastop-herald \
  --member="serviceAccount:herald-runtime-sa@subastop-herald.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"
```

Then immediately re-run the call that failed to confirm the permission is now satisfied.

## Narrow-vs-Broad Decision

When `.create` forces `admin` (broad) and the user wants tighter scope, the alternative is
to pre-create the resource container during deploy so the runtime SA only needs the narrow
version/accessor role. State this trade-off in one line and let the user choose — do not
silently grant `admin` if a tighter path is cheap, and do not block on security theater for
an internal, project-scoped service account.

## Principles

- **Start from the permission, never from a role name.** The error hands you the permission;
  the guessing loop starts the moment you reach for a role you half-remember.
- **Validate before binding.** One `roles describe` call costs less than a failed binding
  round-trip through the user's terminal.
- **Minimal role that actually exists.** Narrowest containing role — but a real one. Most of
  the wasted loops came from inventing plausible-but-nonexistent narrow roles.
- A 403 is not always IAM — pair with [[herald-config-doctor]] when the 403 is really a
  stale/decommissioned URL, and [[machine-bridge]] because the binding must run on the
  machine with the user's gcloud auth, not the sandbox.

## Edge Cases

- **"role is not supported for this resource":** the role exists but at a different level
  (e.g. it is an org role, not a project role). Re-check with `gcloud iam roles list`.
- **Binding succeeds but call still 403s:** propagation delay (wait ~60s) or the call uses a
  different SA than the one you bound. Confirm which identity the failing call runs as.
- **Conditional bindings:** if the policy has IAM conditions, an unconditional binding can be
  rejected — surface the condition rather than forcing it.
