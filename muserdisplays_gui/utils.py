# Example: A function to center text, or animate displays
def center_text(text: str, width: int) -> str:
    if len(text) >= width:
        return text[:width]
    padding = (width - len(text)) // 2
    return ' ' * padding + text + ' ' * (width - len(text) - padding)

# You could also put the console clearing function here if it's more complex
# Or any common character rendering logic that might be shared.
