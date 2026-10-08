import ast
import re
from typing import Dict, Any, List, Optional
from schemas.finding import RawFinding

class CodeParser:
    """Provides syntax-aware AST parsing and metrics extraction without code execution."""

    @staticmethod
    def parse_python(code: str) -> tuple[Optional[ast.AST], List[RawFinding], Dict[str, Any]]:
        """Parse Python source into AST, detect syntax errors, and extract code metrics."""
        findings: List[RawFinding] = []
        metrics = {
            "loc": len([line for line in code.splitlines() if line.strip()]),
            "functions": 0,
            "classes": 0,
            "max_nesting_depth": 0,
            "complexity": 1
        }

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            finding = RawFinding(
                line=e.lineno or 1,
                issue_type="syntax_error",
                severity="CRITICAL",
                title=f"Python Syntax Error: {e.msg}",
                message=f"SyntaxError on line {e.lineno}: {e.msg}",
                explanation=f"The Python parser encountered an invalid syntax construct at line {e.lineno}, column {e.offset}: '{e.text.strip() if e.text else ''}'.",
                evidence=e.text.strip() if e.text else f"Line {e.lineno}",
                confidence=1.0,
                source="parser"
            )
            findings.append(finding)
            return None, findings, metrics

        # Traverse AST for structural metrics
        max_depth = 0
        def calculate_depth(node: ast.AST, current_depth: int = 0):
            nonlocal max_depth
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                current_depth += 1
                if current_depth > max_depth:
                    max_depth = current_depth
            for child in ast.iter_child_nodes(node):
                calculate_depth(child, current_depth)

        calculate_depth(tree)
        metrics["max_nesting_depth"] = max_depth

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                metrics["complexity"] += 1

        return tree, findings, metrics

    @staticmethod
    def parse_generic(code: str, language: str) -> tuple[List[RawFinding], Dict[str, Any]]:
        """Perform bracket-matching and structural analysis for non-Python languages."""
        findings: List[RawFinding] = []
        lines = code.splitlines()
        metrics = {
            "loc": len([l for l in lines if l.strip()]),
            "functions": 0,
            "classes": 0,
            "max_nesting_depth": 0,
            "complexity": 1
        }

        # Check bracket balancing
        stack = []
        pairs = {')': '(', '}': '{', ']': '['}
        for idx, line in enumerate(lines, start=1):
            for col, ch in enumerate(line):
                if ch in "({[":
                    stack.append((ch, idx, col))
                elif ch in ")}]":
                    if not stack:
                        findings.append(RawFinding(
                            line=idx,
                            issue_type="syntax_error",
                            severity="CRITICAL",
                            title=f"Unmatched closing bracket '{ch}'",
                            message=f"Encountered closing bracket '{ch}' with no matching opening bracket.",
                            explanation=f"A closing bracket '{ch}' was found at line {idx} without a corresponding opening bracket.",
                            evidence=line.strip(),
                            confidence=0.95,
                            source="parser"
                        ))
                    else:
                        top, open_line, _ = stack.pop()
                        if pairs[ch] != top:
                            findings.append(RawFinding(
                                line=idx,
                                issue_type="syntax_error",
                                severity="CRITICAL",
                                title=f"Mismatched bracket '{ch}' (opened with '{top}' at line {open_line})",
                                message=f"Expected closing for '{top}' but found '{ch}'.",
                                explanation=f"The bracket opened at line {open_line} is closed incorrectly with '{ch}' at line {idx}.",
                                evidence=line.strip(),
                                confidence=0.95,
                                source="parser"
                            ))

        if stack:
            unclosed_ch, unclosed_line, _ = stack[-1]
            findings.append(RawFinding(
                line=unclosed_line,
                issue_type="syntax_error",
                severity="CRITICAL",
                title=f"Unclosed opening bracket '{unclosed_ch}'",
                message=f"Opening bracket '{unclosed_ch}' at line {unclosed_line} is never closed.",
                explanation=f"A code block opened at line {unclosed_line} was not properly terminated.",
                evidence=lines[unclosed_line - 1].strip() if unclosed_line <= len(lines) else "",
                confidence=0.95,
                source="parser"
            ))

        # Count functions/classes via regex
        if language == "javascript":
            metrics["functions"] = len(re.findall(r"\bfunction\b|\b=>\b", code))
            metrics["classes"] = len(re.findall(r"\bclass\s+\w+", code))
        elif language == "java":
            metrics["functions"] = len(re.findall(r"\b(public|private|protected)\s+[\w<>]+\s+\w+\s*\(", code))
            metrics["classes"] = len(re.findall(r"\bclass\s+\w+", code))

        return findings, metrics
