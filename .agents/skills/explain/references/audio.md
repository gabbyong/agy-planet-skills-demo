# Audio & Voiceover Reference

Use this reference to generate voiceover narration and audio explainers using Gemini TTS.

---

## What Good Looks Like

- **Voice Choice**: Use `Orus` as the standard voice model for crisp, natural delivery.
- **Engaging, Excited Tone**: Prompt the TTS model for genuine curiosity, enthusiasm, and dynamic cadence—like an excited science communicator (e.g., 3Blue1Brown). Avoid dry or robotic monologues.
- **Audio-First Pacing**: Always generate audio and measure its duration *before* assembling animations so scenes synchronize smoothly.

---

## Generating Audio with Gemini TTS

Always use the Google GenAI Interactions API (`client.interactions.create`) with `model="gemini-3.1-flash-tts-preview"` (do NOT use `models.generate_content`, which is restricted to text completions).

```python
import os
import wave
import base64
import subprocess
from google import genai

def generate_narration(text: str, output_path: str = "/tmp/narration.wav", voice: str = "Orus") -> float:
    """Generates speech audio with Gemini TTS and returns duration in seconds."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    interaction = client.interactions.create(
        model="gemini-3.1-flash-tts-preview",
        input=f"Read with genuine excitement, curiosity, and engaging technical pacing like an enthusiastic 3Blue1Brown explainer: {text}",
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": voice}
            ]
        }
    )

    pcm_data = base64.b64decode(interaction.output_audio.data)
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_data)

    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", output_path],
        capture_output=True, text=True
    )
    duration = float(res.stdout.strip())
    print(f"Generated narration ({duration:.2f}s): {output_path}")
    return duration
```

---

## Measuring Duration & Concatenation

To inspect exact durations with `ffprobe`:

```bash
# Check exact duration in seconds
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /tmp/narration.wav
```

To concatenate multiple segment WAVs/MP3s into a seamless narration track:

```bash
cat << 'EOF' > /tmp/audio_list.txt
file '/tmp/seg1.mp3'
file '/tmp/seg2.mp3'
EOF

ffmpeg -y -f concat -safe 0 -i /tmp/audio_list.txt -c copy /tmp/full_narration.mp3
```
