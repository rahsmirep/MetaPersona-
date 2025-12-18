#!/usr/bin/env python3
"""
Meeting Listener Demo
Demonstrates using the Meeting Listener module programmatically.
"""
import time
from src.meeting_listener import MeetingListener, MeetingSummarizer
from src.llm_provider import get_llm_provider
from src.cognitive_profile import ProfileManager


def demo_basic_recording():
    """Demo 1: Basic meeting recording and transcription."""
    print("=" * 80)
    print("DEMO 1: Basic Meeting Recording")
    print("=" * 80)
    
    # Initialize listener
    listener = MeetingListener(
        data_dir='./data/meetings',
        transcription_model='base',
        auto_summarize=False  # We'll do it manually
    )
    
    # Start recording
    print("\n[1] Starting meeting recording...")
    meeting_id = listener.start_meeting(
        title="Demo Team Meeting",
        platform="manual"
    )
    print(f"    Meeting ID: {meeting_id}")
    print("    Status: Recording")
    
    # Simulate meeting (in real usage, this would be actual meeting time)
    print("\n[2] Recording in progress...")
    print("    (Speak into your microphone to test transcription)")
    print("    Waiting 10 seconds...")
    time.sleep(10)
    
    # Stop recording
    print("\n[3] Stopping recording...")
    result = listener.stop_meeting()
    
    print(f"\n✓ Recording complete!")
    print(f"  Duration: {result['metadata']['duration_seconds']:.1f} seconds")
    print(f"  Segments: {len(result['transcript']['segments'])}")
    print(f"  Saved to: {result['files']['transcript_text']}")
    
    # Show some transcript
    if result['transcript']['segments']:
        print("\n[4] Sample transcript:")
        for seg in result['transcript']['segments'][:3]:
            print(f"    [{seg['timestamp']}] {seg['text']}")
    
    return meeting_id


def demo_with_summary(meeting_id):
    """Demo 2: Generate AI summary for a meeting."""
    print("\n" + "=" * 80)
    print("DEMO 2: AI-Powered Summary Generation")
    print("=" * 80)
    
    # Initialize components
    listener = MeetingListener(data_dir='./data/meetings')
    
    # Load transcript
    print(f"\n[1] Loading meeting: {meeting_id}")
    transcript = listener.get_transcript(meeting_id)
    print(f"    Found {len(transcript)} transcript segments")
    
    if not transcript:
        print("    No transcript found! Skipping demo.")
        return
    
    # Load meeting metadata
    from pathlib import Path
    import json
    from src.meeting_listener import MeetingMetadata
    from datetime import datetime
    
    meeting_dir = Path('./data/meetings') / meeting_id
    metadata_file = meeting_dir / 'metadata.json'
    
    with open(metadata_file, 'r') as f:
        metadata_dict = json.load(f)
    
    metadata = MeetingMetadata(
        meeting_id=metadata_dict['meeting_id'],
        title=metadata_dict['title'],
        start_time=datetime.fromisoformat(metadata_dict['start_time']),
        end_time=datetime.fromisoformat(metadata_dict['end_time']) if metadata_dict.get('end_time') else None,
        duration_seconds=metadata_dict.get('duration_seconds', 0),
        platform=metadata_dict.get('platform', 'unknown')
    )
    
    # Initialize LLM and profile
    print("\n[2] Initializing AI summarizer...")
    llm = get_llm_provider('ollama')
    
    # Try to load cognitive profile
    profile_manager = ProfileManager('./data')
    cognitive_profile = profile_manager.load_profile()
    
    if cognitive_profile:
        print(f"    Using cognitive profile: {cognitive_profile.user_id}")
        print(f"    Writing style: {cognitive_profile.writing_style.tone}")
    
    # Create summarizer
    summarizer = MeetingSummarizer(
        llm_provider=llm,
        cognitive_profile=cognitive_profile
    )
    
    # Generate summary
    print("\n[3] Generating AI summary...")
    print("    (This may take 30-60 seconds depending on transcript length)")
    summary = summarizer.generate_summary(transcript, metadata)
    
    # Display summary
    print("\n" + "-" * 80)
    print("MEETING SUMMARY")
    print("-" * 80)
    print(f"\n{summary.summary}\n")
    
    if summary.key_points:
        print("KEY POINTS:")
        for i, point in enumerate(summary.key_points, 1):
            print(f"  {i}. {point}")
        print()
    
    if summary.decisions:
        print("DECISIONS MADE:")
        for i, decision in enumerate(summary.decisions, 1):
            print(f"  {i}. {decision}")
        print()
    
    if summary.action_items:
        print("ACTION ITEMS:")
        for i, item in enumerate(summary.action_items, 1):
            if isinstance(item, dict):
                task = item.get('task', '')
                owner = item.get('owner', 'TBD')
                due = item.get('due', 'TBD')
                print(f"  {i}. {task}")
                print(f"     Owner: {owner}, Due: {due}")
            else:
                print(f"  {i}. {item}")
        print()
    
    if summary.next_steps:
        print("NEXT STEPS:")
        for i, step in enumerate(summary.next_steps, 1):
            print(f"  {i}. {step}")
        print()
    
    print(f"Sentiment: {summary.sentiment.upper()}")
    print("-" * 80)
    
    # Save summary
    summary_file = meeting_dir / 'summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary.to_dict(), f, indent=2)
    
    print(f"\n✓ Summary saved to: {summary_file}")


