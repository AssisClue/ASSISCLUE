from __future__ import annotations

# Public TTS import target.
# External modules should import from here, not from tts_bridge.py directly.
from .tts_bridge import synthesize_and_play_speech

__all__ = ["synthesize_and_play_speech"]