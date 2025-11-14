# core/ai/summarizer.py
def summarize_text(text, max_length=100):
    """
    Résume un texte long en version courte
    """
    return text[:max_length] + "..." if len(text) > max_length else text

def rephrase_text(text):
    """
    Reformule un texte pour notifications ou interface
    """
    return text