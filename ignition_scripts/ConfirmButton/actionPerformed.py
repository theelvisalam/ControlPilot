script = event.source.parent.getComponent("PreviewArea").text

if script.strip():
    try:
        exec(script)
        system.gui.messageBox("Script executed successfully.")
    except Exception as e:
        system.gui.errorBox("Execution failed: " + str(e))
else:
    system.gui.warningBox("No script to execute.")