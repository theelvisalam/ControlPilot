from fastapi import FastAPI, Request
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")

print("KEY LOADED:", openai.api_key)
print("ORG  LOADED:", openai.organization)

app = FastAPI()

@app.post("/generate")
async def generate_code(req: Request):
    print("🔥 /generate endpoint hit")  # Debug print

    try:
        # Parse incoming JSON body
        data = await req.json()
        print("✅ RAW JSON RECEIVED:", data)

        prompt = data.get("prompt", "")
        context = data.get("context", "")
        # propertyname = data.get("propertyname", "")

        if not prompt.strip():
            return {"response": "⚠️ No prompt provided."}

        # Call OpenAI Chat API
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a SCADA expert who writes Jython scripts for Ignition."},
                {"role": "user", "content": f"Context: {context}\n\nPrompt: {prompt}"}
                
            ]
        )

        script = response.choices[0].message.content
        print("✅ GPT Response:", script[:200])  # Print first 200 chars

        return {"response": script}

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"response": f"ERROR: {str(e)}"}
