"""
Meeting Listener Module
Captures audio from meetings, transcribes in real-time, and generates summaries.
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
import json
from enum import Enum
import threading
import queue


class MeetingStatus(Enum):
    """Meeting recording status."""
    WAITING = "waiting"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class TranscriptSegment:
    """A segment of transcribed audio."""
    timestamp: datetime
    speaker: Optional[str]
    text: str
    confidence: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'speaker': self.speaker,
            'text': self.text,
            'confidence': self.confidence,
            'start_time': self.start_time,
            'end_time': self.end_time
        }


@dataclass
class MeetingMetadata:
    """Metadata about the meeting."""
    meeting_id: str
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    participants: List[str] = field(default_factory=list)
    platform: str = "unknown"  # zoom, teams, meet, etc.
    meeting_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'meeting_id': self.meeting_id,
            'title': self.title,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'participants': self.participants,
            'platform': self.platform,
            'meeting_url': self.meeting_url
        }


@dataclass
class MeetingSummary:
    """Structured summary of a meeting."""
    meeting_id: str
    generated_at: datetime
    summary: str
    key_points: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    action_items: List[Dict[str, str]] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'meeting_id': self.meeting_id,
            'generated_at': self.generated_at.isoformat(),
            'summary': self.summary,
            'key_points': self.key_points,
            'decisions': self.decisions,
            'action_items': self.action_items,
            'topics_discussed': self.topics_discussed,
            'next_steps': self.next_steps,
            'sentiment': self.sentiment
        }


class AudioCapture:
    """Handles audio capture from system or microphone."""
    
    def __init__(self, device_index: Optional[int] = None, sample_rate: int = 16000):
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.actual_sample_rate = sample_rate  # Will be updated to device's native rate
        self.is_capturing = False
        self.audio_queue = queue.Queue()
        self.capture_thread = None
        
    def start_capture(self):
        """Start capturing audio."""
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.start()
    
    def stop_capture(self):
        """Stop capturing audio."""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join()
    
    def _capture_loop(self):
        """Main audio capture loop (to be implemented with pyaudio/sounddevice)."""
        try:
            import sounddevice as sd
            import numpy as np
            
            # Get device info and use its native sample rate if specified device
            actual_sample_rate = self.sample_rate
            if self.device_index is not None:
                try:
                    device_info = sd.query_devices(self.device_index)
                    actual_sample_rate = int(device_info['default_samplerate'])
                except Exception as e:
                    print(f"[Warning] Could not get device sample rate: {e}")
            
            self.actual_sample_rate = actual_sample_rate  # Store for transcription
            frames_captured = 0
            
            def audio_callback(indata, frames, time, status):
                nonlocal frames_captured
                if status:
                    print(f"[Audio Warning] {status}")
                # Convert to bytes and add to queue
                audio_data = (indata * 32767).astype(np.int16).tobytes()
                self.audio_queue.put(audio_data)
                frames_captured += 1
            
            with sd.InputStream(
                samplerate=actual_sample_rate,
                channels=1,
                dtype='int16',
                callback=audio_callback,
                device=self.device_index
            ):
                while self.is_capturing:
                    sd.sleep(100)
                    
        except ImportError:
            print("[Error] sounddevice not installed. Install with: pip install sounddevice numpy")
            self.is_capturing = False
        except Exception as e:
            print(f"[Error] Audio capture failed: {e}")
            self.is_capturing = False
    
    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[bytes]:
        """Get next audio chunk from queue."""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None


class TranscriptionEngine:
    """Handles real-time transcription of audio."""
    
    def __init__(self, model: str = "base", language: str = "en"):
        self.model_name = model
        self.language = language
        self.model = None
        self.vad = None
        self._load_model()
        self._init_vad()
    
    def _load_model(self):
        """Load the transcription model."""
        try:
            import whisper
            self.model = whisper.load_model(self.model_name)
        except ImportError:
            print("[Error] Whisper not installed. Install with: pip install openai-whisper")
        except Exception as e:
            print(f"[Error] Failed to load Whisper model: {e}")
    
    def _init_vad(self):
        """Initialize Voice Activity Detection."""
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad(3)  # Aggressiveness mode 0-3 (3 is most aggressive)
        except ImportError:
            print("[Warning] webrtcvad not installed. VAD disabled.")
        except Exception as e:
            print(f"[Warning] Could not initialize VAD: {e}")
    
    def _detect_voice_activity(self, audio_data: bytes, sample_rate: int) -> bool:
        """Detect if audio contains speech using WebRTC VAD."""
        if not self.vad:
            return True  # If VAD not available, assume speech is present
        
        try:
            import webrtcvad
            from scipy import signal
            import numpy as np
            
            # VAD requires specific sample rates: 8000, 16000, 32000, or 48000 Hz
            vad_sample_rates = [8000, 16000, 32000, 48000]
            target_rate = min(vad_sample_rates, key=lambda x: abs(x - sample_rate))
            
            # Resample if needed
            if sample_rate != target_rate:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                num_samples = int(len(audio_array) * target_rate / sample_rate)
                audio_resampled = signal.resample(audio_array, num_samples)
                audio_data = audio_resampled.astype(np.int16).tobytes()
                sample_rate = target_rate
            
            # VAD requires frames of 10, 20, or 30 ms
            frame_duration = 30  # ms
            frame_size = int(sample_rate * frame_duration / 1000) * 2  # 2 bytes per sample
            
            # Check multiple frames
            speech_frames = 0
            total_frames = 0
            
            for i in range(0, len(audio_data) - frame_size, frame_size):
                frame = audio_data[i:i + frame_size]
                if len(frame) == frame_size:
                    try:
                        is_speech = self.vad.is_speech(frame, sample_rate)
                        if is_speech:
                            speech_frames += 1
                        total_frames += 1
                    except:
                        continue
            
            # Require at least 50% of frames to contain speech
            if total_frames > 0:
                speech_ratio = speech_frames / total_frames
                return speech_ratio >= 0.5
            
            return False
            
        except Exception as e:
            # If VAD fails, fall back to assuming speech is present
            return True
    
    def transcribe_audio(self, audio_data: bytes, sample_rate: int = 16000) -> Optional[TranscriptSegment]:
        """Transcribe audio data to text."""
        if not self.model:
            print("[Error] Whisper model not loaded!")
            return None
        
        try:
            import numpy as np
            from scipy import signal
            
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Resample to 16kHz if necessary (Whisper expects 16kHz)
            if sample_rate != 16000:
                num_samples = int(len(audio_float) * 16000 / sample_rate)
                audio_float = signal.resample(audio_float, num_samples)
            
            # Check if audio has content (not silence)
            audio_level = np.abs(audio_float).mean()
            max_level = np.abs(audio_float).max()
            
            # Require significant audio level AND variation
            if audio_level < 0.05 or max_level < 0.15:
                return None
            
            # Voice Activity Detection - check if speech is present
            has_speech = self._detect_voice_activity(audio_data, sample_rate)
            if not has_speech:
                return None
            
            # Transcribe (suppress all output including progress bars)
            import warnings
            import sys
            import os
            from contextlib import redirect_stderr, redirect_stdout
            
            # Suppress all output from Whisper
            with open(os.devnull, 'w') as devnull:
                with redirect_stderr(devnull), redirect_stdout(devnull):
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        result = self.model.transcribe(
                            audio_float,
                            language=self.language,
                            fp16=False,
                            verbose=False
                        )
            
            if result and result.get('text'):
                text = result['text'].strip()
                if text:
                    return TranscriptSegment(
                        timestamp=datetime.now(),
                        speaker=None,  # Speaker diarization can be added later
                        text=text,
                        confidence=1.0  # Whisper doesn't provide confidence scores
                    )
                
        except Exception as e:
            print(f"[Error] Transcription failed: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def transcribe_file(self, audio_file_path: str) -> Optional[Dict[str, Any]]:
        """Transcribe an entire audio file."""
        if not self.model:
            return None
        
        try:
            result = self.model.transcribe(
                audio_file_path,
                language=self.language,
                verbose=False
            )
            return result
        except Exception as e:
            print(f"File transcription error: {e}")
            return None


class MeetingListener:
    """Main meeting listener class that coordinates audio capture and transcription."""
    
    def __init__(
        self,
        data_dir: str = "./data/meetings",
        transcription_model: str = "base",
        auto_summarize: bool = True,
        llm_provider = None,
        cognitive_profile = None,
        device_index: Optional[int] = None
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.audio_capture = AudioCapture(device_index=device_index)
        self.transcription_engine = TranscriptionEngine(model=transcription_model)
        
        self.status = MeetingStatus.WAITING
        self.current_meeting: Optional[MeetingMetadata] = None
        self.transcript_segments: List[TranscriptSegment] = []
        self.auto_summarize = auto_summarize
        
        self.processing_thread = None
        self.should_process = False
    
    def start_meeting(
        self,
        title: str,
        meeting_id: Optional[str] = None,
        platform: str = "manual",
        meeting_url: Optional[str] = None
    ) -> str:
        """Start recording a new meeting."""
        if self.status == MeetingStatus.RECORDING:
            raise RuntimeError("Meeting already in progress")
        
        # Generate meeting ID if not provided
        if not meeting_id:
            meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create meeting metadata
        self.current_meeting = MeetingMetadata(
            meeting_id=meeting_id,
            title=title,
            start_time=datetime.now(),
            platform=platform,
            meeting_url=meeting_url
        )
        
        # Reset transcript
        self.transcript_segments = []
        
        # Start audio capture
        self.audio_capture.start_capture()
        
        # Start processing thread
        self.should_process = True
        self.processing_thread = threading.Thread(target=self._process_audio_loop)
        self.processing_thread.start()
        
        self.status = MeetingStatus.RECORDING
        
        print(f"Started recording meeting: {title} ({meeting_id})")
        return meeting_id
    
    def stop_meeting(self) -> Dict[str, Any]:
        """Stop recording and finalize the meeting."""
        if self.status != MeetingStatus.RECORDING:
            raise RuntimeError("No meeting in progress")
        
        print("Stopping meeting recording...")
        
        # Stop processing
        self.should_process = False
        if self.processing_thread:
            self.processing_thread.join()
        
        # Stop audio capture
        self.audio_capture.stop_capture()
        
        # Finalize metadata
        if self.current_meeting:
            self.current_meeting.end_time = datetime.now()
            self.current_meeting.duration_seconds = (
                self.current_meeting.end_time - self.current_meeting.start_time
            ).total_seconds()
        
        self.status = MeetingStatus.STOPPED
        
        # Save transcript
        transcript_data = self._save_meeting_data()
        
        # Generate summary if enabled
        if self.auto_summarize:
            self.status = MeetingStatus.PROCESSING
            summary = self._generate_summary()
            transcript_data['summary'] = summary.to_dict() if summary else None
        
        self.status = MeetingStatus.COMPLETED
        
        print(f"Meeting recording completed: {self.current_meeting.meeting_id}")
        
        return transcript_data
    
    def pause_meeting(self):
        """Pause recording."""
        if self.status == MeetingStatus.RECORDING:
            self.should_process = False
            self.status = MeetingStatus.PAUSED
            print("Meeting paused")
    
    def resume_meeting(self):
        """Resume recording."""
        if self.status == MeetingStatus.PAUSED:
            self.should_process = True
            self.processing_thread = threading.Thread(target=self._process_audio_loop)
            self.processing_thread.start()
            self.status = MeetingStatus.RECORDING
            print("Meeting resumed")
    
    def _process_audio_loop(self):
        """Background thread that processes audio chunks."""
        audio_buffer = bytearray()
        buffer_duration = 3.0  # Process every 3 seconds (faster feedback)
        # Use actual sample rate from audio capture
        sample_rate = self.audio_capture.actual_sample_rate
        bytes_per_second = sample_rate * 2  # 16-bit audio
        buffer_size = int(buffer_duration * bytes_per_second)
        
        chunks_received = 0
        while self.should_process:
            chunk = self.audio_capture.get_audio_chunk(timeout=0.5)
            
            if chunk:
                chunks_received += 1
                audio_buffer.extend(chunk)
                
                # Process when buffer is full
                if len(audio_buffer) >= buffer_size:
                    segment = self.transcription_engine.transcribe_audio(
                        bytes(audio_buffer),
                        sample_rate
                    )
                    
                    if segment and segment.text:
                        self.transcript_segments.append(segment)
                        print(f"\n[{segment.timestamp.strftime('%H:%M:%S')}] {segment.text}\n")
                    
                    # Clear buffer
                    audio_buffer.clear()
                    chunks_received = 0
    
    def _save_meeting_data(self) -> Dict[str, Any]:
        """Save meeting data to disk."""
        if not self.current_meeting:
            return {}
        
        meeting_dir = self.data_dir / self.current_meeting.meeting_id
        meeting_dir.mkdir(exist_ok=True)
        
        # Save metadata
        metadata_file = meeting_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.current_meeting.to_dict(), f, indent=2)
        
        # Save transcript
        transcript_file = meeting_dir / "transcript.json"
        transcript_data = {
            'meeting_id': self.current_meeting.meeting_id,
            'segments': [seg.to_dict() for seg in self.transcript_segments]
        }
        with open(transcript_file, 'w') as f:
            json.dump(transcript_data, f, indent=2)
        
        # Save readable transcript
        transcript_text_file = meeting_dir / "transcript.txt"
        with open(transcript_text_file, 'w') as f:
            f.write(f"Meeting: {self.current_meeting.title}\n")
            f.write(f"Date: {self.current_meeting.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {self.current_meeting.duration_seconds:.0f} seconds\n\n")
            f.write("=" * 80 + "\n\n")
            
            for seg in self.transcript_segments:
                time_str = seg.timestamp.strftime('%H:%M:%S')
                speaker = f"[{seg.speaker}] " if seg.speaker else ""
                f.write(f"[{time_str}] {speaker}{seg.text}\n")
        
        return {
            'meeting_id': self.current_meeting.meeting_id,
            'metadata': self.current_meeting.to_dict(),
            'transcript': transcript_data,
            'files': {
                'metadata': str(metadata_file),
                'transcript_json': str(transcript_file),
                'transcript_text': str(transcript_text_file)
            }
        }
    
    def _generate_summary(self) -> Optional[MeetingSummary]:
        """Generate meeting summary using AI assistant."""
        if not self.current_meeting or not self.transcript_segments:
            return None
        
        # Combine all transcript segments
        full_transcript = "\n".join([seg.text for seg in self.transcript_segments])
        
        # Create summary (placeholder - will integrate with persona_agent)
        summary = MeetingSummary(
            meeting_id=self.current_meeting.meeting_id,
            generated_at=datetime.now(),
            summary=f"Meeting summary for: {self.current_meeting.title}",
            key_points=["Point 1", "Point 2", "Point 3"],
            decisions=["Decision 1"],
            action_items=[
                {"task": "Action item 1", "owner": "TBD", "due": "TBD"}
            ],
            topics_discussed=["Topic 1", "Topic 2"]
        )
        
        # Save summary
        if self.current_meeting:
            meeting_dir = self.data_dir / self.current_meeting.meeting_id
            summary_file = meeting_dir / "summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary.to_dict(), f, indent=2)
        
        return summary
    
    def get_transcript(self, meeting_id: Optional[str] = None) -> List[TranscriptSegment]:
        """Get transcript for current or specified meeting."""
        if meeting_id:
            # Load from disk
            meeting_dir = self.data_dir / meeting_id
            transcript_file = meeting_dir / "transcript.json"
            
            if transcript_file.exists():
                with open(transcript_file, 'r') as f:
                    data = json.load(f)
                    segments = []
                    for seg_data in data.get('segments', []):
                        segments.append(TranscriptSegment(
                            timestamp=datetime.fromisoformat(seg_data['timestamp']),
                            speaker=seg_data.get('speaker'),
                            text=seg_data['text'],
                            confidence=seg_data.get('confidence', 0.0),
                            start_time=seg_data.get('start_time', 0.0),
                            end_time=seg_data.get('end_time', 0.0)
                        ))
                    return segments
            return []
        
        return self.transcript_segments
    
    def list_meetings(self) -> List[Dict[str, Any]]:
        """List all recorded meetings."""
        meetings = []
        
        for meeting_dir in self.data_dir.iterdir():
            if meeting_dir.is_dir():
                metadata_file = meeting_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        meetings.append(json.load(f))
        
        # Sort by start time (most recent first)
        meetings.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        
        return meetings


class MeetingSummarizer:
    """Generates structured summaries from meeting transcripts."""
    
    def __init__(self, llm_provider=None, cognitive_profile=None, user_profile=None):
        self.llm_provider = llm_provider
        self.cognitive_profile = cognitive_profile
        self.user_profile = user_profile
    
    def generate_summary(
        self,
        transcript: List[TranscriptSegment],
        meeting_metadata: MeetingMetadata
    ) -> MeetingSummary:
        """Generate a structured summary from transcript."""
        
        # Combine transcript
        full_text = "\n".join([f"[{seg.timestamp.strftime('%H:%M:%S')}] {seg.text}" for seg in transcript])
        
        # Create prompt for LLM
        prompt = f"""Analyze this meeting transcript and provide a structured summary.

