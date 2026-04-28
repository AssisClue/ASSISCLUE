MIC -> TEXT tunables (current values in code), grouped:

INPUT SOURCE / MIC

INPUTFEED_SAMPLE_RATE = 16000
INPUTFEED_CHANNELS = 1
sample_width = 2
INPUTFEED_FRAMES_PER_BUFFER = 1024
INPUTFEED_INPUT_GAIN = 1.2
windows_mic_device_name = "AudioPro X5"
INPUTFEED_SOURCE_BACKEND = "windows_wasapi_mic"
RNNOISE

INPUTFEED_ENABLE_RNNOISE = 1 (true)
rnnoise_bypass_min_raw_rms = 180
rnnoise_bypass_max_ratio = 0.35
FASTER WHISPER

STT_MODEL = "medium"
device = "cpu"
STT_COMPUTE_TYPE = "int8"
STT_LANGUAGE = "en"
STT_BEAM_SIZE = 3
STT_VAD_FILTER = false
condition_on_previous_text = false
word_timestamps = true
CHUNK / TIMING

STT_CHUNK_MS = 1000
CHUNK_SECONDS = 1.0 (from max(STT_CHUNK_MS,250)/1000)
INPUTFEED_DEDUP_SECONDS = 4
SILERO VAD GATE

INPUTFEED_ENABLE_SILERO_VAD = true
INPUTFEED_MIN_RMS = 180
INPUTFEED_SILERO_THRESHOLD = 0.50
INPUTFEED_SILERO_MIN_SILENCE_MS = 250
INPUTFEED_SILERO_SPEECH_PAD_MS = 80
INPUTFEED_SILERO_MIN_SPEECH_MS = 450
INPUTFEED_SILERO_MIN_SEGMENTS = 1
STREAMING MODE

INPUTFEED_USE_STREAMING = false
INPUTFEED_STREAM_STEP_SECONDS = 1.0
INPUTFEED_STREAM_OVERLAP_SECONDS = 0.25
INPUTFEED_STREAM_MAX_BUFFER_SECONDS = 3.0
INPUTFEED_STREAM_COMMIT_STABLE_PASSES = 2
INPUTFEED_STREAM_RECENT_SEGMENT_COUNT = 1
SOURCE LABELS / IDs

TRANSCRIPT_SESSION_ID = "session_%Y%m%d_%H%M%S" (auto-generated if not set)
TRANSCRIPT_SOURCE_NAME = "audio_input"
TRANSCRIPT_SOURCE_TYPE = "audio_stream"
RELATED (GLOBAL LIVE MIC/STT in app/settings/audio_settings.py)

stt_language = "en"
stt_device = "auto"
stt_compute_type = "auto"
stt_beam_size = 1
stt_live_enabled = true
stt_live_source = "mic"
stt_live_chunk_seconds = 1.4
stt_live_chunk_overlap_seconds = 0.35
stt_live_max_queue_size = 6
stt_live_frames_per_buffer = 1024
stt_live_input_gain = 2.1
stt_live_consumer_poll_seconds = 0.05
stt_live_silence_finalize_seconds = 0.8
stt_live_max_turn_seconds = 8.0
stt_live_voice_peak_dbfs = -72.0
stt_live_min_confidence = 0.2
stt_live_min_letters = 3
stt_live_min_words = 1
stt_live_max_nonalpha_ratio = 0.7
stt_live_vad_style_gate_enabled = true
stt_live_voice_start_min_peak_dbfs = -71.0
stt_live_voice_continue_min_peak_dbfs = -78.0
stt_live_voice_start_min_confidence = 0.22
stt_live_voice_start_chunks_required = 1
stt_live_voice_end_silence_seconds = 0.9
windows_input_device_name = ""
windows_mic_device_name = "AudioPro X5"
windows_loopback_enabled = true
windows_exclusive_mode = false
stt_fallback_to_wav_file = true
RELATED (TRANSCRIPT_SOURCE isolated path)

source_type = "mic"
windows_input_device_name = ""
windows_mic_device_name = ""
sample_rate = 16000
channels = 1
frames_per_buffer = 1024
input_gain = 1.0
capture_chunk_seconds = 0.3
voice_peak_dbfs = -72.0
min_voice_ratio_to_transcribe = 0.0
chunk_seconds = 1.4
overlap_seconds = 0.35
model_name = "medium"
language = "en"
compute_type = "auto"
vad_filter = true
beam_size = 1
min_confidence = 0.0