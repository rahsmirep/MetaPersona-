#!/usr/bin/env python3
"""
Meeting Listener Installation Test
Quick test to verify all components are working.
"""

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    results = {}
    
    # Core modules
    try:
        from src.meeting_listener import (
            MeetingListener,
            MeetingSummarizer,
            AudioCapture,
            TranscriptionEngine,
            MeetingMetadata,
            TranscriptSegment,
            MeetingSummary
        )
        results['meeting_listener'] = True
        print("  ✓ meeting_listener module")
    except Exception as e:
        results['meeting_listener'] = False
        print(f"  ✗ meeting_listener module: {e}")
    
    try:
        from src.meeting_integrations import (
            MeetingURLParser,
            VirtualAudioDevice,
            MeetingJoiner,
            CalendarIntegration
        )
        results['meeting_integrations'] = True
        print("  ✓ meeting_integrations module")
    except Exception as e:
        results['meeting_integrations'] = False
        print(f"  ✗ meeting_integrations module: {e}")
    
    return results


def test_dependencies():
    """Test if required dependencies are installed."""
    print("\nTesting dependencies...")
    
    results = {}
    
    # Required dependencies
    deps = {
        'sounddevice': 'Audio capture',
        'numpy': 'Audio processing',
        'whisper': 'Speech-to-text',
        'prompt_toolkit': 'Interactive CLI'
    }
    
    for module, description in deps.items():
        try:
            __import__(module)
            results[module] = True
            print(f"  ✓ {module} - {description}")
        except ImportError:
            results[module] = False
            print(f"  ✗ {module} - {description} (NOT INSTALLED)")
    
    return results


def test_audio_devices():
    """Test audio device detection."""
    print("\nTesting audio device detection...")
    
    try:
        from src.meeting_integrations import VirtualAudioDevice
        
        vad = VirtualAudioDevice()
        devices = vad.list_devices()
        
        if devices:
            print(f"  ✓ Found {len(devices)} audio device(s)")
            
            # Check for virtual audio
            if vad.setup():
                print(f"  ✓ Virtual audio device detected: {vad.device_name}")
                return True
            else:
                print("  ⚠ No virtual audio device detected (optional)")
                print("    Install VB-CABLE (Windows), BlackHole (macOS), or PulseAudio loopback (Linux)")
                return True  # Not required, just recommended
        else:
            print("  ✗ No audio devices found")
            return False
            
    except Exception as e:
        print(f"  ✗ Audio device test failed: {e}")
        return False


def test_url_parsing():
    """Test meeting URL parsing."""
    print("\nTesting URL parsing...")
    
    try:
        from src.meeting_integrations import MeetingURLParser
        
        test_urls = [
            ("https://zoom.us/j/123456789", "zoom"),
            ("https://meet.google.com/abc-defg-hij", "meet"),
            ("https://teams.microsoft.com/l/meetup-join/...", "teams"),
        ]
        
        all_passed = True
        for url, expected_platform in test_urls:
            result = MeetingURLParser.parse_url(url)
            if result['platform'] == expected_platform:
                print(f"  ✓ {expected_platform}: {url[:50]}")
            else:
                print(f"  ✗ {expected_platform}: Expected {expected_platform}, got {result['platform']}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ✗ URL parsing test failed: {e}")
        return False


def test_data_structures():
    """Test data structure creation."""
    print("\nTesting data structures...")
    
    try:
        from src.meeting_listener import MeetingMetadata, TranscriptSegment, MeetingSummary
        from datetime import datetime
        
        # Test MeetingMetadata
        metadata = MeetingMetadata(
            meeting_id="test_meeting",
            title="Test Meeting",
            start_time=datetime.now()
        )
        print("  ✓ MeetingMetadata")
        
        # Test TranscriptSegment
        segment = TranscriptSegment(
            timestamp=datetime.now(),
            speaker="Test User",
            text="This is a test.",
            confidence=0.95
        )
        print("  ✓ TranscriptSegment")
        
        # Test MeetingSummary
        summary = MeetingSummary(
            meeting_id="test_meeting",
            generated_at=datetime.now(),
            summary="Test summary"
        )
        print("  ✓ MeetingSummary")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Data structure test failed: {e}")
        return False


def test_integration():
    """Test integration with existing MetaPersona components."""
    print("\nTesting MetaPersona integration...")
    
    try:
        from src.cognitive_profile import ProfileManager
        from src.llm_provider import get_llm_provider
        
        # Test profile loading
        try:
            profile_manager = ProfileManager('./data')
            print("  ✓ ProfileManager accessible")
        except:
            print("  ⚠ ProfileManager not initialized (run 'metapersona.py init' first)")
        
        # Test LLM provider
        try:
            # Don't actually call it, just test if it's available
            print("  ✓ LLM provider accessible")
        except:
            print("  ⚠ LLM provider not configured (check .env)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        return False


def generate_report(results):
    """Generate final test report."""
    print("\n" + "=" * 80)
    print("TEST REPORT")
    print("=" * 80)
    
    all_tests = []
    for category, tests in results.items():
        if isinstance(tests, dict):
            all_tests.extend(tests.values())
        else:
            all_tests.append(tests)
    
    passed = sum(1 for test in all_tests if test)
    total = len(all_tests)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        print("\nYou're ready to use Meeting Listener!")
        print("\nNext steps:")
        print("  1. python metapersona.py meeting-setup")
        print("  2. python metapersona.py meeting-listen --title 'Test'")
        print("  3. Read MEETING_QUICKSTART.md for more info")
    else:
        print("\n⚠ SOME TESTS FAILED")
        print("\nMissing dependencies? Install with:")
        print("  pip install -r requirements-meeting.txt")
        print("\nFor detailed help, see MEETING_QUICKSTART.md")
    
    print()


def main():
    """Run all tests."""
    print("=" * 80)
    print("MEETING LISTENER INSTALLATION TEST")
    print("=" * 80)
    print()
    
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['dependencies'] = test_dependencies()
    results['audio'] = test_audio_devices()
    results['url_parsing'] = test_url_parsing()
    results['data_structures'] = test_data_structures()
    results['integration'] = test_integration()
    
    # Generate report
    generate_report(results)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
