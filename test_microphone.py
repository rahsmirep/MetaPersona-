#!/usr/bin/env python3
"""
Simple microphone test script
Tests if your microphone is capturing audio and if Whisper can transcribe it.
"""
import sounddevice as sd
import numpy as np
import whisper
import sys

def list_devices():
    """List all available audio input devices."""
    print("\n=== Available Audio Input Devices ===\n")
    devices = sd.query_devices()
    default_in = sd.default.device[0]
    
    input_devices = []
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            status = " (DEFAULT)" if i == default_in else ""
            print(f"{i}: {dev['name']}{status}")
            print(f"   Channels: {dev['max_input_channels']}, Sample Rate: {dev['default_samplerate']:.0f}Hz\n")
            input_devices.append(i)
    
    return input_devices

def test_audio_level(device_id=None, duration=5):
    """Test if microphone is capturing audio."""
    print(f"\n=== Testing Audio Levels ===")
    print(f"Recording for {duration} seconds...")
    print("SPEAK NOW into your microphone!\n")
    
    try:
        # Get device sample rate
        if device_id is not None:
            device_info = sd.query_devices(device_id)
            sample_rate = int(device_info['default_samplerate'])
        else:
            sample_rate = 44100
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            device=device_id
        )
        sd.wait()
        
        # Analyze audio levels
        audio_levels = np.abs(recording).flatten()
        max_level = audio_levels.max()
        avg_level = audio_levels.mean()
        
        print(f"\n✓ Recording complete!")
        print(f"  Max audio level: {max_level:.3f}")
        print(f"  Average level:   {avg_level:.3f}")
        
        if avg_level < 0.01:
            print("\n⚠️  WARNING: Audio level is very low (almost silent)")
            print("   - Check if your microphone is muted")
            print("   - Check Windows Sound settings")
            print("   - Try speaking louder")
            return None
        elif max_level < 0.1:
            print("\n⚠️  Audio detected but very quiet")
            print("   - Try speaking louder or closer to the mic")
        else:
            print("\n✓ Good audio levels detected!")
        
        return recording, sample_rate
        
    except Exception as e:
        print(f"\n❌ Error recording audio: {e}")
        return None

def test_transcription(audio_data, sample_rate):
    """Test if Whisper can transcribe the audio."""
    print(f"\n=== Testing Transcription ===")
    print("Loading Whisper model (this may take a minute)...")
    
    try:
        model = whisper.load_model("base")
        print("✓ Model loaded!")
        
        # Prepare audio for Whisper
        audio_float = audio_data.flatten()
        
        # Resample to 16kHz if needed
        if sample_rate != 16000:
            from scipy import signal
            num_samples = int(len(audio_float) * 16000 / sample_rate)
            audio_float = signal.resample(audio_float, num_samples)
            print(f"✓ Resampled from {sample_rate}Hz to 16000Hz")
        
        print("\nTranscribing...")
        result = model.transcribe(audio_float, language="en", fp16=False, verbose=False)
        
        if result and result.get('text'):
            text = result['text'].strip()
            if text:
                print(f"\n✓ TRANSCRIPTION SUCCESS!")
                print(f"\n📝 Transcript:")
                print(f"   \"{text}\"\n")
                return True
            else:
                print("\n⚠️  Whisper returned empty transcription")
                print("   - The audio might not contain clear speech")
                print("   - Try speaking more clearly")
        else:
            print("\n⚠️  No transcription result")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("MICROPHONE & TRANSCRIPTION TEST")
    print("=" * 60)
    
    # List devices
    input_devices = list_devices()
    
    if not input_devices:
        print("❌ No input devices found!")
        return
    
    # Get device selection
    print("\nEnter device number to test (or press Enter for default):")
    device_input = input("> ").strip()
    
    device_id = None
    if device_input:
        try:
            device_id = int(device_input)
            if device_id not in input_devices:
                print(f"❌ Invalid device ID: {device_id}")
                return
        except ValueError:
            print("❌ Invalid input")
            return
    
    # Test audio levels
    result = test_audio_level(device_id, duration=5)
    
    if result is None:
        print("\n❌ Test failed - no audio captured")
        return
    
    audio_data, sample_rate = result
    
    # Ask if user wants to test transcription
    print("\nDo you want to test transcription? (y/n)")
    if input("> ").strip().lower() == 'y':
        test_transcription(audio_data, sample_rate)
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
