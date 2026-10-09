import difflib
from typing import Dict, Any, Optional
from schemas.finding import FindingSchema, SuggestionSchema
from schemas.review import FixResponse

class FixGeneratorService:
    """Produces code remediation suggestions and unified visual diffs."""

    @staticmethod
    def generate_unified_diff(original: str, corrected: str, filename: str = "snippet.py") -> str:
        """Compute unified diff between original code and proposed fix."""
        original_lines = original.splitlines(keepends=True)
        corrected_lines = corrected.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            corrected_lines,
            fromfile=f"a/{filename} (original)",
            tofile=f"b/{filename} (suggested fix)",
            lineterm=""
        )
        return "".join(diff)

    @classmethod
    def generate_fix(cls, original_code: str, finding: FindingSchema, language: str = "python") -> FixResponse:
        """Ensure a complete fix recommendation and diff are available for a given finding."""
        evidence = (finding.evidence or "").strip()
        lines = original_code.splitlines()
        line_no = finding.line or finding.line_number or 1

        original_snippet = evidence
        if not original_snippet and 1 <= line_no <= len(lines):
            original_snippet = lines[line_no - 1]

        corrected_snippet = ""
        rec = ""

        if finding.suggestion and finding.suggestion.corrected_code:
            corrected_snippet = finding.suggestion.corrected_code
            rec = finding.suggestion.recommendation or f"Apply suggested remediation for {finding.title}."
        else:
            # Deterministic heuristic fallback fix based on issue type
            if finding.issue_type == "security":
                var_name = original_snippet.split("=")[0].strip() if "=" in original_snippet else "secret_val"
                corrected_snippet = f"# [Security Fix] Load secret via environment variable\nimport os\n{var_name} = os.getenv('SECRET_KEY', '')"
                rec = "Avoid storing secrets in source code. Retrieve via environment configuration."
            elif finding.issue_type == "logical_error" and "/" in original_snippet:
                corrected_snippet = f"# [Validation] Check for zero before division\nif divisor != 0:\n    {original_snippet}\nelse:\n    return 0"
                rec = "Validate that the denominator is not zero prior to division."
            else:
                corrected_snippet = f"# Refactored implementation:\n{original_snippet}"
                rec = f"Review and revise {original_snippet} to address {finding.title}."

        diff = cls.generate_unified_diff(original_snippet, corrected_snippet)

        return FixResponse(
            original_code=original_snippet,
            corrected_code=corrected_snippet,
            recommendation=rec,
            diff_unified=diff
        )
