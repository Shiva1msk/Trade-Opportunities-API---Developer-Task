import logging
from datetime import datetime, timezone

import google.generativeai as genai

from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set — analysis will use fallback mode.")


def _build_prompt(sector: str, collected_data: dict) -> str:
    snippets = "\n\n".join(
        f"- **{r['title']}**: {r['snippet']}"
        for r in collected_data.get("results", [])
        if r.get("snippet")
    )
    web_context = (
        f"## Additional Web Intelligence\n{snippets}\n\n---\n" if snippets else ""
    )

    return (
        f"You are a senior trade analyst specializing in Indian markets with deep "
        f"knowledge of India's trade policies, economic sectors, and global market "
        f"dynamics as of 2025.\n\n"
        f"{web_context}"
        f"Generate a comprehensive, detailed trade opportunity report for the "
        f"**{sector.title()}** sector in India.\n\n"
        f"Produce a structured Markdown report with these exact sections:\n\n"
        f"# Trade Opportunity Report: {sector.title()} Sector — India (2025)\n\n"
        f"## 1. Executive Summary\n"
        f"3-4 sentences on current state, strategic importance, and outlook.\n\n"
        f"## 2. Market Overview\n"
        f"- Market size and growth rate (with figures)\n"
        f"- Key domestic players\n"
        f"- Recent trends (2024-2025)\n"
        f"- India's global ranking\n\n"
        f"## 3. Trade Opportunities\n"
        f"At least 4 specific actionable opportunities covering exports, import "
        f"substitution, FDI, and joint ventures.\n\n"
        f"## 4. Government Policies & Incentives\n"
        f"PLI schemes, Make in India, FTAs, SEZ benefits, export promotion.\n\n"
        f"## 5. Key Challenges & Risks\n"
        f"Regulatory, infrastructure, competitive, and geopolitical risks.\n\n"
        f"## 6. Recommended Entry Strategies\n"
        f"Step-by-step practical guidance for market entry.\n\n"
        f"## 7. Key Resources\n"
        f"Ministries, industry associations, government portals.\n\n"
        f"## 8. Disclaimer\n"
        f"Note this is AI-generated and should be verified with DGFT, Ministry of "
        f"Commerce, RBI, and IBEF before business decisions.\n\n"
        f"Use specific data, numbers, and named examples wherever possible."
    )


async def generate_analysis(sector: str, collected_data: dict) -> str:
    """Call Gemini to generate a markdown trade analysis report."""
    prompt = _build_prompt(sector, collected_data)

    if not GEMINI_API_KEY:
        logger.warning("Returning fallback report (no API key).")
        return _fallback_report(sector)

    # Try models in order — each has its own free-tier quota bucket
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest",
    ]
    last_error = None
    for model_name in models_to_try:
        try:
            logger.info(f"Trying model '{model_name}' for sector '{sector}'")
            model = genai.GenerativeModel(model_name)
            response = await model.generate_content_async(prompt)
            report = response.text
            logger.info(f"Gemini analysis complete via '{model_name}' for sector '{sector}'")
            return report
        except Exception as e:
            logger.warning(f"Model '{model_name}' failed: {e}")
            last_error = e
            continue

    logger.error(f"All Gemini models failed for sector '{sector}'")
    raise RuntimeError(f"AI analysis failed: {last_error}") from last_error


def _fallback_report(sector: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Trade Opportunity Report: {sector.title()} Sector — India

> **Note:** This is a fallback report. Set `GEMINI_API_KEY` for AI-powered analysis.

**Generated:** {ts}

## 1. Executive Summary
The {sector.title()} sector in India presents significant trade opportunities
driven by domestic demand growth, government initiatives, and global supply
chain realignment.

## 2. Market Overview
- India is one of the fastest-growing economies globally.
- The {sector.title()} sector contributes meaningfully to GDP and employment.

## 3. Trade Opportunities
- Export expansion to emerging markets
- Import substitution through domestic manufacturing
- FDI attraction via liberalized policies

## 4. Government Policies & Incentives
- Production Linked Incentive (PLI) schemes
- Make in India initiative
- Free Trade Agreements with key partners

## 5. Key Challenges & Risks
- Infrastructure gaps
- Regulatory complexity
- Global commodity price volatility

## 6. Recommended Entry Strategies
1. Partner with established local distributors
2. Leverage SEZ/EOU benefits
3. Engage with industry associations (CII, FICCI)

## 7. Key Resources
- DGFT: https://dgft.gov.in
- Ministry of Commerce: https://commerce.gov.in
- IBEF: https://www.ibef.org

## 8. Disclaimer
This report is AI-generated and should be verified with official sources.
"""
