from __future__ import annotations
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).parent
TEMPLATE_PATH = ROOT / "templates" / "cover_letter_template.tex"
PROFILE_PATH = ROOT / "profile.yaml"
BULLETS_PATH = ROOT / "bullets.yaml"

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def pick_bullets(all_bullets: list[dict], tags: list[str], n: int = 3) -> list[str]:
    tags_set = set(t.lower() for t in tags)
    scored = []
    for b in all_bullets:
        b_tags = set(t.lower() for t in b.get("tags", []))
        score = len(tags_set.intersection(b_tags))
        scored.append((score, b["text"]))
    scored.sort(key=lambda x: x[0], reverse=True)
    chosen = [t for s, t in scored if s > 0][:n]
    # fallback if not enough matches
    if len(chosen) < n:
        for _, t in scored:
            if t not in chosen:
                chosen.append(t)
            if len(chosen) == n:
                break
    return chosen[:n]

def render_template(template: str, data: dict) -> str:
    def repl(m: re.Match) -> str:
        key = m.group(1)
        return str(data.get(key, ""))
    return re.sub(r"\{\{\{([a-zA-Z0-9_]+)\}\}\}", repl, template)

def main(job_file: str):
    job_path = ROOT / "jobs" / job_file
    job = load_yaml(job_path)
    profile = load_yaml(PROFILE_PATH)
    bullets_yaml = load_yaml(BULLETS_PATH)
    all_bullets = bullets_yaml["bullets"]

    b1, b2, b3 = pick_bullets(all_bullets, job.get("focus_tags", []), n=3)

    # Add periods if missing (simple polish)
    def ensure_period(s: str) -> str:
        s = s.strip()
        return s if s.endswith((".", "!", "?")) else s + "."

    data = {
        "name": profile["name"],
        "location": profile["location"],
        "phone": profile["phone"],
        "email": profile["email"],
        "linkedin": profile["linkedin"],
        "github": profile["github"],
        "headline": ensure_period(profile["headline"]),
        "date": job.get("date", ""),
        "hiring_manager": job.get("hiring_manager", "Hiring Team"),
        "company": job["company"],
        "team": job.get("team", ""),
        "role": job["role"],
        "job_location": job.get("location", ""),
        "why_company": ensure_period(job.get("why_company", "")),
        "why_role": ensure_period(job.get("why_role", "")),
        "bullet_1": ensure_period(b1),
        "bullet_2": ensure_period(b2),
        "bullet_3": ensure_period(b3),
        "closing_line": ensure_period(job.get("closing_line", "")),
    }

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    out_tex = render_template(template, data)

    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"cover_letter_{job['company'].lower().replace(' ', '_')}.tex"
    out_path.write_text(out_tex, encoding="utf-8")
    print(f"Wrote: {out_path}")

if __name__ == "__main__":
    import sys
    job_file = sys.argv[1] if len(sys.argv) > 1 else "example_job.yaml"
    main(job_file)