def demo_list_meetings():
    """Demo 3: List all recorded meetings."""
    print("\n" + "=" * 80)
    print("DEMO 3: List All Meetings")
    print("=" * 80)
    
    listener = MeetingListener(data_dir='./data/meetings')
    meetings = listener.list_meetings()
    
    if not meetings:
        print("\nNo meetings recorded yet.")
        return
    
    print(f"\nFound {len(meetings)} recorded meeting(s):\n")
    
    for i, meeting in enumerate(meetings, 1):
        from datetime import datetime
        start_time = datetime.fromisoformat(meeting['start_time'])
        duration_min = meeting.get('duration_seconds', 0) / 60
        
        print(f"{i}. {meeting['title']}")
        print(f"   ID: {meeting['meeting_id']}")
        print(f"   Date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Duration: {duration_min:.1f} minutes")
        print(f"   Platform: {meeting.get('platform', 'unknown')}")
        print()


def demo_audio_devices():
    """Demo 4: List available audio devices."""
    print("\n" + "=" * 80)
    print("DEMO 4: Audio Device Detection")
    print("=" * 80)
    
    from src.meeting_integrations import VirtualAudioDevice
    
    print("\n[1] Listing all audio devices...")
    vad = VirtualAudioDevice()
    devices = vad.list_devices()
    
    if devices:
        print(f"\nFound {len(devices)} audio device(s):\n")
        for device in devices:
            inputs = "✓" if device['inputs'] > 0 else "✗"
            outputs = "✓" if device['outputs'] > 0 else "✗"
            print(f"  [{device['index']}] {device['name']}")
            print(f"      Inputs: {inputs} ({device['inputs']} channels)")
            print(f"      Outputs: {outputs} ({device['outputs']} channels)")
            print()
    
    print("\n[2] Detecting virtual audio device...")
    if vad.setup():
        print(f"✓ Found virtual audio device: {vad.device_name}")
        print(f"  Device index: {vad.device_index}")
    else:
        print("✗ No virtual audio device detected")
        print("\nFor best results, install a virtual audio device:")
        print("  • Windows: VB-CABLE (https://vb-audio.com/Cable/)")
        print("  • macOS: BlackHole (https://github.com/ExistentialAudio/BlackHole)")
        print("  • Linux: PulseAudio loopback")


def demo_url_parsing():
    """Demo 5: Parse meeting URLs."""
    print("\n" + "=" * 80)
    print("DEMO 5: Meeting URL Parsing")
    print("=" * 80)
    
    from src.meeting_integrations import MeetingURLParser
    
    test_urls = [
        "https://zoom.us/j/123456789",
        "https://meet.google.com/abc-defg-hij",
        "https://teams.microsoft.com/l/meetup-join/...",
        "https://example.webex.com/meet/john.doe",
        "https://some-custom-platform.com/meeting/xyz"
    ]
    
    print("\nParsing meeting URLs:\n")
    
    for url in test_urls:
        result = MeetingURLParser.parse_url(url)
        print(f"URL: {url}")
        print(f"  Platform: {result['platform']}")
        if result['meeting_id']:
            print(f"  Meeting ID: {result['meeting_id']}")
        print()


def demo_personalized_summary():
    """Demo 6: Generate summary with personalization."""
    print("\n" + "=" * 80)
    print("DEMO 6: Personalized Summary Generation")
    print("=" * 80)
    
    # Check for user profile
    from src.user_profiling import UserProfilingSystem
    
    print("\n[1] Checking for user profile...")
    profiling_system = UserProfilingSystem('./data')
    
    # List available profiles
    from pathlib import Path
    profiles_dir = Path('./data/user_profiles')
    
    if profiles_dir.exists():
        profiles = list(profiles_dir.glob('*.json'))
        if profiles:
            print(f"    Found {len(profiles)} user profile(s)")
            for profile_file in profiles:
                user_id = profile_file.stem
                profile = profiling_system.load_profile(user_id)
                if profile:
                    print(f"    • {user_id}: {profile.profession} ({profile.preferred_communication_style})")
        else:
            print("    No user profiles found")
            print("    Run: python metapersona.py onboard")
    else:
        print("    No user profiles directory")
        print("    Run: python metapersona.py onboard")
    
    print("\n[2] Personalization features:")
    print("    ✓ Writing style matching (tone, vocabulary)")
    print("    ✓ Industry-specific terminology")
    print("    ✓ Technical level adaptation")
    print("    ✓ Skill pack context")
    print("    ✓ Communication style preferences")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print(" " * 25 + "MEETING LISTENER DEMO")
    print("=" * 80)
    print("\nThis demo will show various Meeting Listener capabilities.")
    print("Some demos require manual interaction (speaking into microphone).")
    print("\nPress Ctrl+C to skip any demo.\n")
    
    import sys
    
    try:
        # Demo 4: Audio devices (first to help setup)
        input("Press Enter to run Demo 4: Audio Device Detection... ")
        demo_audio_devices()
        
        # Demo 5: URL parsing
        input("\nPress Enter to run Demo 5: Meeting URL Parsing... ")
        demo_url_parsing()
        
        # Demo 3: List existing meetings
        input("\nPress Enter to run Demo 3: List Meetings... ")
        demo_list_meetings()
        
        # Demo 6: Personalization info
        input("\nPress Enter to run Demo 6: Personalization Features... ")
        demo_personalized_summary()
        
        # Demo 1: Record a meeting (interactive)
        print("\n" + "=" * 80)
        response = input("\nRun Demo 1 (Basic Recording)? This requires speaking. (y/n): ")
        if response.lower() == 'y':
            meeting_id = demo_basic_recording()
            
            # Demo 2: Generate summary
            if meeting_id:
                response = input("\nGenerate AI summary for this meeting? (y/n): ")
                if response.lower() == 'y':
                    demo_with_summary(meeting_id)
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETE!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Run: python metapersona.py meeting-setup")
        print("  2. Run: python metapersona.py onboard")
        print("  3. Run: python metapersona.py meeting-listen")
        print()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
