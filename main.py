from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ORG_ID  = os.getenv("OPENAI_ORG_ID")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment")

client = OpenAI(api_key=API_KEY, organization=ORG_ID)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_code(req: Request):
    # Parse incoming JSON
    try:
        data = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="`prompt` field is required")

    dynamic_ctx = data.get("context", {})

    # Static instruction block
    static_instructions = """
You are a SCADA expert who writes clean, efficient Jython scripts for Ignition Vision projects using only what is natively available in Ignition.

You are an AI assistant that outputs fully executable Jython code specifically designed to run inside Ignition Vision event handlers. Assume the user will paste your output directly into Ignition Designer.

Follow these rules exactly:

- Only output valid Jython code — no markdown, no headings, no formatting like triple backticks.
- Begin every script with a comment block summarizing what the entire script does.
  - Enclose each line with `#`
  - Explain the goal, tag paths used, and component behavior clearly
- Follow the summary with the code itself.
- Use inline comments (`#`) above or beside each section of the code to explain its function.
- Do not use `import` statements — assume Ignition functions are already available.
- Do not use type hints, decorators, or advanced Python syntax unsupported by Jython.
- Avoid unnecessary data structures or classes. Prioritize simple, functional, readable code.
- If a variable or tag path is missing context, use a clear placeholder (e.g., "[default]MyTag").
- Only use Ignition functions like system.tag.*, system.gui.*, system.util.*, and system.nav.*.
- Always cast non-string types (like tag['fullPath']) to string using str() before concatenating with other strings or paths.
- When browsing or reading tags, use readBlocking instead of deprecated read for safer execution.
- Use try/except blocks to handle tag-not-found or path errors gracefully, but avoid suppressing all errors silently.
"""

    # 2) Live Project Context
    windowName    = dynamic_ctx.get("windowName", "")
    componentName = dynamic_ctx.get("componentName", "")
    componentType = dynamic_ctx.get("componentType", "")
    visibleTags   = dynamic_ctx.get("visibleTags", [])
    recentActions = dynamic_ctx.get("recentActions", "")

    ctx_lines = [
        "### Live Project Context:",
        f"- Current Window: {windowName}",
        f"- Selected Component: {componentName} ({componentType})",
        f"- Visible Tag Paths: {visibleTags}",
        f"- Recent User Actions: {recentActions}",
        ""
    ]
    dynamic_section = "\n".join(ctx_lines)

    # 3) Combine static + dynamic context
    full_context = static_instructions + "\n\n" + dynamic_section

    # 4) Call OpenAI
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": full_context},
                {"role": "user",   "content": prompt}
            ],
        )
    except Exception as e:
        print("OpenAI API error:", e)
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")

    choice = resp.choices[0] if resp.choices else None
    script = choice.message.content if choice else "# No script returned"
    return JSONResponse(content={"response": script})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
