# Audio & Voiceover Reference

Use this reference to generate voiceover narration and audio explainers using Gemini TTS.

---

## What Good Looks Like

- **Voice Choice**: Use `Orus` as the standard voice model for authoritative, crisp, and natural technical delivery.
- **Pacing**: Spoken scripts should be deliberate and unhurried, matched to the conceptual weight of the material.
- **Modularity**: Generate audio in distinct conceptual segments so animation keyframes or page sections can synchronize with spoken milestones.

---

## Generating Audio with Gemini TTS

Use the Google GenAI Interactions API with `model="gemini-3.1-flash-tts-preview"`, `voice="Orus"`, and write out the raw PCM data using Python's standard `wave` library:

```python
import os
import wave
import base64
from google import genai

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

interaction = client.interactions.create(
    model="gemini-3.1-flash-tts-preview",
    input="Read with clear authority and natural pacing: Behold: SeeFood. A Convolutional Neural Network classifying hotdogs.",
    response_format={"type": "audio"},
    generation_config={
        "speech_config": [
            {"voice": "Orus"}
        ]
    }
)

pcm_data = base64.b64decode(interaction.output_audio.data)
wave_file("/tmp/narration.wav", pcm_data)
```

---

## Measuring Duration & Concatenation

To synchronize audio with animations or interactive web steps, inspect exact durations with `ffprobe`:

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
