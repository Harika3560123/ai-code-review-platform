from typing import List, Dict, Any, Tuple
from schemas.finding import FindingSchema
from schemas.review import DimensionScores, SummaryCounts

class ScoringService:
    """Calculates multidimensional quality scores and issue distribution counts."""

    # Dimension weights as per Project Specification
    WEIGHT_SECURITY = 0.25
    WEIGHT_CORRECTNESS = 0.30
    WEIGHT_MAINTAINABILITY = 0.20
    WEIGHT_STYLE = 0.10
    WEIGHT_COMPLEXITY = 0.15

    # Penalties per severity level
    PENALTIES = {
        "CRITICAL": 30.0,
        "HIGH": 18.0,
        "MEDIUM": 8.0,
        "LOW": 3.0,
        "INFO": 1.0
    }

    @classmethod
    def calculate_scores_and_summary(
        cls, 
        findings: List[FindingSchema], 
        metrics: Dict[str, Any]
    ) -> Tuple[DimensionScores, SummaryCounts]:
        """Compute the weighted overall quality score and summary counts."""
        sec_score = 100.0
        corr_score = 100.0
        maint_score = 100.0
        style_score = 100.0
        comp_score = 100.0

        summary = SummaryCounts()

        for f in findings:
            sev = f.severity.upper()
            penalty = cls.PENALTIES.get(sev, 5.0)

            # Update issue counts
            if sev == "CRITICAL":
                summary.critical += 1
            elif sev == "HIGH":
                summary.high += 1
            elif sev == "MEDIUM":
                summary.medium += 1
            elif sev == "LOW":
                summary.low += 1
            else:
                summary.info += 1

            # Distribute penalty by issue type
            itype = f.issue_type.lower()
            if "security" in itype:
                sec_score -= penalty
            elif "syntax" in itype or "logical" in itype or "runtime" in itype:
                corr_score -= penalty
            elif "maintain" in itype:
                maint_score -= penalty
            elif "style" in itype or "convention" in itype:
                style_score -= penalty
            elif "complexity" in itype or "performance" in itype:
                comp_score -= penalty
            else:
                # Default distribution across correctness & maintainability
                corr_score -= penalty * 0.6
                maint_score -= penalty * 0.4

        # Complexity penalty from AST metrics if high nesting depth or cyclomatic complexity
        ast_complexity = metrics.get("complexity", 1)
        max_depth = metrics.get("max_nesting_depth", 0)
        if ast_complexity > 10:
            comp_score -= min(30.0, (ast_complexity - 10) * 2.5)
        if max_depth > 4:
            maint_score -= min(20.0, (max_depth - 4) * 4.0)

        # Clamp all dimension scores between 0 and 100
        sec_score = max(0.0, min(100.0, round(sec_score, 2)))
        corr_score = max(0.0, min(100.0, round(corr_score, 2)))
        maint_score = max(0.0, min(100.0, round(maint_score, 2)))
        style_score = max(0.0, min(100.0, round(style_score, 2)))
        comp_score = max(0.0, min(100.0, round(comp_score, 2)))

        # Overall Formula from Section 14:
        # Overall = (Security × 0.25) + (Correctness × 0.30) + (Maintainability × 0.20) + (Style × 0.10) + (Complexity × 0.15)
        overall = (
            (sec_score * cls.WEIGHT_SECURITY)
            + (corr_score * cls.WEIGHT_CORRECTNESS)
            + (maint_score * cls.WEIGHT_MAINTAINABILITY)
            + (style_score * cls.WEIGHT_STYLE)
            + (comp_score * cls.WEIGHT_COMPLEXITY)
        )
        overall = max(0.0, min(100.0, round(overall, 2)))

        scores = DimensionScores(
            overall=overall,
            security=sec_score,
            correctness=corr_score,
            maintainability=maint_score,
            style=style_score,
            complexity=comp_score
        )

        return scores, summary
