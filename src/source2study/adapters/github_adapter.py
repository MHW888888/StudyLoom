from __future__ import annotations

import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from source2study.adapters.base import AdapterError, AdapterResult, SourceAdapter, SourceRequest
from source2study.adapters.utils import file_sha256, read_text_lossy, split_paragraphs, stable_id, utc_now
from source2study.models.evidence import EvidenceLocation, EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class GitHubAdapter(SourceAdapter):
    name = "github_repo"
    source_types = ("github_repo",)
    risk_level = "medium"
    default_enabled = True
    allowed_methods = ("local_directory", "public_git_clone_opt_in", "user_provided_archive")
    blocked_methods = ("private_token_in_url", "secret_leakage", "credentialed_bulk_clone")
    source_type_aliases = ("github", "repo", "github_repo", "local_repo")
    max_file_chars = 20000
    included_names = {"README.md", "README", "pyproject.toml", "package.json", "requirements.txt"}
    included_dirs = {"docs", "examples", "tests"}
    text_suffixes = {".md", ".txt", ".py", ".js", ".ts", ".toml", ".json", ".yaml", ".yml"}

    def can_handle(self, request: SourceRequest) -> bool:
        value = request.value
        path = Path(value)
        if path.exists() and path.is_dir():
            return True
        parsed = urlparse(value)
        return parsed.netloc.lower() == "github.com" and bool(parsed.path.strip("/"))

    def capability(self) -> AdapterCapability:
        return AdapterCapability(
            source_type="github_repo",
            availability="high",
            supported_methods=["local_directory", "public_git_clone_opt_in"],
            required_authorization=["public_repo_or_user_authorized_private_repo"],
            expected_outputs=["README/docs/examples/tests/source snippets"],
            known_risks=["private token leakage", "large repos", "generated/vendor files"],
            fallbacks=["provide local clone", "provide selected files or archive"],
            risk_level=self.risk_level,
            default_enabled=self.default_enabled,
            allowed_methods=list(self.allowed_methods),
            blocked_methods=list(self.blocked_methods),
        )

    def ingest(self, request: SourceRequest) -> AdapterResult:
        repo_path, warnings = self._resolve_repo(request)
        source_id = stable_id("src_repo", str(repo_path))
        files = list(self._iter_relevant_files(repo_path))
        if not files:
            raise AdapterError("No relevant text files found in repository.", "Provide README/docs/examples manually.")

        source = SourceRecord(
            source_id=source_id,
            source_type="github_repo",
            source_url_or_path=request.value,
            title=repo_path.name,
            platform="github" if "github.com" in request.value else "local_git",
            capture_time=utc_now(),
            transcript_source="manual",
            language="unknown",
            duration_or_page_count=str(len(files)),
            files_created=[],
            hashes={"tree": stable_id("tree", "|".join(str(p.relative_to(repo_path)) for p in files))},
            capability=self.capability(),
        )

        evidence: list[EvidenceRecord] = []
        for file_index, file_path in enumerate(files, start=1):
            rel = file_path.relative_to(repo_path).as_posix()
            text = read_text_lossy(file_path)[: self.max_file_chars]
            for chunk_index, chunk in enumerate(split_paragraphs(text), start=1):
                evidence.append(
                    EvidenceRecord(
                        evidence_id=f"ev_{source_id}_{file_index}_{chunk_index}",
                        source_id=source_id,
                        source_type="github_repo",
                        text=chunk,
                        location=EvidenceLocation(path=rel, section=f"chunk {chunk_index}"),
                        confidence=1.0,
                        metadata={"file_hash": file_sha256(file_path)},
                    )
                )
        return AdapterResult(source=source, evidence=evidence, warnings=warnings)

    def _resolve_repo(self, request: SourceRequest) -> tuple[Path, list[str]]:
        path = Path(request.value)
        if path.exists() and path.is_dir():
            return path.resolve(), []

        if not request.policy.allow_network:
            raise AdapterError(
                "GitHub URL ingestion requires explicit network authorization.",
                "Clone the repo locally or rerun with --allow-network.",
            )

        parsed = urlparse(request.value)
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            raise AdapterError("Invalid GitHub repository URL.", "Provide https://github.com/owner/repo.")
        owner, repo = parts[0], parts[1].removesuffix(".git")
        target = request.workspace / "sources" / "github" / f"{owner}_{repo}"
        if target.exists():
            return target, ["Reused cached git clone."]
        target.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.pop("GITHUB_TOKEN", None)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", f"https://github.com/{owner}/{repo}.git", str(target)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
        )
        if result.returncode != 0:
            raise AdapterError("git clone failed.", "Provide a local clone or selected files.")
        return target, ["Cloned public GitHub repository."]

    def _iter_relevant_files(self, repo_path: Path):
        ignored = {".git", "node_modules", "dist", "build", ".venv", "__pycache__"}
        for file_path in repo_path.rglob("*"):
            if not file_path.is_file():
                continue
            parts = set(file_path.relative_to(repo_path).parts)
            if parts & ignored:
                continue
            if file_path.name in self.included_names or file_path.suffix.lower() in self.text_suffixes:
                if file_path.stat().st_size <= 200_000:
                    yield file_path
