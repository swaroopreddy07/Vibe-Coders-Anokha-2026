# adk/skills/extract_job_skill.py
from adk.tools.scraper_tool import scrape_job_url

def extract_job_requirements(url: str) -> dict:
    res = scrape_job_url(url)
    # Give full debug info
    if res.get("error"):
        return {"error": "scrape_failed", "detail": res.get("error")}

    snippet = res.get("snippet", "")
    text = res.get("text", "")

    # SIMPLE heuristic extraction (improve later with LLM)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    responsibilities = [ln for ln in lines if any(k in ln.lower() for k in ("responsib", "you will", "we are looking", "role:"))][:25]
    qualifications = [ln for ln in lines if any(k in ln.lower() for k in ("qualif", "requirement", "must have", "preferred", "bachelor", "degree"))][:25]
    skills = []
    # If snippet or lines include a skills line (comma separated), extract it:
    for ln in lines:
        if any(k in ln.lower() for k in ("skills", "technolog", "tech stack", "requirements:")):
            skills.append(ln)
    # fallback: search for lines with common tech names (simple)
    if not skills:
        tech_keywords = ["python","java","sql","docker","aws","react","node","tensorflow","pytorch"]
        for ln in lines:
            if any(tk in ln.lower() for tk in tech_keywords):
                skills.append(ln)
    return {
        "responsibilities": responsibilities,
        "qualifications": qualifications,
        "skills": skills,
        "snippet": snippet,
        "source": res.get("source")
    }
