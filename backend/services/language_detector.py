import os
import re
from typing import Optional

EXTENSION_MAP = {
    ".py": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c",
    ".hpp": "cpp"
}

def detect_language_from_filename(filename: Optional[str]) -> Optional[str]:
    """Detect programming language using file extension."""
    if not filename:
        return None
    _, ext = os.path.splitext(filename.lower())
    return EXTENSION_MAP.get(ext)

def detect_language_from_content(code: str) -> str:
    """Heuristically inspect code syntax to determine language when not provided."""
    code_sample = code[:2000]
    
    # Python markers: 'def ', 'import ', 'from ... import', ': \n', 'print('
    python_score = 0
    if re.search(r"\bdef\s+[a-zA-Z_]\w*\s*\(", code_sample):
        python_score += 4
    if re.search(r"\bimport\s+[a-zA-Z_]", code_sample) or re.search(r"\bfrom\s+[a-zA-Z_]\w*\s+import", code_sample):
        python_score += 3
    if re.search(r":\s*(\n|\r\n)\s+", code_sample):
        python_score += 2
    if re.search(r"\belif\b", code_sample):
        python_score += 3
    if re.search(r"__name__\s*==\s*['\"]__main__['\"]", code_sample):
        python_score += 5

    # JavaScript markers: 'const ', 'let ', 'var ', 'function', 'console.log', '=>', '===', 'require('
    js_score = 0
    if re.search(r"\b(const|let|var)\s+[a-zA-Z_$]", code_sample):
        js_score += 4
    if re.search(r"\bfunction\s*[a-zA-Z_$]?\(", code_sample):
        js_score += 3
    if "console.log" in code_sample:
        js_score += 3
    if "=>" in code_sample:
        js_score += 2
    if "===" in code_sample:
        js_score += 2

    # Java markers: 'public class', 'System.out.println', 'public static void main'
    java_score = 0
    if re.search(r"\bpublic\s+class\s+[a-zA-Z_]", code_sample):
        java_score += 5
    if "System.out.println" in code_sample:
        java_score += 4
    if "public static void main" in code_sample:
        java_score += 5

    scores = {"python": python_score, "javascript": js_score, "java": java_score}
    best_lang, best_score = max(scores.items(), key=lambda item: item[1])
    return best_lang if best_score > 0 else "python"

def resolve_language(language: Optional[str], filename: Optional[str], code: str) -> str:
    """Resolve the definitive programming language from explicit choice, filename, or content."""
    if language and language.strip().lower() in {"python", "javascript", "java", "c", "cpp"}:
        return language.strip().lower()
    from_file = detect_language_from_filename(filename)
    if from_file:
        return from_file
    return detect_language_from_content(code)
