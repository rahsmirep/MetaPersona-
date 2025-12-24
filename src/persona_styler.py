class PersonaStyler:
    """
    Utility to apply persona rules, tone modifiers, and signature phrasing to handler output.
    """
    def __init__(self, persona_context):
        self.persona_context = persona_context

    def style(self, raw_text, mode=None):
        # Safeguard: suppress persona shaping for low-intent/casual/dismissive input or suppression mode
        def is_low_intent(text):
            low_intent_phrases = [
                "nothing lol", "idk", "nah", "don’t care", "don't care", "nope", "whatever", "meh", "shrug"
            ]
            t = text.strip().lower()
            return any(phrase in t for phrase in low_intent_phrases) or len(t) < 4

        suppression = getattr(self.persona_context, 'persona_suppression_mode', False)
        if suppression or is_low_intent(raw_text):
            # Minimal/neutral shaping
            style = "neutral"
            tone = ""
            phrasing = []
        else:
            style = self.persona_context.voice_style
            tone = ", ".join(self.persona_context.tone_modifiers)
            phrasing = self.persona_context.signature_phrasing

        styled = f"[{style} | {tone}] {raw_text}"
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
