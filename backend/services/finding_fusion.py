import re
from difflib import SequenceMatcher
from typing import List, Dict, Tuple
from schemas.finding import RawFinding, FindingSchema, SuggestionSchema

class FindingFusionService:
    """Merges and deduplicates findings from multiple analyzers (Static tools, Local rules, LLM)."""

    @staticmethod
    def _normalize_string(text: str) -> str:
        """Strip punctuation and casing for semantic comparison."""
        return re.sub(r"[^\w\s]", "", (text or "").lower()).strip()

    @classmethod
    def _is_similar_issue(cls, f1: RawFinding, f2: RawFinding) -> bool:
        """Determine whether two findings describe the same underlying issue."""
        # Line numbers must match or be closely adjacent (+/- 1 line)
        line_diff = abs((f1.line or 1) - (f2.line or 1))
        if line_diff > 1:
            return False

        # If issue types are identical or compatible
        type1 = f1.issue_type.lower()
        type2 = f2.issue_type.lower()
        compatible_types = (
            type1 == type2
            or (type1 in {"security", "vulnerability"} and type2 in {"security", "vulnerability"})
            or (type1 in {"logical_error", "runtime_risk"} and type2 in {"logical_error", "runtime_risk"})
            or (type1 in {"code_quality", "maintainability"} and type2 in {"code_quality", "maintainability"})
        )

        norm_title1 = cls._normalize_string(f1.title)
        norm_title2 = cls._normalize_string(f2.title)
        title_ratio = SequenceMatcher(None, norm_title1, norm_title2).ratio()

        norm_msg1 = cls._normalize_string(f1.message)
        norm_msg2 = cls._normalize_string(f2.message)
        msg_ratio = SequenceMatcher(None, norm_msg1, norm_msg2).ratio()

        # Direct title match or high textual similarity
        if norm_title1 in norm_title2 or norm_title2 in norm_title1:
            return True

        if compatible_types and (title_ratio > 0.55 or msg_ratio > 0.60):
            return True

        return False

    @classmethod
    def fuse_findings(cls, raw_findings: List[RawFinding]) -> List[FindingSchema]:
        """Group and fuse matching findings into deduplicated unified FindingSchema instances."""
        if not raw_findings:
            return []

        clusters: List[List[RawFinding]] = []

        for item in raw_findings:
            matched = False
            for cluster in clusters:
                if any(cls._is_similar_issue(item, existing) for existing in cluster):
                    cluster.append(item)
                    matched = True
                    break
            if not matched:
                clusters.append([item])

        fused_list: List[FindingSchema] = []

        severity_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}

        for cluster in clusters:
            # Determine combined sources
            sources = sorted(list(set(f.source for f in cluster)))
            # If both static/local and LLM contributed, categorize source as ["static", "llm"]
            normalized_sources = []
            has_static = any(s not in {"llm", "ai"} for s in sources)
            has_llm = any(s in {"llm", "ai"} for s in sources)
            if has_static:
                normalized_sources.append("static")
            if has_llm:
                normalized_sources.append("llm")
            if not normalized_sources:
                normalized_sources = ["static"]

            # Select the most critical severity in the cluster
            highest_sev = max(cluster, key=lambda f: severity_weights.get(f.severity.upper(), 1)).severity.upper()

            # Choose the most descriptive title and explanation (prefer LLM or most detailed)
            best_desc = max(cluster, key=lambda f: len(f.explanation or "") + len(f.message or ""))
            primary = cluster[0]

            # Calculate fused confidence: boost when corroborated by multiple sources
            base_conf = max(f.confidence for f in cluster)
            if len(normalized_sources) > 1:
                # Corroborated finding gets a confidence boost, capped at 0.98
                fused_conf = min(0.98, round(base_conf + 0.08, 2))
            else:
                fused_conf = round(base_conf, 2)

            # Find best suggestion in cluster
            best_suggestion = None
            for item in cluster:
                if item.suggestion and (item.suggestion.corrected_code or item.suggestion.recommendation):
                    best_suggestion = item.suggestion
                    break

            fused_finding = FindingSchema(
                line=primary.line or 1,
                line_number=primary.line or 1,
                issue_type=primary.issue_type,
                severity=highest_sev,
                title=best_desc.title or primary.title,
                message=best_desc.message or primary.message,
                explanation=best_desc.explanation or primary.explanation or best_desc.message,
                evidence=primary.evidence or best_desc.evidence,
                confidence=fused_conf,
                sources=normalized_sources,
                suggestion=best_suggestion
            )
            fused_list.append(fused_finding)

        # Sort by line number ascending, then severity descending
        fused_list.sort(key=lambda x: (x.line or 0, -severity_weights.get(x.severity.upper(), 0)))
        return fused_list
