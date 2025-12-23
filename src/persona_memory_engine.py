from collections import Counter
import datetime

class PersonaMemoryEngine:
    """
    Observes styled output, extracts stylistic features, and updates PersonaContext adaptively.
    Reinforces consistent patterns and gradually shifts style based on user interaction.
    """
    def __init__(self, persona_context):
        self.persona_context = persona_context

    def observe_and_update(self, styled_output, user_message=None):
        now = datetime.datetime.now().isoformat()
        style, tone, signature = self._extract_features(styled_output)
        # Only update if we have a styled output
        if style:
            self.persona_context.style_history.append((now, style))
        if tone:
            self.persona_context.tone_history.append((now, tone))
        if signature:
            self.persona_context.signature_patterns_used.append((now, signature))
        # Adaptive rules
        self._reinforce_tone()
        self._strengthen_signature()
        if user_message:
            self._adapt_to_user(user_message)
        self._maintain_coherence()
        self.persona_context.persona_evolution_state["last_update"] = now
        # Debug output for test diagnosis
        print("[MEMORY ENGINE DEBUG] Updated PersonaContext:")
        print(f"  style_history: {self.persona_context.style_history}")
        print(f"  tone_history: {self.persona_context.tone_history}")
        print(f"  signature_patterns_used: {self.persona_context.signature_patterns_used}")
        print(f"  persona_evolution_state: {self.persona_context.persona_evolution_state}")
        print(f"  voice_style: {self.persona_context.voice_style}")
        print(f"  tone_modifiers: {self.persona_context.tone_modifiers}")

    def _extract_features(self, styled_output):
        # Robustly extract style, tone, and signature from output
        import re
        style = None
        tone = []
        signature = None
        if not styled_output or not isinstance(styled_output, str):
            return style, tone, signature
        match = re.match(r"\[(.*?)\|(.*?)\](.*)", styled_output)
        if match:
            style = match.group(1).strip().lower()  # normalize to lowercase
            tone = [t.strip().lower() for t in match.group(2).split(",") if t.strip()]
            rest = match.group(3)
            # Look for signature lines, e.g., '- Sincerely, MetaPersona' or similar
            import re as _re
            sig_match = _re.search(r"(-\s*[^\n]+)", rest)
            if sig_match:
                signature = sig_match.group(1).strip()
        # Fallback: if no match, try after newline as before
        if not signature and "\n" in styled_output:
            sig_candidate = styled_output.split("\n", 1)[1].strip()
            if len(sig_candidate) > 0 and (sig_candidate.startswith("-") or "," in sig_candidate or "MetaPersona" in sig_candidate):
                signature = sig_candidate
        return style, tone, signature

    def _reinforce_tone(self):
        # Find most frequent tones and reinforce
        tones = [tone for _, tlist in self.persona_context.tone_history for tone in tlist]
        if tones:
            most_common = Counter(tones).most_common(1)[0][0]
            if most_common not in self.persona_context.tone_modifiers:
                self.persona_context.tone_modifiers.append(most_common)

    def _strengthen_signature(self):
        # If a signature is used frequently, add to signature_phrasing
        sigs = [sig for _, sig in self.persona_context.signature_patterns_used if sig]
        if sigs:
            most_common = Counter(sigs).most_common(1)[0][0]
            if most_common and most_common not in self.persona_context.signature_phrasing:
                self.persona_context.signature_phrasing.append(most_common)

    def _adapt_to_user(self, user_message):
        # If user writes more formally, agent shifts slightly formal
        import re
        print(f"[ADAPT DEBUG] _adapt_to_user called with user_message: {user_message!r}")
        if user_message:
            # Lowercase and tokenize, stripping punctuation
            msg = user_message.lower()
            words = re.findall(r"\b\w+\b", msg)
            formal_keywords = ["therefore", "hence", "thus", "regarding", "consequently"]
            casual_keywords = ["hey", "yo", "lol", "cool", "ok"]
            if any(word in words for word in formal_keywords):
                print("[ADAPT DEBUG] Detected formal keyword, setting voice_style to 'formal'")
                self.persona_context.user_preference_inferences["formality"] = "formal"
                self.persona_context.voice_style = "formal"
            elif any(word in words for word in casual_keywords):
                print("[ADAPT DEBUG] Detected casual keyword, setting voice_style to 'casual'")
                self.persona_context.user_preference_inferences["formality"] = "casual"
                self.persona_context.voice_style = "casual"
            else:
                print("[ADAPT DEBUG] No adaptation keyword detected; voice_style unchanged.")

    def _maintain_coherence(self):
        # Prevent abrupt style changes: smooth transitions
        if len(self.persona_context.style_history) > 2:
            last_style = self.persona_context.style_history[-1][1]
            prev_style = self.persona_context.style_history[-2][1]
            if last_style and prev_style and last_style != prev_style:
                # Only allow change if stability is low
                if self.persona_context.persona_evolution_state.get("stability", 1.0) > 0.5:
                    # Revert to previous style
                    self.persona_context.style_history[-1] = (self.persona_context.style_history[-1][0], prev_style)
                    self.persona_context.voice_style = prev_style
                    self.persona_context.persona_evolution_state["stability"] *= 0.95
                else:
                    self.persona_context.persona_evolution_state["stability"] *= 1.05
