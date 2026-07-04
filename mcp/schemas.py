from __future__ import annotations

"""JSON schemas for the restricted Source2Study MCP tool surface."""

BASE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "error": {"type": ["object", "null"]},
    },
    "required": ["status", "warnings"],
}


PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "goal": {"type": "string"},
        "current_level": {"type": "string"},
        "time_budget": {"type": "string"},
        "use_case": {"type": "string"},
        "preferred_style": {"type": "string"},
        "must_include": {"type": "array", "items": {"type": "string"}},
        "avoid": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}


TOOLS = [
    {
        "name": "source2study_policy_check",
        "title": "Source2Study Policy Check",
        "description": "Check whether a local source or URL is allowed without reading cookies, credentials, or network content.",
        "inputSchema": {
            "type": "object",
            "properties": {"source": {"type": "string"}},
            "required": ["source"],
        },
        "outputSchema": BASE_OUTPUT_SCHEMA,
    },
    {
        "name": "source2study_inspect_local",
        "title": "Source2Study Inspect Local",
        "description": "Inspect one allowlisted local source and write an intake report before ingestion.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "source": {"type": "string"},
                "source_type": {"type": "string"},
            },
            "required": ["workspace", "source"],
        },
        "outputSchema": BASE_OUTPUT_SCHEMA,
    },
    {
        "name": "source2study_ingest_local",
        "title": "Source2Study Ingest Local",
        "description": "Ingest allowlisted local files or directories into a Source2Study workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "sources": {"type": "array", "items": {"type": "string"}},
                "source_type": {"type": "string"},
            },
            "required": ["workspace", "sources"],
        },
        "outputSchema": BASE_OUTPUT_SCHEMA,
    },
    {
        "name": "source2study_build_index",
        "title": "Source2Study Build Index",
        "description": "Rebuild evidence ledgers for an allowlisted workspace after intake gates pass.",
        "inputSchema": {
            "type": "object",
            "properties": {"workspace": {"type": "string"}},
            "required": ["workspace"],
        },
        "outputSchema": BASE_OUTPUT_SCHEMA,
    },
    {
        "name": "source2study_generate_pack",
        "title": "Source2Study Generate Pack",
        "description": "Generate a source-grounded learning pack from an allowlisted workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "mode": {"type": "string"},
                "format": {"type": "string", "enum": ["markdown", "md", "docx", "pdf"]},
            },
            "required": ["workspace", "mode"],
        },
        "outputSchema": BASE_OUTPUT_SCHEMA,
    },
    {
        "name": "source2study_generate_personalized_pack",
        "title": "Source2Study Generate Personalized Pack",
        "description": "Generate a personalized learning pack with citation and learning-quality reports.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "mode": {"type": "string"},
                "profile": PROFILE_SCHEMA,
                "format": {"type": "string", "enum": ["markdown", "md", "docx", "pdf"]},
            },
            "required": ["workspace", "mode", "profile"],
        },
        "outputSchema": BASE_OUTPUT_SCHEMA,
    },
    {
        "name": "source2study_validate_pack",
        "title": "Source2Study Validate Pack",
        "description": "Run citation validation for an allowlisted workspace and optional pack JSON.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "pack_path": {"type": "string"},
                "mode": {"type": "string"},
            },
            "required": ["workspace"],
        },
        "outputSchema": BASE_OUTPUT_SCHEMA,
    },
    {
        "name": "source2study_run_eval",
        "title": "Source2Study Run Eval",
        "description": "Run a deterministic built-in eval suite without arbitrary source or URL access.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "suite": {
                    "type": "string",
                    "enum": ["standard_demo", "personalized_demo", "degraded_demo"],
                }
            },
            "required": ["suite"],
        },
        "outputSchema": BASE_OUTPUT_SCHEMA,
    },
]


def list_tools() -> list[dict]:
    return list(TOOLS)
