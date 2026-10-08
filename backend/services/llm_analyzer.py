import json
import re
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from schemas.finding import RawFinding, SuggestionSchema

logger = logging.getLogger("code_review.llm_analyzer")

SYSTEM_PROMPT = """You are an expert software code reviewer.
Analyze the supplied source code using the static-analysis findings as supporting evidence.
Identify only issues that have reasonable evidence.

Check:
1. Logical bugs
2. Runtime risks
3. Security vulnerabilities
4. Poor coding practices
5. Maintainability problems

For every issue provide:
- line: exact 1-indexed line number where the issue occurs
- issue_type: one of ["security", "logical_error", "runtime_risk", "maintainability", "code_quality", "syntax_error"]
- severity: one of ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
- title: concise title describing the issue
- message: clear 1-2 sentence issue message
- explanation: detailed explanation answering why it is a problem and its impact
- evidence: exact code snippet or line from the source code showing the issue
- confidence: number between 0.5 and 1.0 representing system confidence
- suggested_fix: concrete corrected code replacement snippet
- recommendation: actionable guidance on how to fix and avoid this issue

Rules:
- Do not invent issues without evidence.
- Prefer exact source lines.
- Explain the issue in simple, educational language.
- Return VALID JSON ONLY in the following exact format:
{
  "issues": [
    {
      "line": 8,
      "issue_type": "logical_error",
      "severity": "HIGH",
      "title": "Possible division by zero",
      "message": "The divisor is used without validating whether it equals zero.",
      "explanation": "The function performs division without verifying that the divisor b is non-zero, causing a ZeroDivisionError at runtime.",
      "evidence": "return a / b",
      "confidence": 0.92,
      "suggested_fix": "if b == 0:\\n    return None\\nreturn a / b",
      "recommendation": "Validate the divisor before performing division."
    }
  ]
}
"""

class LLMAnalyzerService:
    """Orchestrates AI analysis with Gemini / OpenAI with resilient parsing and fallback."""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY.strip() if settings.LLM_API_KEY else None
        self.provider = settings.LLM_PROVIDER.lower()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def analyze(self, code: str, language: str, static_findings: List[RawFinding]) -> tuple[List[RawFinding], str]:
        """Send code and static analysis context to LLM; safely extract and validate JSON."""
        if not self.is_configured():
            return [], "LLM service is not configured (API key missing). Static and local rules will be used."

        static_context = [
            {
                "line": f.line,
                "source": f.source,
                "type": f.issue_type,
                "severity": f.severity,
                "title": f.title,
                "message": f.message
            }
            for f in static_findings
        ]

        user_prompt = f"""Programming Language: {language}

Static Analysis Findings:
{json.dumps(static_context, indent=2)}

Source Code:
```
{code}
```
"""

        try:
            raw_text = self._call_llm(user_prompt)
            findings = self._parse_and_validate_json(raw_text)
            return findings, "LLM analysis completed successfully."
        except Exception as e:
            logger.error(f"LLM analysis encountered an error: {e}")
            return [], f"LLM analysis failed gracefully: {str(e)}"

    def _call_llm(self, user_content: str) -> str:
        """Execute request against Gemini or OpenAI based on settings."""
        if self.provider == "openai":
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            resp = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30.0)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        else:
            # Default: Gemini API using google-genai or google.generativeai or REST
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
                response = model.generate_content(user_content)
                return response.text
            except Exception as e:
                # Fallback to direct REST endpoint for maximum compatibility
                import httpx
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                body = {
                    "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\n{user_content}"}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                resp = httpx.post(url, json=body, timeout=30.0)
                resp.raise_for_status()
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

    def _parse_and_validate_json(self, raw_text: str) -> List[RawFinding]:
        """Safely extract JSON object from markdown or text and map to RawFinding objects."""
        clean_text = raw_text.strip()
        
        # Strip markdown fences if present
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text)
            clean_text = re.sub(r"\s*```$", "", clean_text)

        try:
            parsed = json.loads(clean_text)
        except json.JSONDecodeError:
            # Safe JSON extraction regex
            match = re.search(r"\{.*\}", clean_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
            else:
                logger.warning("Failed to extract valid JSON from LLM response.")
                return []

        issues = parsed.get("issues", [])
        validated_findings: List[RawFinding] = []

        for item in issues:
            try:
                line_no = int(item.get("line", 1))
                sev = str(item.get("severity", "MEDIUM")).upper()
                if sev not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
                    sev = "MEDIUM"

                validated_findings.append(RawFinding(
                    line=line_no,
                    issue_type=str(item.get("issue_type", "logical_error")),
                    severity=sev,
                    title=str(item.get("title", "AI Identified Issue")),
                    message=str(item.get("message", "")),
                    explanation=str(item.get("explanation", "")),
                    evidence=str(item.get("evidence", "")),
                    confidence=float(item.get("confidence", 0.85)),
                    source="llm",
                    suggestion=SuggestionSchema(
                        original_code=str(item.get("evidence", "")),
                        corrected_code=str(item.get("suggested_fix", "")),
                        recommendation=str(item.get("recommendation", ""))
                    )
                ))
            except Exception as val_err:
                logger.warning(f"Skipping malformed LLM item: {val_err}")

        return validated_findings
