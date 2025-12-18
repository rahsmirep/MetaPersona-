# Meeting Listener Documentation

## Overview

The Meeting Listener module enables MetaPersona to join meetings, capture audio streams, transcribe conversations in real-time, and generate structured summaries with action items in your personal style.

## Features

### Current Features (v1.0)

- **Real-time Audio Capture**: Record audio from meetings using system microphone or virtual audio devices
- **Live Transcription**: Speech-to-text using OpenAI Whisper models (offline)
- **Structured Summaries**: AI-generated summaries with key points, decisions, and action items
- **Personalized Output**: Summaries generated in your communication style using your cognitive profile
- **Meeting Management**: List, view, and search past meeting recordings
- **Multiple Format Support**: Save transcripts as JSON and readable text

### Planned Features (Future)

- **Automatic Meeting Joining**: Join Zoom, Teams, and Google Meet automatically
- **Calendar Integration**: Detect meetings from Google Calendar and Outlook
- **Speaker Diarization**: Identify who said what in the meeting
- **Autonomous Participation**: Respond to questions and take notes on your behalf
- **Multi-Meeting Support**: Attend multiple meetings simultaneously with cloned agents

## Architecture

### Components

```
Meeting Listener System
├── AudioCapture          # Captures audio from meetings
├── TranscriptionEngine   # Converts speech to text (Whisper)
├── MeetingListener       # Main coordinator
├── MeetingSummarizer     # Generates structured summaries
└── Integrations
    ├── VirtualAudioDevice    # Virtual audio routing
    ├── MeetingJoiner         # Auto-join meetings (future)
    └── CalendarIntegration   # Calendar sync (future)
```

### Data Flow

```
Meeting Audio → AudioCapture → Audio Queue
                                    ↓
                              TranscriptionEngine
                                    ↓
                            TranscriptSegments
                                    ↓
                         MeetingListener (Storage)
                                    ↓
                            MeetingSummarizer
                                    ↓
                        Structured Summary + Action Items
```

## Installation

### Required Dependencies

```bash
# Core dependencies
pip install openai-whisper sounddevice numpy prompt_toolkit

# Optional: For GPU acceleration
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Virtual Audio Setup

For best results, install a virtual audio device to capture meeting audio:

**Windows:**
- Download VB-CABLE: https://vb-audio.com/Cable/
- Install and restart your computer
- Set VB-CABLE as your meeting audio output

**macOS:**
- Install BlackHole: `brew install blackhole-2ch`
- Configure Audio MIDI Setup to route meeting audio

**Linux:**
- Load PulseAudio loopback module:
  ```bash
  pactl load-module module-loopback
  ```

### Verify Setup

```bash
python metapersona.py meeting-setup
```

This command will:
- Check all dependencies
- List available audio devices
- Detect virtual audio devices
- Show setup recommendations

## Usage

### Basic Workflow

#### 1. Start Recording a Meeting

```bash
python metapersona.py meeting-listen --title "Team Standup"
```

Interactive options:
- `pause` - Pause recording
- `resume` - Resume recording
- `stop` - Stop and save recording

#### 2. List Recorded Meetings

```bash
python metapersona.py meeting-list
```

#### 3. View Meeting Details

```bash
python metapersona.py meeting-show meeting_20241218_143022
```

Add `--show-transcript` to see full transcript.

#### 4. Generate/Regenerate Summary

```bash
python metapersona.py meeting-summarize meeting_20241218_143022
```

### Advanced Usage

#### Specify Meeting URL

```bash
python metapersona.py meeting-listen \
  --title "Client Demo" \
  --url "https://zoom.us/j/123456789"
```

The system will detect the platform (Zoom, Teams, Meet, etc.).

#### Choose Whisper Model

```bash
# Faster, less accurate
python metapersona.py meeting-listen --title "Quick Meeting" --model tiny

# Default
python metapersona.py meeting-listen --title "Team Meeting" --model base

# More accurate, slower
python metapersona.py meeting-listen --title "Important Meeting" --model medium
```

Available models:
- `tiny` - Fastest, least accurate (~1GB RAM)
- `base` - Good balance (~1GB RAM)
- `small` - Better accuracy (~2GB RAM)
- `medium` - High accuracy (~5GB RAM)
- `large` - Best accuracy (~10GB RAM)

#### Disable Auto-Summary

```bash
python metapersona.py meeting-listen --title "Recording Only" --no-summary
```

Generate summary later:
```bash
python metapersona.py meeting-summarize meeting_20241218_143022
```

## CLI Commands

### `meeting-listen`
Start listening and transcribing a meeting.

**Options:**
- `--title TEXT` - Meeting title (required)
- `--url TEXT` - Meeting URL (optional)
- `--model TEXT` - Whisper model (default: base)
- `--no-summary` - Skip automatic summary generation
- `--data-dir PATH` - Data directory (default: ./data)

**Example:**
```bash
python metapersona.py meeting-listen \
  --title "Q4 Planning" \
  --url "https://meet.google.com/abc-defg-hij" \
  --model medium
