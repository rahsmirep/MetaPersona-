# Meeting Listener Quick Start Guide

Get started with Meeting Listener in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- MetaPersona installed and initialized
- Microphone or virtual audio device

## Installation

### 1. Install Meeting Listener Dependencies

```bash
pip install openai-whisper sounddevice numpy prompt_toolkit
```

For GPU acceleration (optional, requires NVIDIA GPU):
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Or install all at once:
```bash
pip install -r requirements-meeting.txt
```

### 2. Verify Installation

```bash
python metapersona.py meeting-setup
```

This will:
- Check all dependencies
- List available audio devices
- Detect virtual audio devices
- Show setup recommendations

## Quick Start

### Option 1: Record with System Microphone

1. **Start recording:**
   ```bash
   python metapersona.py meeting-listen --title "Test Meeting"
   ```

2. **Speak into your microphone** - transcription will appear in real-time

3. **Stop recording:**
   Type `stop` and press Enter

4. **View the results:**
   ```bash
   python metapersona.py meeting-list
   python metapersona.py meeting-show meeting_YYYYMMDD_HHMMSS
   ```

### Option 2: Record Meeting Audio (Recommended)

For capturing actual meeting audio, use a virtual audio device:

#### Windows Setup

1. **Install VB-CABLE:**
   - Download from: https://vb-audio.com/Cable/
   - Install and restart computer

2. **Configure audio:**
   - In your meeting app (Zoom, Teams, etc.), set audio output to "CABLE Input"
   - In MetaPersona, audio will be captured from "CABLE Output"

3. **Start recording:**
   ```bash
   python metapersona.py meeting-listen --title "Team Meeting" --url "https://zoom.us/j/123456789"
   ```

#### macOS Setup

1. **Install BlackHole:**
   ```bash
   brew install blackhole-2ch
   ```

2. **Configure Audio MIDI Setup:**
   - Open Audio MIDI Setup
   - Create Multi-Output Device
   - Select both your speakers and BlackHole

3. **Start recording:**
   ```bash
   python metapersona.py meeting-listen --title "Team Meeting"
   ```

#### Linux Setup

1. **Load PulseAudio loopback:**
   ```bash
   pactl load-module module-loopback
   ```

2. **Start recording:**
   ```bash
   python metapersona.py meeting-listen --title "Team Meeting"
   ```

## Basic Workflow

### 1. Before the Meeting

```bash
# Verify setup
python metapersona.py meeting-setup

# Make sure your audio routing is correct
```

### 2. During the Meeting

```bash
# Start listening
python metapersona.py meeting-listen --title "Project Sync" --url "https://zoom.us/j/123456"

# Available commands:
# - pause: Pause recording
# - resume: Resume recording
# - stop: Stop and save
```

### 3. After the Meeting

```bash
# View all meetings
python metapersona.py meeting-list

# See details and summary
python metapersona.py meeting-show meeting_20241218_143022

# Regenerate summary (if needed)
python metapersona.py meeting-summarize meeting_20241218_143022
```

## Choosing a Whisper Model

The transcription quality and speed depend on the model:

| Model | Speed | Accuracy | RAM | Best For |
|-------|-------|----------|-----|----------|
| tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1GB | Quick tests, short meetings |
| base | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1GB | Most meetings (default) |
| small | ⚡⚡⚡ | ⭐⭐⭐⭐ | ~2GB | Important meetings |
| medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~5GB | Critical meetings, technical content |
| large | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | Highest accuracy needed |

**Usage:**
```bash
python metapersona.py meeting-listen --title "Quick Sync" --model tiny
python metapersona.py meeting-listen --title "Board Meeting" --model medium
```

## Example: Complete Meeting Flow

```bash
# 1. Setup (first time only)
python metapersona.py meeting-setup

# 2. Complete onboarding (for personalized summaries)
python metapersona.py onboard

# 3. Start recording your meeting
python metapersona.py meeting-listen \
  --title "Q4 Planning Meeting" \
  --url "https://zoom.us/j/987654321" \
  --model base

# ... meeting happens, transcription appears in real-time ...

# 4. When done, type: stop

# 5. View the summary
python metapersona.py meeting-show meeting_20241218_143022

# Output:
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Meeting Details                            ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# Meeting: Q4 Planning Meeting
# Duration: 45.2 minutes
# Platform: zoom
#
# Summary:
# Team discussed Q4 objectives, resource allocation,
# and timeline for major initiatives...
#
# Key Points:
#  • Increase focus on customer retention
#  • Allocate 3 engineers to new feature
#  • Launch planned for November 15th
#
# Action Items:
#  • Draft project plan (Owner: Alice, Due: Friday)
#  • Schedule kickoff meeting (Owner: Bob, Due: Monday)
```

## Personalization

For summaries in YOUR style:

1. **Complete onboarding:**
   ```bash
   python metapersona.py onboard
   ```

2. **Initialize your profile:**
   ```bash
   python metapersona.py init
   ```

3. **Record and summarize:**
   ```bash
   python metapersona.py meeting-listen --title "My Meeting"
   # Summaries will now match your communication style!
   ```

## Programmatic Usage

For automation or custom workflows:

```python
from src.meeting_listener import MeetingListener, MeetingSummarizer
from src.llm_provider import get_llm_provider

# Initialize
listener = MeetingListener(
    data_dir='./data/meetings',
    transcription_model='base'
)

# Start recording
meeting_id = listener.start_meeting(
    title="Automated Meeting",
    platform="zoom"
)

# ... meeting happens ...

# Stop and get results
result = listener.stop_meeting()
print(f"Recorded {len(result['transcript']['segments'])} segments")

# Generate summary
llm = get_llm_provider('ollama')
summarizer = MeetingSummarizer(llm_provider=llm)
summary = summarizer.generate_summary(
    listener.get_transcript(meeting_id),
    metadata
)

print(summary.summary)
for item in summary.action_items:
    print(f"  • {item}")
```

## Troubleshooting

### No transcription appearing

1. Check microphone/audio device:
   ```bash
   python metapersona.py meeting-setup
   ```

2. Verify audio is playing (speak or play audio)

3. Check buffer duration (may need to wait 5-10 seconds)

### "Module not found" errors

Install missing dependencies:
```bash
pip install openai-whisper sounddevice numpy prompt_toolkit
```

### Transcription too slow

1. Use a smaller model (`--model tiny` or `--model base`)
2. Enable GPU acceleration
3. Reduce audio quality in code if needed

### Inaccurate transcription

1. Use a larger model (`--model medium` or `--model large`)
2. Ensure good audio quality (reduce background noise)
3. Check language setting if not English

## Next Steps

- **Read full docs:** [MEETING_LISTENER.md](MEETING_LISTENER.md)
- **Run demo:** `python examples/meeting_listener_demo.py`
- **Explore API:** Check `src/meeting_listener.py`
- **Customize:** Extend `MeetingSummarizer` for your needs

## Tips

1. **Test first** with a short test meeting before important meetings
2. **Use virtual audio** for best quality when capturing meeting audio
3. **Choose appropriate model** - balance speed vs accuracy for your use case
4. **Complete onboarding** for personalized summaries
5. **Review summaries** and provide feedback to improve over time

## Getting Help

- Check the troubleshooting section above
- Review [MEETING_LISTENER.md](MEETING_LISTENER.md) for detailed docs
- Run `python metapersona.py meeting-setup` to diagnose issues
- Check that audio devices are properly configured

---

**You're ready to go!** Start with:
```bash
python metapersona.py meeting-listen --title "First Test"
```
