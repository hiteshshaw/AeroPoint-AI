"""
Offline Voice Listener:
Continuously listens on a low-priority daemon thread using sounddevice & Vosk.
Optimized for 16kHz native model frequency with software gain and instant partial-phrase detection.
"""
import os
import sys
import json
import queue
import threading
import numpy as np
import sounddevice as sd

try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 170)
except Exception:
    tts_engine = None

try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    Model = None
    KaldiRecognizer = None


class VoiceListener(threading.Thread):
    def __init__(self, intent_engine, model_path: str = "model"):
        super().__init__(daemon=True)
        self.intent_engine = intent_engine
        self.audio_queue = queue.Queue()
        self.is_running = False
        self.model_path = model_path
        self.recognizer = None
        self.sample_rate = 16000
        self.latest_heard = ""
        self.gain = 3.0  # 3x software boost for quiet laptop mics

    def speak(self, text: str):
        """Offline spoken voice response in a separate thread so audio stream doesn't block."""
        if not tts_engine or not text:
            return
        def _speak_worker():
            try:
                # Re-initialize or run safely
                engine = pyttsx3.init()
                engine.setProperty('rate', 170)
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=_speak_worker, daemon=True).start()

    def _audio_callback(self, indata, frames, time_info, status):
        """Buffer callback with digital gain amplification."""
        if status:
            pass
        # Apply digital gain to boost low laptop mic levels
        audio_data = np.frombuffer(indata, dtype=np.int16).astype(np.float32)
        audio_data = np.clip(audio_data * self.gain, -32768, 32767).astype(np.int16)
        self.audio_queue.put(audio_data.tobytes())

    def run(self):
        if not Model:
            print("[VOICE] Vosk library is not loaded. Voice listener idle.")
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_full_path = os.path.join(base_dir, self.model_path)

        if os.path.exists(model_full_path):
            model = Model(model_full_path)
        elif os.path.exists(self.model_path):
            model = Model(self.model_path)
        else:
            try:
                model = Model(model_name="vosk-model-small-en-us")
            except Exception as e:
                print(f"[VOICE] Local voice model not found at {model_full_path} ({e}).")
                return

        # 16000 Hz is the exact native acoustic frequency of Vosk models
        self.recognizer = KaldiRecognizer(model, 16000.0)
        self.is_running = True
        print("[VOICE] Offline Voice Engine is Active & Listening at 16kHz (Boosted)...")

        try:
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=4000,
                dtype='int16',
                channels=1,
                callback=self._audio_callback
            ):
                while self.is_running:
                    data = self.audio_queue.get()
                    # 1. Check Full Sentence / Silence
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip()
                        if text:
                            self._handle_voice_text(text)
                    else:
                        # 2. Check Partial Result for instantaneous zero-delay triggering
                        partial = json.loads(self.recognizer.PartialResult())
                        partial_text = partial.get('partial', '').strip()
                        if partial_text:
                            # If a key trigger command is clearly detected in partial audio
                            for trigger in ['open youtube', 'open google', 'open chrome', 'mute',
                                            'volume up', 'volume down', 'screenshot', 'lock',
                                            'desktop', 'stop assistant', 'exit assistant']:
                                if trigger in partial_text:
                                    self._handle_voice_text(partial_text)
                                    self.recognizer.Reset()
                                    break
        except Exception as e:
            print(f"[VOICE ERROR] Microphone stream failed: {e}")

    def _handle_voice_text(self, text: str):
        print(f"\n🎤 [VOICE COMMAND HEARD]: '{text}'")
        self.latest_heard = text
        action_res = self.intent_engine.execute_command(text)
        if action_res.get('message'):
            print(f"⚡ [ACTION]: {action_res['message']}")
            self.speak(action_res['message'])

    def stop(self):
        self.is_running = False
