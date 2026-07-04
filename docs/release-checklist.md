# Release Checklist

Use this checklist before publishing a GitHub release.

## Version And Docs

- [ ] version bumped in `pyproject.toml`
- [ ] version bumped in `src/source2study/__init__.py`
- [ ] MCP server metadata version updated
- [ ] README updated
- [ ] roadmap updated
- [ ] examples updated
- [ ] known limitations documented
- [ ] compliance docs reviewed
- [ ] source capability matrix reviewed

## Verification

- [ ] tests pass: `python -m unittest discover -s tests`
- [ ] compileall pass: `python -m compileall -q src evals mcp`
- [ ] CLI smoke pass: `source2study --help`
- [ ] inspect smoke pass: `source2study inspect --help`
- [ ] standard demo pass
- [ ] low-risk demo pass
- [ ] personalized demo pass
- [ ] degraded demo pass
- [ ] eval suite pass: `standard_demo`
- [ ] eval suite pass: `personalized_demo`
- [ ] eval suite pass: `degraded_demo`
- [ ] MCP smoke pass: `python mcp/server.py --list-tools`
- [ ] MCP tool tests pass: `python -m unittest tests/test_mcp_tools.py`
- [ ] skill structure check pass

## Repository Hygiene

- [ ] no temporary workspace committed
- [ ] no `.source2study/cache` committed
- [ ] no `__pycache__` committed
- [ ] no egg-info committed
- [ ] no large generated outputs committed
- [ ] no `.env` committed
- [ ] no tokens, cookies, API keys, authorization headers, private keys, browser profiles, or login state

## Release Notes

- [ ] summarize user-facing changes
- [ ] summarize safety/compliance changes
- [ ] summarize verification results
- [ ] list known limitations
- [ ] list next milestone
