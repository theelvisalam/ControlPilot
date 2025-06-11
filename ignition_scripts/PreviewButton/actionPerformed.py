script = event.source.parent.getComponent("PreviewArea").text

if script.strip():
    system.gui.messageBox(script, "Preview")
else:
    system.gui.warningBox("Nothing to preview. Click 'Generate' first.")