# Ignition Vision Button – onActionPerformed event

import system
from java.lang import String
from java.net import URL
from java.io import BufferedReader, InputStreamReader

# [1] Get components
container   = event.source.parent
promptBox   = container.getComponent("PromptArea")
previewBox  = container.getComponent("PreviewArea")

# [2] Read and validate prompt
prompt = promptBox.text.strip()
if not prompt or prompt == "Type your prompt here...":
    system.gui.warningBox("Please enter a prompt first.", "ControlPilot")
else:
    try:
        # [3] Find the window root and name
        comp = event.source
        while getattr(comp, "getParent", None) and comp.getParent() is not None:
            comp = comp.getParent()
        try:
            windowName = comp.getName()
        except:
            windowName = str(comp)

        # [4] Collect component info
        component     = event.source
        componentName = component.name
        componentType = component.__class__.__name__

        # [5] Browse tags
        try:
            tagResults = system.tag.browse("[default]", {"recursive": True}).getResults()
            visibleTags = [str(t['fullPath']) for t in tagResults if not t['hasChildren']]
        except:
            visibleTags = []

        # [6] Read recentActions (optional)
        try:
            recentActions = system.tag.readBlocking(["[Client]ControlPilot/RecentActions"])[0].value
        except:
            recentActions = ""

        # [7] Build payload
        payloadDict = {
            "prompt": prompt,
            "context": {
                "windowName":    windowName,
                "componentName": componentName,
                "componentType": componentType,
                "visibleTags":   visibleTags,
                "recentActions": recentActions
            }
        }
        jsonPayload = system.util.jsonEncode(payloadDict)

        # [8] Send HTTP POST
        url  = URL("http://localhost:5000/generate")
        conn = url.openConnection()
        conn.setRequestMethod("POST")
        conn.setDoOutput(True)
        conn.setRequestProperty("Content-Type", "application/json")

        outStream = conn.getOutputStream()
        outStream.write(String(jsonPayload).getBytes("UTF-8"))
        outStream.flush()
        outStream.close()

        # [9] Read response and display
        reader = BufferedReader(InputStreamReader(conn.getInputStream(), "UTF-8"))
        responseLines = []
        line = reader.readLine()
        while line is not None:
            responseLines.append(line)
            line = reader.readLine()
        reader.close()

        rawResponse = "".join(responseLines)
        result = system.util.jsonDecode(rawResponse)
        previewBox.text = result.get("response", "# No script returned")

    except Exception as e:
        system.gui.errorBox("Error communicating with backend:\n\n" + str(e), "ControlPilot")