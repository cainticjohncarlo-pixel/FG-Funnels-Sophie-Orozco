---
name: feedback-env-secrets-local-only
description: "Keep .env and all credentials local to the user's device — never echo secrets into chat, commits, or any outbound surface"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1279e05d-8c7e-47a7-a8c3-aeaa149efea7
  modified: 2026-07-20T16:10:55.419Z
---

Secrets belong in `.env` on the user's machine and must stay there. Never print
`.env` contents, API keys, or tokens into chat messages, commit messages,
artifacts, or any other surface that leaves the device. Read credentials via
environment variables or by piping from the file inside a shell command — never
into a visible message.

If the user offers to paste a key into the chat, redirect them to the file
instead. If they paste one anyway, write it where they asked, then recommend
revoking and reissuing once — the transcript leaves the device even when the
device itself is secure.

**Why:** The `.env` file is protected by the device being the user's own. A chat
transcript is not — it is stored server-side, retained, and reachable by anyone
with account access. Device security protects the file and does nothing for the
transcript, so "only I use this machine" does not make pasting safe.

**How to apply:** Verify `.env` is gitignored before writing to it. Pass keys via
`$ENV_VAR` or `grep ... | cut` inside a single Bash call so the value never
appears in tool output. When verifying a credential works, print only the HTTP
status, never the key. See [[project-autonomous-stack-instantly]].