Meeting: {meeting_metadata.title}
Duration: {meeting_metadata.duration_seconds / 60:.1f} minutes

TRANSCRIPT:
{full_text}

Please provide:
1. A brief summary (2-3 sentences)
2. Key points discussed (bullet points)
3. Decisions made
4. Action items (with suggested owners if mentioned)
5. Topics discussed
6. Next steps
7. Overall sentiment (positive/neutral/negative)

Format your response as JSON with these exact keys:
- summary
- key_points (array)
- decisions (array)
- action_items (array of objects with: task, owner, due)
- topics_discussed (array)
- next_steps (array)
- sentiment
"""
        
        # Call LLM if available
        if self.llm_provider:
            try:
                response = self.llm_provider.generate(prompt)
                
                # Parse JSON response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    
                    return MeetingSummary(
                        meeting_id=meeting_metadata.meeting_id,
                        generated_at=datetime.now(),
                        summary=result.get('summary', ''),
                        key_points=result.get('key_points', []),
                        decisions=result.get('decisions', []),
                        action_items=result.get('action_items', []),
                        topics_discussed=result.get('topics_discussed', []),
                        next_steps=result.get('next_steps', []),
                        sentiment=result.get('sentiment', 'neutral')
                    )
            except Exception as e:
                print(f"Error generating summary: {e}")
        
        # Fallback: basic summary
        return MeetingSummary(
            meeting_id=meeting_metadata.meeting_id,
            generated_at=datetime.now(),
            summary=f"Meeting: {meeting_metadata.title} - {len(transcript)} segments transcribed",
            key_points=[seg.text for seg in transcript[:3]],
            decisions=[],
            action_items=[],
            topics_discussed=[],
            next_steps=[]
        )
