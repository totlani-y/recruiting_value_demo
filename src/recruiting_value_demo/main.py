#!/usr/bin/env python
import json
import os
import re
import warnings

from recruiting_value_demo.crew import RecruitingValueDemoCrew
 
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
 
# --------------------------------------------------------------------------- #
# Dashboard HTML template
# Reads the JSON output and writes a self-contained HTML file next to it.
# --------------------------------------------------------------------------- #
 
DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Sourcing Shortlist — {req_id}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: #f5f5f3;
    color: #1a1a18;
    padding: 2rem 1rem;
    font-size: 14px;
    line-height: 1.6;
  }}
  .page {{ max-width: 860px; margin: 0 auto; }}
  h1 {{ font-size: 18px; font-weight: 500; margin-bottom: 4px; }}
  .meta {{ font-size: 12px; color: #666; margin-bottom: 1.5rem; }}
  .section-label {{
    font-size: 10px; font-weight: 500; letter-spacing: .07em;
    text-transform: uppercase; color: #888; margin: 0 0 10px;
  }}
  /* Summary cards */
  .summary-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 2rem; }}
  .metric {{ background: #fff; border: 0.5px solid #e0e0da; border-radius: 10px; padding: 14px 16px; }}
  .metric-val {{ font-size: 26px; font-weight: 500; line-height: 1.1; margin-bottom: 2px; }}
  .metric-lbl {{ font-size: 11px; color: #888; }}
  .v-blue {{ color: #185FA5; }} .v-green {{ color: #3B6D11; }}
  .v-coral {{ color: #993C1D; }} .v-amber {{ color: #854F0B; }}
  /* Candidate cards */
  .card {{
    background: #fff; border: 0.5px solid #e0e0da; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 10px;
  }}
  .card-top {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }}
  .avatar {{
    width: 40px; height: 40px; border-radius: 50%; display: flex;
    align-items: center; justify-content: center; font-weight: 500;
    font-size: 13px; flex-shrink: 0;
  }}
  .av-0 {{ background: #E6F1FB; color: #0C447C; }}
  .av-1 {{ background: #EAF3DE; color: #27500A; }}
  .av-2 {{ background: #FAEEDA; color: #633806; }}
  .av-3 {{ background: #FBEAF0; color: #72243E; }}
  .av-4 {{ background: #E1F5EE; color: #085041; }}
  .cname {{ font-size: 15px; font-weight: 500; margin: 0 0 2px; }}
  .ctitle {{ font-size: 12px; color: #888; margin: 0; }}
  .rank-badge {{
    font-size: 11px; font-weight: 500; padding: 3px 10px;
    border-radius: 20px; white-space: nowrap; flex-shrink: 0;
  }}
  .rank-0 {{ background: #E6F1FB; color: #185FA5; }}
  .rank-1 {{ background: #EAF3DE; color: #3B6D11; }}
  .rank-2 {{ background: #FAEEDA; color: #854F0B; }}
  /* Value bar */
  .bar-section {{ margin-bottom: 10px; }}
  .bar-label {{ display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 4px; }}
  .bar-track {{ height: 8px; background: #f0f0ec; border-radius: 4px; position: relative; overflow: hidden; }}
  .bar-high {{ height: 100%; position: absolute; top: 0; left: 0; border-radius: 4px; opacity: .35; }}
  .bar-base {{ height: 100%; position: absolute; top: 0; left: 0; border-radius: 4px; }}
  .bar-colors-0 {{ background: #378ADD; }} .bar-colors-0-light {{ background: #B5D4F4; }}
  .bar-colors-1 {{ background: #639922; }} .bar-colors-1-light {{ background: #C0DD97; }}
  .bar-colors-2 {{ background: #BA7517; }} .bar-colors-2-light {{ background: #FAC775; }}
  /* Tags */
  .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0; }}
  .tag {{
    font-size: 11px; padding: 3px 9px; border-radius: 20px;
    background: #f5f5f3; color: #555; border: 0.5px solid #e0e0da;
  }}
  .tag.matched {{ background: #EAF3DE; color: #3B6D11; border-color: #C0DD97; }}
  /* Rationale */
  .rationale {{
    font-size: 12px; color: #666; line-height: 1.6; margin-top: 8px;
    padding-top: 8px; border-top: 0.5px solid #e8e8e4;
  }}
  /* Not shortlisted */
  .ns-card {{
    background: #fff; border: 0.5px solid #e0e0da; border-radius: 10px;
    padding: .875rem 1rem; margin-bottom: 8px; display: flex;
    gap: 12px; align-items: flex-start;
  }}
  .ns-avatar {{
    width: 32px; height: 32px; border-radius: 50%; background: #f0f0ec;
    color: #888; display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 500; flex-shrink: 0;
  }}
  .ns-name {{ font-size: 13px; font-weight: 500; margin: 0 0 3px; }}
  .ns-reason {{ font-size: 12px; color: #888; line-height: 1.5; margin: 0; }}
  .review-pill {{
    font-size: 11px; background: #FAECE7; color: #993C1D;
    padding: 3px 9px; border-radius: 20px; white-space: nowrap; flex-shrink: 0;
  }}
  /* Notes */
  .note-box {{ background: #fff; border: 0.5px solid #e0e0da; border-radius: 10px; padding: 12px 14px; margin-top: 1.5rem; }}
  .note-item {{ font-size: 12px; color: #888; padding: 2px 0; display: flex; gap: 8px; }}
  .note-item::before {{ content: "›"; color: #bbb; }}
  a {{ color: #185FA5; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  @media (max-width: 600px) {{
    .summary-row {{ grid-template-columns: repeat(2, 1fr); }}
    .card-top {{ flex-direction: column; align-items: flex-start; }}
  }}
</style>
</head>
<body>
<div class="page">
  <h1>{job_title}</h1>
  <p class="meta">Requisition <strong>{req_id}</strong> &nbsp;·&nbsp; Ranked by estimated expected annual business value</p>
 
  <div class="section-label">Screening summary</div>
  <div class="summary-row">
    <div class="metric"><div class="metric-val">{screened}</div><div class="metric-lbl">Candidates screened</div></div>
    <div class="metric"><div class="metric-val v-blue">{shortlisted}</div><div class="metric-lbl">Shortlisted</div></div>
    <div class="metric"><div class="metric-val v-coral">{not_shortlisted}</div><div class="metric-lbl">Not shortlisted</div></div>
    <div class="metric"><div class="metric-val v-amber">{review_flag}</div><div class="metric-lbl">Human review required</div></div>
  </div>
 
  <div class="section-label">Shortlisted candidates</div>
  {shortlisted_html}
 
  <div class="section-label" style="margin-top:1.5rem">Not shortlisted — human review flagged</div>
  {not_shortlisted_html}
 
  <div class="note-box">
    <div class="section-label" style="margin-bottom:8px">Screening notes</div>
    {notes_html}
  </div>
</div>
</body>
</html>"""
 
 
MAX_VALUE_USD = 500_000  # bar scale anchor
 
 
def _initials(name: str) -> str:
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()
 
 
def _pct(value: int, maximum: int = MAX_VALUE_USD) -> int:
    return min(100, round(value / maximum * 100))
 
 
def _fmt_usd(v: int) -> str:
    return f"${v // 1000}K" if v >= 1000 else f"${v}"
 
 
def _build_shortlisted_html(candidates: list) -> str:
    html = ""
    for i, c in enumerate(candidates):
        idx = i % 4
        vals = c.get("estimated_expected_annual_value_usd", {})
        low, base, high = vals.get("low", 0), vals.get("base", 0), vals.get("high", 0)
        matched = c.get("job_requirement_match", {}).get("matched_must_haves", [])
        nice = c.get("job_requirement_match", {}).get("matched_nice_to_haves", [])
        tags_html = "".join(f'<span class="tag matched">{t}</span>' for t in matched)
        tags_html += "".join(f'<span class="tag">{t}</span>' for t in nice)
        rank = c.get("rank", i + 1)
        url = c.get("source_url", "#")
        title = c.get("possible_title") or "Product Designer"
        html += f"""
    <div class="card">
      <div class="card-top">
        <div style="display:flex;gap:12px;align-items:center">
          <div class="avatar av-{idx}">{_initials(c['candidate_name'])}</div>
          <div>
            <p class="cname"><a href="{url}" target="_blank">{c['candidate_name']}</a></p>
            <p class="ctitle">{title}</p>
          </div>
        </div>
        <span class="rank-badge rank-{idx}">#{rank} Ranked</span>
      </div>
      <div class="bar-section">
        <div class="bar-label">
          <span>Estimated annual value</span>
          <span><strong>{_fmt_usd(low)} – {_fmt_usd(high)}</strong> &nbsp;<span style="font-weight:400;color:#aaa">(base {_fmt_usd(base)})</span></span>
        </div>
        <div class="bar-track">
          <div class="bar-high bar-colors-{idx % 3}-light" style="width:{_pct(high)}%"></div>
          <div class="bar-base bar-colors-{idx % 3}" style="width:{_pct(base)}%"></div>
        </div>
      </div>
      <div class="tags">{tags_html}</div>
      <p class="rationale">{c.get('value_rationale', '')}</p>
    </div>"""
    return html
 
 
def _build_not_shortlisted_html(candidates: list) -> str:
    html = ""
    for c in candidates:
        html += f"""
    <div class="ns-card">
      <div class="ns-avatar">{_initials(c['candidate_name'])}</div>
      <div style="flex:1;min-width:0">
        <p class="ns-name">{c['candidate_name']} <span style="font-size:11px;font-weight:400;color:#aaa">· {c.get('possible_title','')}</span></p>
        <p class="ns-reason">{c.get('reason_not_shortlisted','')}</p>
      </div>
      {'<span class="review-pill">⚠ Review</span>' if c.get('human_review_required') else ''}
    </div>"""
    return html


def load_crew_json(path: str) -> dict:
    """Load crew JSON output, stripping optional markdown code fences."""
    with open(path, encoding="utf-8") as f:
        text = f.read().strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1)
        text = re.sub(r"\s*```\s*$", "", text)
    return json.loads(text)


def normalize_crew_json_file(path: str) -> None:
    """Rewrite crew output as clean JSON (no markdown fences)."""
    data = load_crew_json(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_dashboard(json_path: str, output_path: str) -> None:
    """Read the crew JSON output and write a self-contained HTML dashboard."""
    data = load_crew_json(json_path)
 
    summary = data.get("shortlist_summary", {})
    shortlisted = data.get("shortlisted_candidates", [])
    not_shortlisted = data.get("not_shortlisted_for_this_req", [])
    notes = data.get("screening_notes", [])
 
    notes_html = "".join(f'<div class="note-item">{n}</div>' for n in notes)
    review_flag = "⚠ Yes" if summary.get("human_review_required") else "No"
 
    html = DASHBOARD_TEMPLATE.format(
        req_id=data.get("req_id", ""),
        job_title=data.get("job_title", ""),
        screened=summary.get("candidates_screened", "—"),
        shortlisted=summary.get("shortlisted_candidates", "—"),
        not_shortlisted=summary.get("not_shortlisted", "—"),
        review_flag=review_flag,
        shortlisted_html=_build_shortlisted_html(shortlisted),
        not_shortlisted_html=_build_not_shortlisted_html(not_shortlisted),
        notes_html=notes_html,
    )
 
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
 
    print(f"\nDashboard written → {output_path}")
 
 
# --------------------------------------------------------------------------- #


def run():
    """
    Demo mocks the Job Req output, runs two agents:
    1. Talent Sourcing Agent
    2. Screening Agent
    """

    inputs = {
        "req_id": "POSTMAN_6340592003",
        "job_title": "Account Development Representative",
        "location": "San Francisco, California, United States",
        "must_haves": [
            "6 months to 2 years of business development, sales, SDR, ADR, BDR, or related experience",
            "lead qualification experience",
            "prospecting and outbound engagement",
            "account research and target-account mapping",
            "CRM hygiene and daily activity updates",
            "ability to work in a high-energy, fast-paced sales environment",
            "proficiency with standard productivity tools",
            "consultative communication with prospects",
            "ability to work onsite in San Francisco 5 days a week",
        ],
        "nice_to_haves": [
            "experience selling or prospecting into Strategic or Enterprise accounts",
            "experience engaging developers, managers, directors, VPs, or executives",
            "SaaS sales experience",
            "developer tools or API platform familiarity",
            "Salesforce, Outreach, Salesloft, ZoomInfo, Apollo, LinkedIn Sales Navigator, or similar sales tools",
            "campaign-based prospecting experience",
            "startup or high-growth technology company experience",
            "curiosity about APIs, developer workflows, or API-first software development",
        ],
        "approved_search_queries": [
            'site:linkedin.com/in ("Account Development Representative" OR ADR) "SaaS" "San Francisco"',
            'site:linkedin.com/in ("Sales Development Representative" OR SDR) "SaaS" "San Francisco"',
            'site:linkedin.com/in ("Business Development Representative" OR BDR) "enterprise accounts" "SaaS"',
            'site:linkedin.com/in ("Account Development Representative" OR "Sales Development Representative") "developer tools"',
            'site:linkedin.com/in ("SDR" OR "BDR") ("Salesforce" OR "Outreach" OR "Salesloft") "San Francisco"',
            'site:linkedin.com/in ("Account Development Representative" OR "Business Development Representative") "API" "SaaS"',
            'site:linkedin.com/in ("SDR" OR "BDR") "qualified leads" "enterprise"',
            'site:linkedin.com/in ("sales development" OR "business development") "Postman" OR "developer platform"',
        ],
        "role_value_model": {
            "time_horizon": "12 months",
            "business_context": (
                "Postman is hiring an Account Development Representative to uncover "
                "business needs in Strategic and Enterprise Accounts, create and qualify "
                "pipeline for the sales organization, and improve the prospect experience "
                "before handoff to Sales. The role is valuable when the ADR can identify "
                "high-quality prospects, research target accounts, engage qualified leads, "
                "create productive sales conversations, maintain clean CRM data, and learn "
                "Postman's API platform well enough to connect customer challenges to "
                "relevant product value."
            ),
            "source_job_posting_summary": {
                "company_context": (
                    "Postman is an API platform used by more than 45 million developers "
                    "and 500,000 organizations, including 98% of the Fortune 500."
                ),
                "opportunity_summary": (
                    "The ADR uncovers business needs for Strategic and Enterprise Accounts "
                    "and builds pipeline for the sales organization."
                ),
                "responsibility_summary": [
                    "Create strategic targets to identify new and expansion business opportunities",
                    "Meet or exceed strategic goals and committed targets",
                    "Qualify opportunities by understanding business challenges and educating prospects",
                    "Research targeted accounts to identify key contacts and critical account information",
                    "Select and engage prospects identified through marketing efforts",
                    "Become an expert in sales prospecting and enablement tools",
                    "Use customer challenges to prescribe relevant campaigns and events",
                    "Develop strong prospect relationships",
                    "Self-audit activity for accuracy and improvement",
                    "Update lead status and prospect interactions in CRM daily",
                ],
                "candidate_profile_summary": (
                    "6 months to 2 years of business development, sales, or related experience. "
                    "Lead qualification experience across organizational levels is a plus. "
                    "Energy, creativity, productivity-tool proficiency, and comfort in a fast-paced "
                    "sales environment are important."
                ),
            },
            "value_drivers": [
                {
                    "driver": "Qualified strategic and enterprise pipeline creation",
                    "why_it_matters": (
                        "The core business value of the ADR role is creating qualified pipeline "
                        "for the sales organization by identifying and engaging high-fit prospects "
                        "in Strategic and Enterprise Accounts."
                    ),
                    "estimated_annual_impact_range_usd": {
                        "low": 150000,
                        "base": 350000,
                        "high": 700000,
                    },
                },
                {
                    "driver": "Higher-quality lead qualification and sales handoff",
                    "why_it_matters": (
                        "Better discovery and consultative qualification can improve the quality "
                        "of opportunities handed to Sales, reduce wasted AE time, and increase "
                        "conversion from first meeting to pipeline."
                    ),
                    "estimated_annual_impact_range_usd": {
                        "low": 100000,
                        "base": 250000,
                        "high": 500000,
                    },
                },
                {
                    "driver": "Target-account research and contact mapping",
                    "why_it_matters": (
                        "Detailed account research helps identify the right buying committee, "
                        "prioritize high-value accounts, and personalize outreach to executives, "
                        "developers, managers, directors, and VPs."
                    ),
                    "estimated_annual_impact_range_usd": {
                        "low": 75000,
                        "base": 175000,
                        "high": 350000,
                    },
                },
                {
                    "driver": "Campaign and event-driven prospect engagement",
                    "why_it_matters": (
                        "Using customer challenges to prescribe relevant campaigns and events "
                        "can improve reply rates, meeting conversion, and early prospect trust."
                    ),
                    "estimated_annual_impact_range_usd": {
                        "low": 50000,
                        "base": 125000,
                        "high": 250000,
                    },
                },
                {
                    "driver": "CRM accuracy and sales process reliability",
                    "why_it_matters": (
                        "Daily CRM updates, clean lead statuses, and self-audited activity improve "
                        "forecasting, handoff quality, and management visibility."
                    ),
                    "estimated_annual_impact_range_usd": {
                        "low": 25000,
                        "base": 75000,
                        "high": 150000,
                    },
                },
                {
                    "driver": "Postman product and API-market fluency",
                    "why_it_matters": (
                        "The role requires learning Postman's product, competitive products, and "
                        "market knowledge. Candidates with developer-tools or API fluency may ramp "
                        "faster and engage prospects more credibly."
                    ),
                    "estimated_annual_impact_range_usd": {
                        "low": 50000,
                        "base": 150000,
                        "high": 300000,
                    },
                },
            ],
        },
        "market_rate_context": {
            "role_level": "Entry to early-career Account Development Representative",
            "official_ote_range_usd": {
                "low": 75000,
                "high": 95000,
            },
            "equity": "Competitive equity package",
            "source_note": (
                "Official Postman job posting states the reasonably estimated OTE "
                "for this role is $75,000 to $95,000 plus a competitive equity package. "
                "Actual compensation depends on skills, qualifications, and experience."
            ),
            "how_to_use_in_value_estimation": (
                "Use the OTE range as the market-rate anchor. Candidates should only receive "
                "higher expected annual value estimates when their public evidence suggests "
                "they can generate qualified pipeline, improve lead qualification, ramp quickly "
                "in SaaS/developer-tools sales, or reduce operational drag through strong CRM "
                "and prospecting discipline."
            ),
        },
    }

    print("\nRecruiting Value Demo")
    print("=" * 60)
    print("Workflow:")
    print("1. Mocked Job Req Agent output provides approved search queries.")
    print("2. Talent Sourcing Agent uses Serper to find public candidate leads.")
    print("3. Screening Agent estimates expected annual business value.")
    print("4. Screening Agent creates a value-based recruiter-review shortlist.")
    print("=" * 60)

    result = RecruitingValueDemoCrew().crew().kickoff(inputs=inputs)

    shortlist_path = "output/sourcing_value_shortlist.json"
    dashboard_path = "output/sourcing_value_shortlist.html"
    if os.path.isfile(shortlist_path):
        normalize_crew_json_file(shortlist_path)
        generate_dashboard(shortlist_path, dashboard_path)

    print("\nCrew finished.")
    print("Primary output file:")
    print(shortlist_path)
    print("Dashboard:")
    print(dashboard_path)

    print("\nFinal result:")
    print(result.raw if hasattr(result, "raw") else result)


def train():
    raise NotImplementedError("Training is not configured for this demo.")


def replay():
    raise NotImplementedError("Replay is not configured for this demo.")


def test():
    raise NotImplementedError("Testing is not configured for this demo.")


if __name__ == "__main__":
    run()