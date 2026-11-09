"""
Voice Diagnostic & Live Command Execution Tool:
Transcribes full speech phrases using Faster-Whisper 'base.en' and executes commands live!
"""
import sys
import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from controller.os_actions import SystemController
from voice.speech_engine import VoiceIntentEngine
from voice.whisper_listener import get_active_microphone, COMMAND_PROMPT

def test_voice():
    print("=" * 60)
    print("  PHRASE-BASED VOICE CONTROLLER & DIAGNOSTIC TOOL")
    print("=" * 60)

    # Initialize System & Intent Engine
    sys_ctrl = SystemController()
    intent_engine = VoiceIntentEngine(system_controller=sys_ctrl)

    # Detect mic
    print("[INFO] Scanning for active audio inputs...")
    mic_idx, mic_name = get_active_microphone()
    print(f"\n[TARGET MIC CONNECTED]: [{mic_idx}] {mic_name}")

    print("\n[INFO] Loading Faster-Whisper 'base.en' on CPU...")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    print("[SUCCESS] Speech Engine Ready & Armed with OS Automation!")

    sample_rate = 16000
    chunk_size = int(sample_rate * 0.1)  # 100ms
    audio_buffer = []
    buffer_lock = threading.Lock()
    is_running = True
    last_text = ""
    last_command_time = 0

    is_speaking = False
    silence_start = None
    speech_start_time = None

    def audio_callback(indata, frames, time_info, status):
        if is_running:
            with buffer_lock:
                audio_buffer.extend(indata.flatten().tolist())

    print(f"\n[READY] Speak full phrases into '{mic_name}':")
    print("  👉 Say: 'open notepad' (or simply 'notepad')")
    print("  👉 Say: 'type hello how are you'")
    print("  👉 Say: 'enter'")
    print("  👉 Say: 'open youtube' (or simply 'youtube')")
    print("  👉 Say: 'volume up' or 'mute'")
    print("  👉 Say: 'stop assistant' to quit")
    print("Press Ctrl+C in terminal to stop.\n")

    try:
        with sd.InputStream(
            device=mic_idx,
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            blocksize=chunk_size,
            callback=audio_callback
        ):
            while True:
                time.sleep(0.08)

                with buffer_lock:
                    if len(audio_buffer) < chunk_size * 2:
                        continue
                    recent_chunk = np.array(audio_buffer[-chunk_size * 2:], dtype=np.float32)

                rms = float(np.sqrt(np.mean(recent_chunk**2)))
                now = time.time()

                bar_len = min(25, int(rms * 1500))
                bar = "█" * bar_len + "░" * (25 - bar_len)
                status_lbl = "Speaking..." if is_speaking else "Listening..."
                print(f"  [{bar}] Signal: {rms*1000:.1f} | {status_lbl}", end='\r', flush=True)

                # Voice Activity Detection
                if rms > 0.0025:
                    if not is_speaking:
                        is_speaking = True
                        speech_start_time = now
                    silence_start = None
                elif is_speaking:
                    if silence_start is None:
                        silence_start = now
                    # Wait for 0.65s silence pause before cutting the audio!
                    elif (now - silence_start > 0.65) or (now - speech_start_time > 4.0):
                        with buffer_lock:
                            full_phrase = np.array(audio_buffer, dtype=np.float32)
                            audio_buffer.clear()

                        is_speaking = False
                        silence_start = None
                        speech_start_time = None

                        if len(full_phrase) > int(sample_rate * 0.3):
                            print("\n[TRANSCRIBING FULL PHRASE]...")
                            segments, _ = model.transcribe(
                                full_phrase,
                                initial_prompt=COMMAND_PROMPT,
                                vad_filter=True,
                                language="en",
                                beam_size=1
                            )
                            text = " ".join([s.text for s in segments]).strip().lower()
                            for char in [".", ",", "!", "?", "-", "'", '"']:
                                text = text.replace(char, "")

                            if text:
                                print(f"🎤 [FULL PHRASE HEARD]: '{text}'")
                                last_text = text
                                last_command_time = now

                                res = intent_engine.execute_command(text)
                                if res.get('message'):
                                    print(f"🚀 [SUCCESS]: {res['message']}\n")

                if not is_speaking:
                    with buffer_lock:
                        if len(audio_buffer) > int(sample_rate * 0.5):
                            del audio_buffer[:len(audio_buffer) - int(sample_rate * 0.3)]

    except KeyboardInterrupt:
        print("\n[DIAGNOSTIC] Voice controller stopped.")
    except Exception as e:
        print(f"\n[ERROR] Microphone stream failed: {e}")

if __name__ == '__main__':
    test_voice()
