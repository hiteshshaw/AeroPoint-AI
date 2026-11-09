"""
High-Accuracy Offline Voice Listener:
Accumulates full phrases until a natural silence pause (0.7s) before transcribing.
Never cuts words like 'open notepad' in half.
"""
import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

COMMAND_PROMPT = "Open YouTube, Open Google, Open Chrome, Open Notepad, Open Calculator, Open Settings, Type, Write, Enter, Backspace, Save, Mute, Volume Up, Volume Down, Volume Full, Play, Pause, Next, Previous, Screenshot, Desktop, Close Window, Lock."


def get_active_microphone():
    """Prefers connected headsets (e.g. Rockerz 411) or default active device."""
    headset_idx = None
    default_idx = sd.default.device[0]

    for idx, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0:
            name = d['name'].lower()
            if any(k in name for k in ['rockerz', 'headset', 'bluetooth']):
                if headset_idx is None:
                    headset_idx = idx

    selected = headset_idx if headset_idx is not None else default_idx
    selected_name = sd.query_devices(selected)['name']
    return selected, selected_name


class WhisperVoiceListener(threading.Thread):
    def __init__(self, intent_engine, model_size: str = "base.en", sample_rate: int = 16000, device_index=None):
        super().__init__(daemon=True)
        self.intent_engine = intent_engine
        self.sample_rate = sample_rate
        self.model_size = model_size
        self.device_index = device_index
        self.is_running = False
        self.latest_heard = ""
        self.last_command_time = 0
        self.model = None

    def run(self):
        print(f"[VOICE] Initializing Whisper '{self.model_size}' Phrase Listener...")
        try:
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        except Exception as e:
            print(f"[VOICE ERROR] Whisper init failed: {e}")
            return

        if self.device_index is None:
            self.device_index, device_name = get_active_microphone()
        else:
            device_name = sd.query_devices(self.device_index)['name']

        print(f"[VOICE] Connected to: [{self.device_index}] '{device_name}'")
        print("[VOICE] Full-Phrase Listener is ACTIVE & READY!")

        self.is_running = True
        audio_buffer = []
        buffer_lock = threading.Lock()
        chunk_size = int(self.sample_rate * 0.1)  # 100ms chunks

        is_speaking = False
        silence_start = None
        speech_start_time = None

        def audio_callback(indata, frames, time_info, status):
            if self.is_running:
                with buffer_lock:
                    audio_buffer.extend(indata.flatten().tolist())

        try:
            with sd.InputStream(
                device=self.device_index,
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=chunk_size,
                callback=audio_callback
            ):
                while self.is_running:
                    time.sleep(0.08)

                    with buffer_lock:
                        if len(audio_buffer) < chunk_size * 2:
                            continue
                        recent_chunk = np.array(audio_buffer[-chunk_size * 2:], dtype=np.float32)

                    rms = float(np.sqrt(np.mean(recent_chunk**2)))
                    now = time.time()

                    # Voice Activity Detection (RMS > 0.003 is human speech on Rockerz 411)
                    if rms > 0.0025:
                        if not is_speaking:
                            is_speaking = True
                            speech_start_time = now
                        silence_start = None
                    elif is_speaking:
                        if silence_start is None:
                            silence_start = now
                        # When user has stopped speaking for 0.65s OR reached max phrase duration (4s)
                        elif (now - silence_start > 0.65) or (now - speech_start_time > 4.0):
                            # Grab full phrase audio
                            with buffer_lock:
                                full_phrase = np.array(audio_buffer, dtype=np.float32)
                                audio_buffer.clear()

                            is_speaking = False
                            silence_start = None
                            speech_start_time = None

                            # Minimum 0.3s of audio
                            if len(full_phrase) > int(self.sample_rate * 0.3):
                                self._transcribe_phrase(full_phrase)

                    # Prevent unbounded buffer growth during idle silence
                    if not is_speaking:
                        with buffer_lock:
                            if len(audio_buffer) > int(self.sample_rate * 0.5):
                                del audio_buffer[:len(audio_buffer) - int(self.sample_rate * 0.3)]

        except Exception as e:
            print(f"[VOICE STREAM ERROR]: {e}")

    def _transcribe_phrase(self, audio_data: np.ndarray):
        try:
            segments, _ = self.model.transcribe(
                audio_data,
                initial_prompt=COMMAND_PROMPT,
                vad_filter=True,
                language="en",
                beam_size=1
            )
            text = " ".join([s.text for s in segments]).strip().lower()
            for char in [".", ",", "!", "?", "-", "'", '"']:
                text = text.replace(char, "")

            if text:
                now = time.time()
                if text != self.latest_heard or (now - self.last_command_time) > 1.2:
                    self.latest_heard = text
                    self.last_command_time = now
                    print(f"\n🎤 [VOICE PHRASE HEARD]: '{text}'")
                    res = self.intent_engine.execute_command(text)
                    if res.get('message'):
                        print(f"⚡ [ACTION]: {res['message']}")
        except Exception as ex:
            print(f"[VOICE EXCEPTION]: {ex}")

    def stop(self):
        self.is_running = False