```

### `meeting-list`
List all recorded meetings.

**Options:**
- `--limit INTEGER` - Number of meetings to show (default: 10)
- `--data-dir PATH` - Data directory

**Example:**
```bash
python metapersona.py meeting-list --limit 20
```

### `meeting-show`
Show details and summary of a specific meeting.

**Arguments:**
- `MEETING_ID` - Meeting identifier

**Options:**
- `--show-transcript` - Display full transcript
- `--data-dir PATH` - Data directory

**Example:**
```bash
python metapersona.py meeting-show meeting_20241218_143022 --show-transcript
```

### `meeting-summarize`
Generate AI-powered summary for a meeting.

**Arguments:**
- `MEETING_ID` - Meeting identifier

**Options:**
- `--provider TEXT` - LLM provider (default: ollama)
- `--data-dir PATH` - Data directory

**Example:**
```bash
python metapersona.py meeting-summarize meeting_20241218_143022 --provider openai
```

### `meeting-setup`
Setup and verify meeting listener configuration.

**Options:**
- `--data-dir PATH` - Data directory

**Example:**
```bash
python metapersona.py meeting-setup
```

## Data Structures

### Meeting Metadata

```json
{
  "meeting_id": "meeting_20241218_143022",
  "title": "Team Standup",
  "start_time": "2024-12-18T14:30:22",
  "end_time": "2024-12-18T14:45:30",
  "duration_seconds": 908,
  "participants": ["Alice", "Bob", "Charlie"],
  "platform": "zoom",
  "meeting_url": "https://zoom.us/j/123456789"
}
```

### Transcript Segment

```json
{
  "timestamp": "2024-12-18T14:31:15",
  "speaker": "Alice",
  "text": "Let's review the sprint progress.",
  "confidence": 0.95,
  "start_time": 53.2,
  "end_time": 55.8
}
```

### Meeting Summary

```json
{
  "meeting_id": "meeting_20241218_143022",
  "generated_at": "2024-12-18T14:46:00",
  "summary": "Team discussed sprint progress and identified blockers.",
  "key_points": [
    "Sprint is 80% complete",
    "Frontend deployment blocked by API issues",
    "Need to schedule client demo"
  ],
  "decisions": [
    "Move API fix to top priority",
    "Schedule demo for Friday afternoon"
  ],
  "action_items": [
    {
      "task": "Fix API authentication bug",
      "owner": "Bob",
      "due": "Tomorrow"
    },
    {
      "task": "Prepare demo presentation",
      "owner": "Alice",
      "due": "Friday morning"
    }
  ],
  "topics_discussed": [
    "Sprint progress",
    "Technical blockers",
    "Client demo planning"
  ],
  "next_steps": [
    "Daily check-in on API fix",
    "Review demo slides Thursday"
  ],
  "sentiment": "positive"
}
```

## Storage Structure

```
data/meetings/
├── meeting_20241218_143022/
│   ├── metadata.json          # Meeting metadata
│   ├── transcript.json        # Full transcript (structured)
│   ├── transcript.txt         # Readable transcript
│   └── summary.json           # AI-generated summary
├── meeting_20241218_153045/
│   └── ...
└── meeting_20241218_163012/
    └── ...
```

## Integration with MetaPersona

### Using Cognitive Profile

The Meeting Listener integrates with your cognitive profile to generate summaries in YOUR style:

```python
from src.meeting_listener import MeetingSummarizer
from src.cognitive_profile import ProfileManager

# Load your profile
profile_manager = ProfileManager('./data')
cognitive_profile = profile_manager.load_profile()

# Create summarizer with your profile
summarizer = MeetingSummarizer(
    llm_provider=llm,
    cognitive_profile=cognitive_profile
)

# Summary will match your writing style, tone, and preferences
summary = summarizer.generate_summary(transcript, metadata)
```

### Using Adaptive Profile

If you've completed onboarding, summaries adapt to your profession and needs:

```python
from src.user_profiling import UserProfilingSystem

profiling_system = UserProfilingSystem('./data')
user_profile = profiling_system.load_profile('your_user_id')

# Summarizer adapts to:
# - Your industry terminology
# - Your technical level
# - Your preferred communication style
# - Your loaded skill packs
```

## Programmatic API

### Basic Usage

```python
from src.meeting_listener import MeetingListener

# Initialize
listener = MeetingListener(
    data_dir='./data/meetings',
    transcription_model='base',
    auto_summarize=True
)

# Start meeting
meeting_id = listener.start_meeting(
    title="Team Meeting",
    platform="zoom"
)

# ... meeting happens, transcription runs in background ...

