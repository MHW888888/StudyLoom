# MCP And Agent Tools

Source2Study can be called by agents, but only through a restricted, auditable tool surface.

The goal is not to make agents more powerful. The goal is to let agents run the same verified local workflow that the CLI already uses:

```text
policy -> inspect -> ingest local -> build index -> generate -> validate -> eval
```

## Tool Surface

The MCP server exposes only:

| Tool | Purpose |
|---|---|
| `source2study_policy_check` | Check whether a source is allowed without fetching it. |
| `source2study_inspect_local` | Inspect one allowlisted local source and write intake reports. |
| `source2study_ingest_local` | Ingest allowlisted local files or directories. |
| `source2study_build_index` | Rebuild evidence ledgers after intake gates pass. |
| `source2study_generate_pack` | Generate a source-grounded learning pack. |
| `source2study_generate_personalized_pack` | Generate with a learner profile and write citation and learning-quality reports. |
| `source2study_validate_pack` | Run citation validation. |
| `source2study_run_eval` | Run built-in deterministic eval suites. |

The server does not expose:

- arbitrary URL fetching
- arbitrary local file reads
- shell command execution
- cookie import
- login-session import
- browser-profile access
- bulk platform crawling
- anti-bot bypass
- paywall bypass
- DRM bypass
- request-signature reverse engineering

## Workspace Allowlist

MCP tools read `.source2study/config.json` when present. If it does not exist, they use:

```json
{
  "allowed_workspaces": [
    "./workspace",
    "./examples",
    "./tmp/source2study"
  ],
  "network_enabled": false,
  "allow_degraded": false,
  "max_source_size_mb": 50,
  "max_output_chars": 20000
}
```

All local source paths and workspace paths must resolve inside an allowed root. Network access is disabled by default.

## Tool Inputs And Outputs

`source2study_generate_personalized_pack` input:

```json
{
  "workspace": "./workspace/demo",
  "mode": "beginner",
  "profile": {
    "goal": "Understand these sources from zero base",
    "current_level": "beginner",
    "time_budget": "2 hours",
    "use_case": "self_study",
    "preferred_style": "clear, structured, example-driven"
  },
  "format": "markdown"
}
```

Typical output:

```json
{
  "status": "pass",
  "pack_path": "outputs/study_pack_beginner_full.json",
  "output_path": "outputs/learning_pack_beginner_full.md",
  "citation_report_path": "outputs/citation_report_beginner_full.json",
  "learning_quality_report_path": "outputs/learning_quality_report_beginner_full.json",
  "intake_summary_path": "intake_report.json",
  "warnings": []
}
```

Tool responses are structured JSON. They return paths, metadata, report status, warnings, and metrics rather than large raw source text.

## Recommended Agent Workflow

1. Ask for or read the learner profile.
2. Run `source2study_policy_check`.
3. Run `source2study_inspect_local`.
4. Stop if intake is `blocked` or `fail`.
5. If intake is `degraded`, disclose the risk and continue only when allowed.
6. Run `source2study_ingest_local`.
7. Run `source2study_build_index`.
8. Run `source2study_generate_personalized_pack`.
9. Run `source2study_validate_pack`.
10. Check `learning_quality_report_<mode>.json`.
11. Run `source2study_run_eval` for demos, release checks, or regression checks.

## Agent Boundaries

Agents must preserve `Source Fidelity First`. They should not silently skip intake warnings, low-confidence OCR, missing timestamps, missing source locations, or degraded extraction.

Agents must not request cookies, tokens, login sessions, browser profiles, private headers, localStorage, sessionStorage, CAPTCHA bypass, proxy pools, paywall bypass, DRM bypass, or request-signature reverse engineering.

## Codex / Claude / Cursor

Codex and Claude skill files live under:

```text
skills/codex/source2study/SKILL.md
skills/claude/source2study/SKILL.md
```

Agent metadata lives under:

```text
agents/openai.yaml
agents/claude.yaml
```

For Codex, configure the MCP server as a stdio server that runs:

```bash
python mcp/server.py
```

Keep client-side tool approvals conservative. The Source2Study tool surface is already restricted, but users should still see when agents invoke tools.

## Why The Tool Surface Is Small

MCP tools are model-invoked actions. A small tool surface reduces data exfiltration risk, keeps source fidelity auditable, and prevents Source2Study from turning into a crawling or bypass toolkit.
