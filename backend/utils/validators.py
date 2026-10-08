import os
from fastapi import HTTPException, UploadFile, status

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024 # 2 Megabytes
ALLOWED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp"
}

SUPPORTED_LANGUAGES = {"python", "javascript", "java", "c", "cpp"}


def validate_code_input(code: str, language: str = None) -> tuple[str, str]:
    """Validate pasted source code and normalize language."""
    if not code or not code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source code cannot be empty."
        )
    
    if len(code.encode("utf-8")) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Code snippet exceeds maximum permitted size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
        )
    
    lang = (language or "python").strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
        # Default or fallback gracefully
        lang = "python"
    
    return code, lang


def validate_uploaded_file(file: UploadFile) -> tuple[str, str]:
    """Validate uploaded file for size, safe filename, and supported extension."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required."
        )
    
    clean_filename = os.path.basename(file.filename)
    _, ext = os.path.splitext(clean_filename.lower())
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS.keys())}."
        )
    
    detected_language = ALLOWED_EXTENSIONS[ext]
    return clean_filename, detected_language
