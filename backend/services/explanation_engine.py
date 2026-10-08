import re
from typing import List, Dict, Any, Optional
from schemas.finding import RawFinding, SuggestionSchema, FindingSchema

class ExplanationEngine:
    """Enhances findings with structured Explainable AI (XAI) narratives and provides local offline fallback analysis."""

    @staticmethod
    def run_local_fallback_analysis(code: str, language: str) -> List[RawFinding]:
        """Deterministic, pattern-based demonstration rules for offline/demo operation.
        
        Explicitly labelled as 'Local Static Analysis'.
        """
        findings: List[RawFinding] = []
        lines = code.splitlines()

        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()

            # Rule 1: Division by zero risk
            div_match = re.search(r"/\s*([a-zA-Z_]\w*)\b", line_str)
            if div_match:
                var_name = div_match.group(1)
                # Check if preceding context (up to 10 lines above) validates the divisor
                start_context = max(0, idx - 10)
                context_above = "\n".join(lines[start_context:idx])
                
                # Check for explicit checks: `if var == 0:`, `if var != 0:`, `if not var:`, `try: ... except ZeroDivisionError`
                is_validated = (
                    re.search(rf"\bif\s+.*{var_name}\s*==\s*0", context_above) or
                    re.search(rf"\bif\s+.*{var_name}\s*!=?\s*0", context_above) or
                    re.search(rf"\bif\s+not\s+{var_name}\b", context_above) or
                    re.search(rf"\bif\s+{var_name}\s*:\b", context_above) or
                    "ZeroDivisionError" in context_above or
                    re.search(r"if\s+.*!=?\s*0", line_str)
                )

                if not is_validated and not line_str.startswith("#") and not line_str.startswith("//") and not line_str.startswith("/*"):
                    findings.append(RawFinding(
                        line=idx,
                        issue_type="logical_error",
                        severity="HIGH",
                        title="Possible division by zero risk",
                        message=f"The divisor variable '{var_name}' is used in division without validating whether it is zero.",
                        explanation=f"A division operation ('/{var_name}') is performed at line {idx}. If '{var_name}' evaluates to zero, a runtime exception (e.g. ZeroDivisionError or ArithmeticException) will crash the process.",
                        evidence=line_str,
                        confidence=0.88,
                        source="Local Static Analysis",
                        suggestion=SuggestionSchema(
                            original_code=line_str,
                            corrected_code=f"if {var_name} == 0:\n    raise ValueError('Divisor cannot be zero')\n{line_str}",
                            recommendation=f"Validate that '{var_name}' is non-zero before attempting division."
                        )
                    ))

            # Rule 2: Hard-coded password / secret credential
            pwd_match = re.search(r"(password|secret|api_key|token|passwd|auth_token)\s*=\s*['\"][^'\"]{8,}['\"]", line_str, re.IGNORECASE)
            if pwd_match and not line_str.startswith("#") and not line_str.startswith("//"):
                findings.append(RawFinding(
                    line=idx,
                    issue_type="security",
                    severity="HIGH",
                    title="Hard-coded credential or secret detected",
                    message="Hard-coded sensitive credential detected in source code.",
                    explanation=f"Plaintext secrets or API tokens embedded directly in code files violate security compliance (CWE-798). They can be exposed through version control history or client distribution.",
                    evidence=line_str,
                    confidence=0.94,
                    source="Local Static Analysis",
                    suggestion=SuggestionSchema(
                        original_code=line_str,
                        corrected_code=re.sub(r"=\s*['\"][^'\"]+['\"]", "= os.getenv('API_SECRET')", line_str),
                        recommendation="Store secrets in environment variables or an encrypted secrets vault instead of committing them."
                    )
                ))

            # Rule 3: SQL Injection pattern (string concatenation into SQL query)
            sql_match = re.search(r"(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*(\+|%|\.format|\$)", line_str, re.IGNORECASE)
            if sql_match and not line_str.startswith("#") and not line_str.startswith("//"):
                findings.append(RawFinding(
                    line=idx,
                    issue_type="security",
                    severity="CRITICAL",
                    title="Potential SQL Injection vulnerability",
                    message="SQL query constructed via dynamic string concatenation.",
                    explanation=f"Directly concatenating untrusted user input into an SQL statement allows attackers to manipulate query logic (CWE-89), potentially resulting in unauthorized data exfiltration or deletion.",
                    evidence=line_str,
                    confidence=0.92,
                    source="Local Static Analysis",
                    suggestion=SuggestionSchema(
                        original_code=line_str,
                        corrected_code="# Use parameterized queries:\ncursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                        recommendation="Replace string concatenation with parameterized SQL queries or ORM queries."
                    )
                ))

            # Rule 4: Dangerous execution primitives
            danger_match = re.search(r"\b(eval|exec|dangerouslySetInnerHTML)\b\s*\(", line_str)
            if danger_match and not line_str.startswith("#") and not line_str.startswith("//"):
                func_name = danger_match.group(1)
                findings.append(RawFinding(
                    line=idx,
                    issue_type="security",
                    severity="CRITICAL",
                    title=f"Use of dangerous execution primitive '{func_name}'",
                    message=f"Invoking '{func_name}' allows execution of arbitrary code strings.",
                    explanation=f"The function '{func_name}' executes raw string payloads within the interpreter/DOM environment, creating severe remote code execution or cross-site scripting (XSS) risks.",
                    evidence=line_str,
                    confidence=0.96,
                    source="Local Static Analysis",
                    suggestion=SuggestionSchema(
                        original_code=line_str,
                        corrected_code="# Replace eval with safe parsing:\nimport ast\nast.literal_eval(payload)",
                        recommendation=f"Avoid '{func_name}'. Use structured serialization (e.g., json.loads or ast.literal_eval)."
                    )
                ))

            # Rule 5: Bare exception handling (Python)
            if language == "python" and re.search(r"except\s*:", line_str):
                findings.append(RawFinding(
                    line=idx,
                    issue_type="code_quality",
                    severity="MEDIUM",
                    title="Bare except clause catches all exceptions",
                    message="Bare 'except:' intercepts system signals including KeyboardInterrupt and SystemExit.",
                    explanation="Catching all exceptions without qualification obscures bugs, hides tracebacks, and makes graceful shutdowns difficult.",
                    evidence=line_str,
                    confidence=0.90,
                    source="Local Static Analysis",
                    suggestion=SuggestionSchema(
                        original_code=line_str,
                        corrected_code="except Exception as e:\n    logger.error(f'Handled error: {e}')",
                        recommendation="Specify concrete exception classes (e.g. 'except (ValueError, KeyError):') or at minimum 'except Exception:'."
                    )
                ))

            # Rule 6: Missing error handling in async/Promise (JavaScript)
            if language == "javascript" and re.search(r"\.then\(", line_str) and not re.search(r"\.catch\(", line_str):
                findings.append(RawFinding(
                    line=idx,
                    issue_type="runtime_risk",
                    severity="LOW",
                    title="Potential unhandled Promise rejection",
                    message="Promise chain does not include an explicit '.catch()' error handler.",
                    explanation="Asynchronous operations that reject without an attached .catch handler will trigger unhandledRejection events in Node.js or silent failures in browsers.",
                    evidence=line_str,
                    confidence=0.75,
                    source="Local Static Analysis",
                    suggestion=SuggestionSchema(
                        original_code=line_str,
                        corrected_code=f"{line_str}.catch(err => console.error(err));",
                        recommendation="Chain a .catch() handler or wrap in a try/catch block when using async/await."
                    )
                ))

        return findings

    @staticmethod
    def enrich_explainability(finding: FindingSchema, source_code: str) -> FindingSchema:
        """Ensure all 5 explainability dimensions (What, Where, Why, Evidence, How to fix) are populated clearly."""
        lines = source_code.splitlines()
        line_no = finding.line or finding.line_number or 1

        # Extract evidence line if missing
        if not finding.evidence or finding.evidence.strip() == "":
            if 1 <= line_no <= len(lines):
                finding.evidence = lines[line_no - 1].strip()
            else:
                finding.evidence = f"Line {line_no}"

        # Ensure explanation addresses cause and impact
        if not finding.explanation or finding.explanation.strip() == "":
            finding.explanation = (
                f"At line {line_no}, the construct '{finding.evidence}' triggers an issue ({finding.title}). "
                f"This can degrade system reliability, introduce security vulnerabilities, or hinder maintainability."
            )

        # Ensure suggestion is present
        if not finding.suggestion:
            finding.suggestion = SuggestionSchema(
                original_code=finding.evidence,
                corrected_code=f"# Remediation required for {finding.title}\n{finding.evidence}",
                recommendation=f"Review line {line_no} to ensure proper input validation and compliance with {finding.issue_type} best practices."
            )

        return finding
