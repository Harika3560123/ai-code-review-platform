import os
import json
import shutil
import tempfile
import subprocess
import logging
from typing import List, Dict, Tuple
from schemas.finding import RawFinding, SuggestionSchema

logger = logging.getLogger("code_review.static_analyzer")

class StaticAnalyzerService:
    """Executes deterministic static analyzers (Pylint, Bandit, Semgrep, ESLint) safely."""

    def __init__(self):
        self.has_pylint = shutil.which("pylint") is not None
        self.has_bandit = shutil.which("bandit") is not None
        self.has_semgrep = shutil.which("semgrep") is not None
        self.has_eslint = shutil.which("eslint") is not None or shutil.which("npx") is not None

    def get_analyzer_status(self) -> Dict[str, str]:
        """Return availability status for all supported analyzers."""
        return {
            "pylint": "available" if self.has_pylint else "not installed (gracefully bypassed)",
            "bandit": "available" if self.has_bandit else "not installed (gracefully bypassed)",
            "semgrep": "available" if self.has_semgrep else "not installed (gracefully bypassed)",
            "eslint": "available" if self.has_eslint else "not installed (gracefully bypassed)"
        }

    def analyze(self, code: str, language: str) -> Tuple[List[RawFinding], Dict[str, str]]:
        """Run all applicable static analyzers for the detected language."""
        status_map = self.get_analyzer_status()
        findings: List[RawFinding] = []

        # Create isolated temporary file for analysis (never executed)
        ext_map = {"python": ".py", "javascript": ".js", "java": ".java", "c": ".c", "cpp": ".cpp"}
        suffix = ext_map.get(language, ".txt")

        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        try:
            if language == "python":
                if self.has_bandit:
                    findings.extend(self._run_bandit(temp_path))
                if self.has_pylint:
                    findings.extend(self._run_pylint(temp_path))
            elif language == "javascript":
                if self.has_eslint:
                    findings.extend(self._run_eslint(temp_path))
            
            # Cross-language Semgrep if available
            if self.has_semgrep:
                findings.extend(self._run_semgrep(temp_path, language))

        except Exception as e:
            logger.error(f"Error during static analysis orchestration: {e}")
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

        return findings, status_map

    def _run_bandit(self, file_path: str) -> List[RawFinding]:
        """Run Bandit security analyzer on Python code."""
        findings: List[RawFinding] = []
        try:
            cmd = ["bandit", "-f", "json", "-q", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            output = result.stdout.strip()
            if output:
                data = json.loads(output)
                for issue in data.get("results", []):
                    sev = issue.get("issue_severity", "MEDIUM").upper()
                    if sev not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
                        sev = "MEDIUM"
                    findings.append(RawFinding(
                        line=issue.get("line_number", 1),
                        issue_type="security",
                        severity=sev,
                        title=issue.get("test_name", "Security Vulnerability"),
                        message=issue.get("issue_text", "Bandit flagged a security vulnerability."),
                        explanation=f"Bandit rule {issue.get('test_id')}: {issue.get('issue_text')}. Severity: {sev}, Confidence: {issue.get('issue_confidence')}.",
                        evidence=issue.get("code", "").strip(),
                        confidence=0.85 if issue.get("issue_confidence") == "HIGH" else 0.70,
                        source="bandit",
                        suggestion=SuggestionSchema(
                            original_code=issue.get("code", "").strip(),
                            recommendation=f"Review and remediate according to rule {issue.get('test_id')}."
                        )
                    ))
        except Exception as e:
            logger.warning(f"Bandit execution bypassed: {e}")
        return findings

    def _run_pylint(self, file_path: str) -> List[RawFinding]:
        """Run Pylint code quality analyzer on Python code."""
        findings: List[RawFinding] = []
        try:
            cmd = ["pylint", "--output-format=json", "--score=n", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            output = result.stdout.strip()
            if output:
                try:
                    issues = json.loads(output)
                except json.JSONDecodeError:
                    issues = []
                for item in issues:
                    msg_type = item.get("type", "convention")
                    # Map pylint message type to standard severity
                    if msg_type in ("fatal", "error"):
                        sev = "HIGH"
                        itype = "logical_error"
                    elif msg_type == "warning":
                        sev = "MEDIUM"
                        itype = "runtime_risk"
                    else:
                        sev = "LOW"
                        itype = "code_quality"

                    symbol = item.get("symbol", "pylint-finding")
                    line_no = item.get("line", 1)
                    findings.append(RawFinding(
                        line=line_no,
                        issue_type=itype,
                        severity=sev,
                        title=f"Pylint: {symbol.replace('-', ' ').title()}",
                        message=item.get("message", ""),
                        explanation=f"Pylint detected '{symbol}' ({item.get('message-id')}). {item.get('message')}",
                        evidence=f"Line {line_no}",
                        confidence=0.80,
                        source="pylint",
                        suggestion=SuggestionSchema(
                            recommendation=f"Refactor to satisfy Pylint rule '{symbol}'."
                        )
                    ))
        except Exception as e:
            logger.warning(f"Pylint execution bypassed: {e}")
        return findings

    def _run_eslint(self, file_path: str) -> List[RawFinding]:
        """Run ESLint or basic node lint check if available."""
        findings: List[RawFinding] = []
        try:
            cmd = ["npx", "--no-install", "eslint", "-f", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            output = result.stdout.strip()
            if output:
                data = json.loads(output)
                if isinstance(data, list) and data:
                    for msg in data[0].get("messages", []):
                        sev = "HIGH" if msg.get("severity") == 2 else "MEDIUM"
                        findings.append(RawFinding(
                            line=msg.get("line", 1),
                            issue_type="code_quality" if "style" in msg.get("ruleId", "") else "logical_error",
                            severity=sev,
                            title=f"ESLint: {msg.get('ruleId', 'Syntax/Linter Warning')}",
                            message=msg.get("message", ""),
                            explanation=f"ESLint reported: {msg.get('message')}",
                            evidence=f"Line {msg.get('line', 1)}",
                            confidence=0.85,
                            source="eslint"
                        ))
        except Exception as e:
            logger.debug(f"ESLint check note: {e}")
        return findings

    def _run_semgrep(self, file_path: str, language: str) -> List[RawFinding]:
        """Run Semgrep rule-based pattern checks if available."""
        findings: List[RawFinding] = []
        try:
            cmd = ["semgrep", "--config", "auto", "--json", "-q", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            output = result.stdout.strip()
            if output:
                data = json.loads(output)
                for res in data.get("results", []):
                    check_id = res.get("check_id", "semgrep-finding")
                    sev = res.get("extra", {}).get("severity", "WARNING").upper()
                    mapped_sev = "HIGH" if sev == "ERROR" else "MEDIUM"
                    findings.append(RawFinding(
                        line=res.get("start", {}).get("line", 1),
                        issue_type="security" if "security" in check_id.lower() else "code_quality",
                        severity=mapped_sev,
                        title=f"Semgrep: {check_id.split('.')[-1].replace('-', ' ').title()}",
                        message=res.get("extra", {}).get("message", ""),
                        explanation=res.get("extra", {}).get("message", ""),
                        evidence=res.get("extra", {}).get("lines", "").strip(),
                        confidence=0.90,
                        source="semgrep"
                    ))
        except Exception as e:
            logger.debug(f"Semgrep check note: {e}")
        return findings
