class PersonaContext:
    """
    Stores persona-related attributes for consistent agent style and voice.
    """
    def __init__(self,
                 voice_style: str = "concise",
                 tone_modifiers: list = None,
                 mode_specific_style: dict = None,
                 signature_phrasing: list = None,
                 persona_memory: dict = None,
                 style_history: list = None,
                 tone_history: list = None,
                 signature_patterns_used: list = None,
                 user_preference_inferences: dict = None,
                 persona_evolution_state: dict = None,
                 persona_suppression_mode: bool = False):
        self.voice_style = voice_style
        self.tone_modifiers = tone_modifiers or ["confident"]
        self.mode_specific_style = mode_specific_style or {
            "task": voice_style,
            "reflection": voice_style,
            "recovery": voice_style,
            "onboarding": voice_style
        }
        self.signature_phrasing = signature_phrasing or []
        self.persona_memory = persona_memory or {}
        self.style_history = style_history or []
        self.tone_history = tone_history or []
        self.signature_patterns_used = signature_patterns_used or []
        self.user_preference_inferences = user_preference_inferences or {}
        self.persona_evolution_state = persona_evolution_state or {"stability": 1.0, "last_update": None}
        self.persona_suppression_mode = persona_suppression_mode

    def update_style(self, key, value):
        # If updating voice_style, propagate to mode_specific_style if any mode was using the old voice_style
        if key == 'voice_style':
            old_voice_style = self.voice_style
            setattr(self, key, value)
            for mode, style in self.mode_specific_style.items():
                if style == old_voice_style:
                    self.mode_specific_style[mode] = value
        else:
            setattr(self, key, value)
        if key not in self.persona_memory:
            self.persona_memory[key] = []
        self.persona_memory[key].append(value)

    def get_mode_style(self, mode):
        return self.mode_specific_style.get(mode, self.voice_style)

    def add_signature_phrase(self, phrase):
        if phrase not in self.signature_phrasing:
            self.signature_phrasing.append(phrase)

    def remember(self, key, value):
        self.persona_memory.setdefault(key, []).append(value)
