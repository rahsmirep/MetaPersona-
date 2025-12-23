class PersonaStyler:
    """
    Utility to apply persona rules, tone modifiers, and signature phrasing to handler output.
    """
    def __init__(self, persona_context):
        self.persona_context = persona_context

    def style(self, raw_text, mode=None):
        # Always use evolving voice_style for style tag, ignore mode-specific override
        style = self.persona_context.voice_style
        tone = ", ".join(self.persona_context.tone_modifiers)
        phrasing = self.persona_context.signature_phrasing
        # Always include style and tone for memory engine
        styled = f"[{style} | {tone}] {raw_text}"
        # Always include signature phrasing, even if empty (for extraction)
        if phrasing and len(phrasing) > 0:
            styled += "\n" + " ".join(phrasing)
        else:
            styled += "\n"
        return styled

    def evolve(self, feedback):
        # Example: update persona context based on feedback
        if feedback.get("liked_tone"):
            self.persona_context.tone_modifiers.append(feedback["liked_tone"])
        if feedback.get("new_phrase"):
            self.persona_context.add_signature_phrase(feedback["new_phrase"])
