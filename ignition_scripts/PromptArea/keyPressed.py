if event.keyCode == event.VK_ENTER:
    prompt = event.source.text
    if prompt.strip() and prompt != "Type your prompt here...":
        try:
            script = controlpilot.generate.generate(prompt)
            event.source.parent.getComponent("PreviewArea").text = script
        except Exception as e:
            system.gui.errorBox("Error generating script: " + str(e), "ControlPilot")
        event.source.text = ""  # Clear after submitting
        event.consume()  # Prevent Enter from making a new line