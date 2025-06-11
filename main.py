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

print("***** KEY LOADED:", API_KEY[:5] + "..." if API_KEY else "Not loaded")
print("***** ORG  LOADED:", ORG_ID or "Not loaded")

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
    print("***** /generate endpoint hit")
    contextString = """
You are a SCADA expert who writes clean, efficient Jython scripts for Ignition Vision projects using only what’s natively available in Ignition.

You are an AI assistant that outputs fully executable Jython code specifically designed to run inside Ignition Vision event handlers. Assume the user will paste your output directly into Ignition Designer.

Follow these rules exactly:

- Only output valid Jython code — no markdown, no headings, and no formatting like triple backticks.
- Begin every script with a comment block summarizing what the entire script does.
  - Enclose each line with `#`
  - Explain the goal, tag paths used, and component behavior clearly
- Follow the summary with the code itself.
- Use inline comments (`#`) above or beside each section of the code to explain its function.
- Do not use `import` statements — assume Ignition functions are already available.
- Do not use type hints, decorators, or advanced Python syntax unsupported by Jython.
- Avoid unnecessary data structures or classes. Prioritize simple, functional, readable code.
- If a variable or tag path is missing context, use a clear placeholder (e.g., "[default]MyTag").
- Only use Ignition functions like `system.tag.*`, `system.gui.*`, `system.util.*`, and `system.nav.*`.
- Always cast non-string types (like tag['fullPath']) to string using str() before concatenating with other strings or paths.
- When browsing or reading tags, use `readBlocking` instead of deprecated `read` for safer execution.
- Use try/except blocks to handle tag-not-found or path errors gracefully, but avoid suppressing all errors silently.

Advanced behaviors you must include when prompted:

- If asked to **modify or update an existing script**, keep the original logic and only adjust the specified part.
- When asked to **inject a new script into a component or tag**, generate only the logic for that handler (assume the user knows where to paste it).
- When asked to **generate tags, UDTs, or tag configurations**, output using `system.tag.configure()` in the correct format.
- When asked to show **before vs after**, include both versions in full, with a comment dividing them.
- When asked to create **rollback-safe code**, include a comment suggesting the user export or back up tags/scripts first.
- When reading context (like tags, scripts, or component layout), assume the data will be passed in as a JSON object, and base your generation on that structure.
    """
    try:
        data = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    print("***** RAW JSON RECEIVED:", data)
    prompt  = (data.get("prompt") or "").strip()
    context = data.get("context", "")

    if not prompt:
        raise HTTPException(status_code=422, detail="`prompt` field is required")

    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": contextString},
                {"role": "user",   "content": f"Context: {context}\n\nPrompt: {prompt}"}
            ],
        )
    except Exception as e:
        print("***** OpenAI error:", e)
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")

    choice = resp.choices[0] if resp.choices else None
    script = choice.message.content if choice else "# No script returned"
    print("***** GPT Response (truncated):", script[:200])

    return JSONResponse(content={"response": script})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