# Stop meeting
result = listener.stop_meeting()

print(f"Recorded {len(result['transcript']['segments'])} segments")
print(f"Summary: {result['summary']['summary']}")
```

### Custom Transcription

```python
from src.meeting_listener import TranscriptionEngine

# Initialize engine
engine = TranscriptionEngine(model='medium', language='en')

# Transcribe audio file
result = engine.transcribe_file('meeting_audio.mp3')

print(result['text'])  # Full transcript
for segment in result['segments']:
    print(f"[{segment['start']:.1f}s] {segment['text']}")
```

### Custom Summarization

```python
from src.meeting_listener import MeetingSummarizer
from src.llm_provider import get_llm_provider

# Initialize
llm = get_llm_provider('openai')
summarizer = MeetingSummarizer(llm_provider=llm)

# Generate summary
summary = summarizer.generate_summary(transcript, metadata)

print(f"Summary: {summary.summary}")
print(f"Key points: {summary.key_points}")
print(f"Action items: {summary.action_items}")
```

## Best Practices

### Audio Quality

1. **Use a virtual audio device** for direct audio capture
2. **Set meeting audio output** to virtual device
3. **Test audio levels** before important meetings
4. **Use headphones** to prevent echo/feedback

### Model Selection

- **Quick meetings (<15 min)**: Use `tiny` or `base`
- **Regular meetings**: Use `base` or `small`
- **Important meetings**: Use `medium` or `large`
- **Non-English**: Specify language in code

### Storage Management

- Recordings can be large (especially with larger models)
- Regularly archive old meetings
- Keep summaries, delete full transcripts if needed

```bash
# Archive meetings older than 30 days
find ./data/meetings -type d -mtime +30 -exec tar -czf archive.tar.gz {} \;
```

## Troubleshooting

### No Audio Captured

**Problem**: Recording starts but no transcription appears.

**Solutions:**
1. Check audio device selection
2. Verify virtual audio device is working
3. Test with `meeting-setup` command
4. Increase buffer duration in code

### Transcription Errors

**Problem**: Transcription is inaccurate.

**Solutions:**
1. Use a larger Whisper model (`medium` or `large`)
2. Ensure good audio quality
3. Reduce background noise
4. Specify correct language

### Slow Transcription

**Problem**: Real-time transcription lags behind.

**Solutions:**
1. Use smaller model (`tiny` or `base`)
2. Use GPU acceleration (install CUDA-enabled PyTorch)
3. Increase buffer duration (process less frequently)
4. Close other applications

### Import Errors

**Problem**: `ImportError` for whisper, sounddevice, etc.

**Solutions:**
```bash
# Install missing dependencies
pip install openai-whisper
pip install sounddevice numpy
pip install prompt_toolkit

# Or install all at once
pip install openai-whisper sounddevice numpy prompt_toolkit
```

## Future Enhancements

### Phase 2: Automatic Joining (Coming Soon)

- Browser automation with Selenium/Playwright
- Join Zoom, Teams, Google Meet automatically
- Calendar integration for scheduled auto-join
- Headless mode for background operation

### Phase 3: Meeting Clone (Planned)

- Autonomous meeting participation
- Answer questions in your style
- Take notes and summarize on your behalf
- Intelligent muting/unmuting

### Phase 4: Multi-Meeting Orchestrator (Planned)

- Attend multiple meetings simultaneously
- Priority-based attention allocation
- Cross-meeting context awareness
- Automated follow-up actions

## API Reference

See `src/meeting_listener.py` for complete API documentation.

### Key Classes

- `MeetingListener` - Main coordinator
- `AudioCapture` - Audio recording
- `TranscriptionEngine` - Speech-to-text
- `MeetingSummarizer` - Summary generation
- `MeetingMetadata` - Meeting info
- `TranscriptSegment` - Transcript piece
- `MeetingSummary` - Structured summary

### Key Functions

- `start_meeting()` - Begin recording
- `stop_meeting()` - End and save
- `get_transcript()` - Retrieve transcript
- `list_meetings()` - List all meetings
- `generate_summary()` - Create AI summary

## Contributing

To extend the Meeting Listener:

1. **Add new platforms**: Extend `MeetingJoiner` class
2. **Improve transcription**: Integrate alternative engines
3. **Enhanced summaries**: Customize `MeetingSummarizer` prompts
4. **Speaker diarization**: Add pyannote.audio integration
5. **Calendar sync**: Implement OAuth for Google/Outlook

## License

Part of MetaPersona project. See main LICENSE file.

## Support

For issues and questions:
- Check troubleshooting section above
- Review example code in `examples/`
- Open an issue on GitHub

---

**Next Steps:**
- Complete onboarding: `python metapersona.py onboard`
- Setup meeting listener: `python metapersona.py meeting-setup`
- Record your first meeting: `python metapersona.py meeting-listen`
