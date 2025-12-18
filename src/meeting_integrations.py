"""
Meeting Integrations
Handles joining and capturing audio from various meeting platforms.
"""
from typing import Optional, Dict, Any
from enum import Enum
import re


class MeetingPlatform(Enum):
    """Supported meeting platforms."""
    ZOOM = "zoom"
    MICROSOFT_TEAMS = "teams"
    GOOGLE_MEET = "meet"
    WEBEX = "webex"
    GENERIC = "generic"


class MeetingURLParser:
    """Parse meeting URLs to extract platform and meeting details."""
    
    PATTERNS = {
        MeetingPlatform.ZOOM: [
            r'https?://(?:[\w-]+\.)?zoom\.us/j/(\d+)',
            r'https?://(?:[\w-]+\.)?zoom\.us/s/(\d+)',
        ],
        MeetingPlatform.MICROSOFT_TEAMS: [
            r'https?://teams\.microsoft\.com/l/meetup-join/',
        ],
        MeetingPlatform.GOOGLE_MEET: [
            r'https?://meet\.google\.com/([\w-]+)',
        ],
        MeetingPlatform.WEBEX: [
            r'https?://(?:[\w-]+\.)?webex\.com/meet/([\w-]+)',
        ],
    }
    
    @classmethod
    def parse_url(cls, url: str) -> Dict[str, Any]:
        """Parse a meeting URL and extract details."""
        for platform, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return {
                        'platform': platform.value,
                        'meeting_id': match.group(1) if match.lastindex else None,
                        'url': url
                    }
        
        return {
            'platform': MeetingPlatform.GENERIC.value,
            'meeting_id': None,
            'url': url
        }


class VirtualAudioDevice:
    """
    Manages virtual audio devices for capturing meeting audio.
    
    This is a placeholder for platform-specific implementations.
    On Windows: Use VB-CABLE or similar
    On macOS: Use BlackHole or similar
    On Linux: Use PulseAudio loopback
    """
    
    def __init__(self):
        self.device_name = None
        self.device_index = None
    
    def setup(self) -> bool:
        """Setup virtual audio device."""
        # Detect available virtual audio devices
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            
            # Look for common virtual audio device names
            virtual_device_names = [
                'VB-Cable',
                'BlackHole',
                'Loopback',
                'CABLE Output',
                'Stereo Mix'
            ]
            
            for i, device in enumerate(devices):
                device_name = device['name']
                for virt_name in virtual_device_names:
                    if virt_name.lower() in device_name.lower():
                        if device['max_input_channels'] > 0:
                            self.device_name = device_name
                            self.device_index = i
                            print(f"Found virtual audio device: {device_name}")
                            return True
            
            print("No virtual audio device found. Using default input.")
            return False
            
        except ImportError:
            print("sounddevice not installed")
            return False
    
    def get_device_index(self) -> Optional[int]:
        """Get the device index for audio capture."""
        return self.device_index
    
    def list_devices(self) -> list:
        """List all available audio devices."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            return [
                {
                    'index': i,
                    'name': device['name'],
                    'inputs': device['max_input_channels'],
                    'outputs': device['max_output_channels']
                }
                for i, device in enumerate(devices)
            ]
        except ImportError:
            return []


class MeetingJoiner:
    """
    Automatically joins meetings on various platforms.
    
    This is a placeholder for future implementation using browser automation
    (Selenium/Playwright) or platform-specific APIs.
    """
    
    def __init__(self):
        self.browser = None
        self.current_platform = None
    
    def join_meeting(self, url: str, display_name: str = "Meeting Listener") -> bool:
        """
        Join a meeting via URL.
        
        Future implementation will use browser automation to:
        1. Open meeting URL
        2. Set display name
        3. Disable camera/microphone (we only listen)
        4. Join meeting
        5. Route audio to virtual audio device
        """
        parsed = MeetingURLParser.parse_url(url)
        self.current_platform = parsed['platform']
        
        print(f"Would join {parsed['platform']} meeting: {url}")
        print("Note: Automatic joining requires browser automation (not yet implemented)")
        print("For now, manually join the meeting and ensure audio is routed to virtual device")
        
        return False  # Not implemented yet
    
    def leave_meeting(self) -> bool:
        """Leave the current meeting."""
        if self.browser:
            print("Would leave meeting")
            return True
        return False
    
    def is_in_meeting(self) -> bool:
        """Check if currently in a meeting."""
        return self.browser is not None


class CalendarIntegration:
    """
    Integration with calendar services to automatically detect and join meetings.
    
    This is a placeholder for future implementation.
    Supports: Google Calendar, Outlook Calendar, etc.
    """
    
    def __init__(self, calendar_provider: str = "google"):
        self.provider = calendar_provider
        self.authenticated = False
    
    def authenticate(self, credentials_path: Optional[str] = None) -> bool:
        """Authenticate with calendar service."""
        # Future: OAuth flow for Google Calendar, Microsoft Graph API for Outlook
        print(f"Calendar authentication not yet implemented for {self.provider}")
        return False
    
    def get_upcoming_meetings(self, hours_ahead: int = 2) -> list:
        """Get upcoming meetings from calendar."""
        # Future: Query calendar API
        return []
    
    def extract_meeting_urls(self, event: Dict[str, Any]) -> Optional[str]:
        """Extract meeting URL from calendar event."""
        # Future: Parse event description/location for meeting URLs
        return None
    
    def schedule_auto_join(self, meeting_id: str, join_time: str):
        """Schedule automatic joining for a meeting."""
        # Future: Schedule task to join meeting at specified time
        pass


def setup_meeting_listener(
    use_virtual_device: bool = True,
    calendar_provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Setup meeting listener with platform integrations.
    
    Returns configuration and status.
    """
    config = {
        'virtual_audio': None,
        'calendar': None,
        'joiner': None,
        'status': 'configured'
    }
    
    # Setup virtual audio device
    if use_virtual_device:
        vad = VirtualAudioDevice()
        if vad.setup():
            config['virtual_audio'] = {
                'device_name': vad.device_name,
                'device_index': vad.device_index
            }
        else:
            print("Warning: No virtual audio device found. Using default input.")
    
    # Setup calendar integration
    if calendar_provider:
        cal = CalendarIntegration(calendar_provider)
        config['calendar'] = {
            'provider': calendar_provider,
            'authenticated': False
        }
        print(f"Calendar integration will be available in future updates")
    
    # Setup meeting joiner
    joiner = MeetingJoiner()
    config['joiner'] = {
        'available': False,
        'note': 'Automatic joining will be available in future updates'
    }
    
    return config
