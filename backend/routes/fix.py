from fastapi import APIRouter
from schemas.review import FixRequest, FixResponse
from services.fix_generator import FixGeneratorService

router = APIRouter(prefix="/api/fix", tags=["Fix Recommendation"])

@router.post("/generate", response_model=FixResponse)
def generate_fix(payload: FixRequest):
    """Generate or refine a proposed code remediation and compute visual diff."""
    return FixGeneratorService.generate_fix(
        original_code=payload.original_code,
        finding=payload.finding,
        language=payload.language or "python"
    )
