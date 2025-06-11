if event.propertyName == "text":
    maxLength = 300
    if len(event.newValue) > maxLength:
        event.source.text = event.newValue[:maxLength]