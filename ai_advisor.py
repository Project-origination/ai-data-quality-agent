import json

from openai import OpenAI


# ============================================================
# LOCAL LLM CONFIGURATION
# ============================================================

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio",
)

MODEL = "qwen/qwen3-4b-2507"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a senior Data Quality and Data Governance advisor.

Your role is NOT to detect data-quality issues yourself.
A deterministic Python engine has already performed the analysis.

You receive:
- an overall data-quality score,
- multidimensional quality scores,
- detected issues,
- severity levels,
- affected columns,
- affected row counts.

Your job is to interpret these findings for business and data teams.

Rules:
1. Never invent issues that are not present in the supplied analysis.
2. Never claim that a detected statistical outlier is necessarily an error.
3. Distinguish confirmed rule violations from signals requiring investigation.
4. Prioritize Critical issues before High, Medium and Low issues.
5. Explain potential business consequences.
6. Recommend concrete remediation actions.
7. Keep the analysis concise and professional.
8. Do not use unnecessary technical jargon.
9. Use the supplied quality_status exactly. Do not reinterpret the overall score using your own thresholds.

Return the analysis using exactly these sections:

EXECUTIVE SUMMARY
PRIORITY ACTIONS
BUSINESS IMPACT
RECOMMENDED REMEDIATION
"""


# ============================================================
# BUILD LLM CONTEXT
# ============================================================

def quality_status(score):

    if score >= 90:
        return "Excellent"

    if score >= 75:
        return "Healthy"

    if score >= 50:
        return "Needs attention"

    return "Critical attention"


def build_quality_context(result):

    context = {
        "overall_quality_score": result["quality_score"],
        "quality_status": quality_status(
            result["quality_score"]
        ),
        "quality_dimensions": result["quality_dimensions"],
        "severity_counts": result["severity_counts"],
        "issues": result["issues"],
    }

    return json.dumps(
        context,
        indent=2,
        ensure_ascii=False,
    )
    

# ============================================================
# AI ADVISOR
# ============================================================

def generate_quality_advice(result):

    quality_context = build_quality_context(
        result
    )

    user_prompt = f"""
Interpret the following deterministic data-quality assessment.

Do not perform a new data-quality analysis.
Base your answer strictly on the supplied findings.

DATA QUALITY ASSESSMENT:

{quality_context}
"""

    response = client.chat.completions.create(
        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],

        temperature=0.2,
    )

    return (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


# ============================================================
# CONNECTION TEST
# ============================================================

def lm_studio_available():

    try:

        client.models.list()

        return True

    except Exception:

        return False

    