## Summary

What changed?

## Scope

- [ ] adapter or source intake
- [ ] evidence/citation/quality gate
- [ ] generation/template
- [ ] exporter
- [ ] MCP/agent tooling
- [ ] docs/release
- [ ] tests/evals

## Source Fidelity

- [ ] IntakeReport behavior is preserved or improved.
- [ ] No source assets are silently dropped.
- [ ] Low-confidence evidence is labeled.
- [ ] New claims are source-grounded.

## Safety

- [ ] No cookies, tokens, API keys, browser profiles, or login state.
- [ ] No login/paywall/DRM/anti-bot/signature bypass.
- [ ] No arbitrary shell, file-read, or URL-fetch capability is exposed to agents.

## Verification

```bash
python -m unittest discover -s tests
python -m compileall -q src evals mcp
python evals/run_eval.py --suite standard_demo
```

Add any additional commands run:

## Notes

Known limitations or follow-up work:
