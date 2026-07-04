# Source2Study MCP Tools

This directory contains a minimal, restricted MCP-style wrapper around the existing Source2Study CLI.

The tool surface is intentionally small:

- `source2study_policy_check`
- `source2study_inspect_local`
- `source2study_ingest_local`
- `source2study_build_index`
- `source2study_generate_pack`
- `source2study_generate_personalized_pack`
- `source2study_validate_pack`
- `source2study_run_eval`

The server does not expose shell execution, arbitrary URL fetches, arbitrary local file reads, cookies, browser profiles, login sessions, bulk platform crawling, paywall bypass, DRM bypass, anti-bot bypass, or signature reverse engineering.

Run a schema smoke check:

```bash
python mcp/server.py --list-tools
```

Run as a stdio process from an MCP client:

```bash
python mcp/server.py
```

Configuration is read from `.source2study/config.json` when present. If the file does not exist, the server defaults to:

```json
{
  "allowed_workspaces": ["./workspace", "./examples", "./tmp/source2study"],
  "network_enabled": false,
  "allow_degraded": false,
  "max_source_size_mb": 50,
  "max_output_chars": 20000
}
```

All tool responses are structured JSON and are redacted before being returned to an agent.
