# Security Policy

## Supported Scope

This repository contains workflow docs, templates, merge scripts, and agent
skills. Security reports are welcome for:

- Exposed secrets or private infrastructure details.
- Unsafe workflow guidance that could cause data loss or unintended disclosure.
- Skill content that encourages unsafe handling of credentials or private data.
- Supply-chain, license, or provenance issues in imported skill material.

## Reporting

Please report security issues privately through the repository owner's preferred
private contact channel. If no private channel is listed, open a minimal public
issue that says a private security report is needed, but do not include secrets
or exploit details in the issue body.

## Handling Expectations

- Do not post credentials, private keys, tokens, or private hostnames publicly.
- Include the affected file path, why it is risky, and a minimal reproduction or
  example when safe.
- For imported third-party material, include the provenance path when known.

## Maintainer Response

Maintainers should remove or redact sensitive content, preserve audit history
where safe, update state docs, and add validation to prevent recurrence.
