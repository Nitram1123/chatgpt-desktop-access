# Release versioning policy

ChatGPT Desktop Access versions follow the current stable NVDA release.

- The base add-on release uses the NVDA stable version plus a zero patch, currently `2026.3.0`.
- Add-on-only patches append a third component: `2026.2.1`, `2026.2.2`, `2026.2.3`, `2026.2.4`, `2026.2.5`, `2026.2.6`, `2026.2.7`, `2026.2.8`, and so on.
- Patch numbering increases for every published add-on update while NVDA 2026.2
  remains the current stable NVDA release.
- When a newer stable NVDA version is released, the add-on starts a matching new
  version line. For example, NVDA 2026.2 starts add-on version `2026.2.0`, followed
  by `2026.2.1`, `2026.2.2`, `2026.2.3`, `2026.2.4`, `2026.2.5`, `2026.2.6`, `2026.2.7`, `2026.2.8`, and so on as patches are published.
- Preview, beta, release-candidate, and development NVDA versions do not start a
  new add-on version line. Only a stable NVDA release does.
- The manifest version, source version constant, build-script default, release
  notes, changelog heading, package filename, and release tag must agree before
  publishing.
- The active release line never retains references to an earlier NVDA stable line.

Before preparing any future release, confirm the latest stable NVDA version and
apply this policy. Do not publish a package whose version follows an outdated
NVDA stable release line.
