# Security Policy

## Reporting A Vulnerability

Please report security issues privately to the maintainers when a public issue would expose users, credentials, or private content.

Do not paste the following into public issues, pull requests, discussions, or logs:

- tokens
- cookies
- API keys
- authorization headers
- browser profiles
- private course material
- private documents
- copyrighted full text
- sensitive local file paths

Use a minimal synthetic reproduction whenever possible.

## Project Security Boundaries

Source2Study does not accept features that bypass:

- login gates
- paywalls
- DRM
- anti-bot systems
- CAPTCHA
- request signatures
- platform access controls

Source2Study also does not accept cookie replay, login-session replay, browser-profile import, private-header import, or bulk account-history crawling.

## MCP And Agent Tools

MCP tools must not expose:

- shell execution
- arbitrary local file reads
- arbitrary URL fetching
- credential reads
- cookies or tokens
- login state
- browser profiles

The restricted MCP layer should use workspace allowlists, redaction, intake gates, citation validation, learning-quality validation, and deterministic evals.

## Supported Versions

This pre-1.0 project currently supports the latest released version only.
