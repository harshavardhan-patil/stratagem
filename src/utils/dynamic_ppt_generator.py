import tempfile
import json
import re
from pptx import Presentation
from src.utils import ppt

def generate_dynamic_pptx_from_chat(chat_history, llm):
    prs = Presentation()

    # Prompt the LLM to extract structured content
    prompt = f"""
    Based on the following conversation history, generate structured content for a business strategy presentation with this JSON format:
    {{
        "title": "Presentation Title",
        "subtitle": "Subtitle goes here",
        "overview": ["Company founded in...", "..."],
        "swot": {{
            "strengths": ["...", "..."],
            "weaknesses": ["...", "..."],
            "opportunities": ["...", "..."],
            "threats": ["...", "..."]
        }},
        "roadmap": {{
            "short_term": ["...", "..."],
            "mid_term": ["...", "..."],
            "long_term": ["...", "..."]
        }},
        "financials": ["Projected revenue...", "Operating costs...", "Profit margin..."]
    }}
    Return ONLY the JSON object.

    --- Chat History ---
    {chat_history}
    """

    response = llm.invoke(prompt).content
    json_str = re.sub(r"```json|```", "", response).strip()
    content = json.loads(json_str)

    # Build slides dynamically
    ppt.add_styled_title_slide(prs, content["title"], content["subtitle"])
    ppt.add_section_divider_slide(prs, "Company Overview")
    ppt.add_bullet_slide(prs, "Company Overview", content["overview"])
    ppt.add_section_divider_slide(prs, "SWOT Analysis")
    ppt.add_swot_slide_with_data(prs, content["swot"])
    ppt.add_section_divider_slide(prs, "Strategic Roadmap")
    ppt.add_roadmap_slide_with_data(prs, content["roadmap"])
    ppt.add_section_divider_slide(prs, "Financials")
    ppt.add_financial_chart_slide_with_data(prs, content["financials"])

    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
    prs.save(output_file.name)
    return output_file.name
