# Changelog

## Unreleased

- Added system `curl` fallback for live HTTP requests when Python HTTPS
  certificate verification fails.
- Added regression coverage for package and installed skill runtime HTTP
  fallback behavior.
- Added comparison-topic fanout so live sources search each compared entity
  separately before merging evidence.
- Changed default live sources to GitHub, Hacker News, and PyPI for stronger
  technical stack adoption signal.

## 0.1.0 - 2026-06-09

Initial public release.

- Added installable `aistack-radar` skill contract.
- Added self-contained skill runtime under `skills/aistack-radar/scripts/`.
- Added deterministic fixture mode for offline demos and CI.
- Added package CLI under `src/aistack_radar/`.
- Added live connectors for GitHub, Hacker News, Reddit, PyPI, npm, and arXiv.
- Added transparent evidence scoring, recommendations, risk flags, and source health.
- Added JSON, Markdown, and self-contained HTML report writers.
- Added unit tests and GitHub Actions CI.
