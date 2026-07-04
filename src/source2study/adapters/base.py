from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from source2study.config import SourcePolicy
from source2study.models.evidence import EvidenceRecord
from source2study.models.source import AdapterCapability, SourceRecord


class AdapterError(RuntimeError):
    def __init__(self, message: str, fallback: str | None = None):
        super().__init__(message)
        self.fallback = fallback


@dataclass(frozen=True)
class SourceRequest:
    value: str
    workspace: Path
    policy: SourcePolicy = field(default_factory=SourcePolicy)
    authorization: str = "personal_learning"
    source_type: str | None = None


@dataclass(frozen=True)
class AdapterResult:
    source: SourceRecord
    evidence: list[EvidenceRecord]
    artifacts: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SourceAdapter(ABC):
    name = "source_adapter"
    source_types: tuple[str, ...] = ("unknown",)
    risk_level = "unknown"
    default_enabled = True
    allowed_methods: tuple[str, ...] = ()
    blocked_methods: tuple[str, ...] = ()
    source_type_aliases: tuple[str, ...] = ()

    @abstractmethod
    def can_handle(self, request: SourceRequest) -> bool:
        raise NotImplementedError

    @abstractmethod
    def capability(self) -> AdapterCapability:
        raise NotImplementedError

    @abstractmethod
    def ingest(self, request: SourceRequest) -> AdapterResult:
        raise NotImplementedError

    def policy_check(self, request: SourceRequest):
        from source2study.safety.policy import PolicyDecision, PolicyEngine

        decision = PolicyEngine().check_source(request.value, request.policy, adapter=self)
        if decision.allowed and not self.default_enabled:
            return PolicyDecision(
                allowed=False,
                reason=f"{self.name} is not enabled by default.",
                safe_alternatives=self.fallback_options(request.value),
                source_type=self.source_types[0] if self.source_types else "unknown",
                risk_level=self.risk_level,
                allowed_methods=list(self.allowed_methods),
                blocked_methods=list(self.blocked_methods),
            )
        return decision

    def extract(self, source: str | SourceRequest, workspace: Path | None = None) -> list[EvidenceRecord]:
        request = source if isinstance(source, SourceRequest) else SourceRequest(str(source), workspace or Path.cwd())
        return self.ingest(request).evidence

    def matches_source_type(self, source_type: str | None) -> bool:
        if not source_type:
            return True
        normalized = source_type.lower().replace("-", "_")
        names = {self.name.lower().replace("-", "_"), *(item.lower().replace("-", "_") for item in self.source_types)}
        names.update(item.lower().replace("-", "_") for item in self.source_type_aliases)
        return normalized in names

    def fallback_options(self, source: str | None = None) -> list[str]:
        capability = self.capability()
        if capability.fallbacks:
            return list(capability.fallbacks)
        return ["Provide user-exported PDF/HTML/Markdown/screenshots or manual notes."]

    def contract(self) -> dict:
        return {
            "name": self.name,
            "source_types": list(self.source_types),
            "risk_level": self.risk_level,
            "default_enabled": self.default_enabled,
            "allowed_methods": list(self.allowed_methods),
            "blocked_methods": list(self.blocked_methods),
            "source_type_aliases": list(self.source_type_aliases),
            "fallback_options": self.fallback_options(),
        }
