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
                {"role": "system", "content": "You are a SCADA expert who writes Jython scripts for Ignition."},
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
