#!/usr/bin/env python3
"""List all available audio devices"""
import sounddevice as sd

devices = sd.query_devices()
print("\n=== Available Audio Devices ===\n")

for i, device in enumerate(devices):
    device_type = []
    if device['max_input_channels'] > 0:
        device_type.append('INPUT')
    if device['max_output_channels'] > 0:
        device_type.append('OUTPUT')
    
    print(f"{i}: {device['name']}")
    print(f"   Type: {' + '.join(device_type)}")
    print(f"   Channels: In={device['max_input_channels']}, Out={device['max_output_channels']}")
    print()

print(f"Default Input Device: {sd.default.device[0]}")
print(f"Default Output Device: {sd.default.device[1]}")
