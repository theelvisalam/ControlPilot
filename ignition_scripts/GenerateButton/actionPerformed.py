import system
from java.lang import String
from java.net import URL
from java.io import BufferedReader, InputStreamReader

# 1) Grab your Prompt and Preview components
container  = event.source.parent
promptBox  = container.getComponent("PromptArea")
previewBox = container.getComponent("PreviewArea")

# 2) Read and sanitize user input
prompt = promptBox.text.strip()
if not prompt or prompt == "Type your prompt here...":
    system.gui.warningBox("Please enter a prompt first.", "ControlPilot")
else:
    try:
        # 3) Build JSON payload
        payloadDict = {
            "prompt": prompt,
            "context": ""   # or pull from another component if you need dynamic context
        }
        jsonPayload = system.util.jsonEncode(payloadDict)

        # 4) Open an HttpURLConnection
        url  = URL("http://localhost:5000/generate")  # adjust host/port if needed
        conn = url.openConnection()
        conn.setRequestMethod("POST")
        conn.setDoOutput(True)
        conn.setRequestProperty("Content-Type", "application/json")

        # 5) Write the JSON to the request body
        outStream = conn.getOutputStream()
        outStream.write(String(jsonPayload).getBytes("UTF-8"))
        outStream.flush()
        outStream.close()

        # 6) Read the response back in
        reader = BufferedReader(InputStreamReader(conn.getInputStream(), "UTF-8"))
        responseLines = []
        line = reader.readLine()
        while line is not None:
            responseLines.append(line)
            line = reader.readLine()
        reader.close()

        rawResponse = "".join(responseLines)
        # 7) JSON-decode and display
        result = system.util.jsonDecode(rawResponse)
        scriptText = result.get("response", "# No script returned")
        previewBox.text = scriptText

    except Exception as e:
        system.gui.errorBox("Error communicating with backend:\n\n" + str(e), "ControlPilot")