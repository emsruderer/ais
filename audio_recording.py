"""
Audio Voice Recorder for Linux/Ubuntu
Records microphone input to WAV files with real-time feedback
"""
import argparse
from html import parser
import wave
import threading
import os
import time

from datetime import datetime
import pyaudio
from pyaudio import paNoDevice


class VoiceRecorder(threading.Thread):
    """Voice recorder using PyAudio for Linux/Ubuntu"""

    def __init__(self, filename='out.wav', sample_rate=22050, chunk_size=1024, device_index=4, channels = 1, format = 'PCM_16'):
        """
        Initialize the voice recorder
        Args:
            filename: Output WAV file path. If None, generates timestamped filename
            duration: Recording duration in seconds. If None, records until stop() is called
            sample_rate: Audio sample rate in Hz (default: 44100)
            chunk_size: Buffer size for audio chunks (default: 1024)
            device_index: Input device index. If None, uses system default
        """
        super().__init__()
        self.sample_rate = sample_rate
        self.channels = channels  # Mono
        self.chunk_size = chunk_size
        self.is_recording = False
        self.audio_data = []
        self.device_index = device_index

        if format == 'PCM_16':
            self.format = pyaudio.paInt16
        elif format == 'PCM_24':
            self.format = pyaudio.paInt24
        elif format == 'FLOAT':
            self.format = pyaudio.paFloat32
        else:
            self.format = pyaudio.paInt16  # Default to PCM_16


       self.filename = filename
        self.p = pyaudio.PyAudio()
        self.stream = None

    def list_input_devices(self):
        """List all available input devices"""
        print("\n=== Available Input Devices ===")
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"Device {i}: {info['name']}")
                print(f"  Channels: {info['maxInputChannels']}")
                print(f"  Sample Rate: {int(info['defaultSampleRate'])} Hz")
        print()

    def set_input_device(self, device_index ):
        """Set the input device by index"""
        try:
            info = self.p.get_device_info_by_index(device_index)
            if info['maxInputChannels'] > 0:
                self.device_index = device_index
                print(f"Set input device to: {info['name']}")
            else:
                print(f"Device {device_index} is not an input device")
        except paNoDevice:
            print(f"Invalid device index: {device_index}")

    def run(self):
        """Thread run method to start recording"""
        self.start_recording()

    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            print("Already recording")
            return

        device_info = self.p.get_device_info_by_index(self.device_index)
        print(f"Using device: {device_info['name']}")

        self.stream = self.p.open(
                    format= self.format,
                    channels = self.channels,
                    rate = self.sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=self.chunk_size)

        self.is_recording = True
        self.audio_data = []
       # Record in a separate thread if duration is specified

        print(f"Recording started... (File: {self.filename})")
        self._record_continuous()

    def _record_continuous(self):
        """Internal: Record continuously until stop() is called"""
        frames_count = 0
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.append(data)
                frames_count += 1
                if frames_count % 50 == 0:  # Print every ~1 second at 44100 Hz
                    print(f"\rRecording... {frames_count * self.chunk_size / self.sample_rate:.1f}s", end="", flush=True)
            except pyaudio.paInputOverflow  as e:
                print(f"Error reading audio: {e}")
                break

    def stop_recording(self):
        """Stop recording and save to file"""
        if not self.is_recording:
            print("Not currently recording")
            return

        self.is_recording = False

        # Close stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        # Save to WAV file
        self._save_to_file()

    def _save_to_file(self):
        """Internal: Save recorded audio to WAV file"""
        if not self.audio_data:
            print("No audio data to save")
            return

        try:
            # Concatenate all audio data
            audio_bytes = b''.join(self.audio_data)

            # Write WAV file
            wf = wave.open(self.filename, "wb" )
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_bytes)
            wf.close()
            file_size = os.path.getsize(self.filename) / (1024 * 1024)  # Size in MB
            print(f"\n✓ Recording saved: {self.filename} ({file_size:.2f} MB)")
        except Exception as e:
            print(f"Error saving file: {e}")

    def cleanup(self):
        """Clean up resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        print("Recorder cleaned up")


# Example usage and testing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="audio_recording.py", description="Voice recorder to WAV", add_help=True)

    parser.add_argument("filename", help="filename (e.g. out.wav)")
    parser.add_argument("-d", "--device", type=float, default=4, help="Device index for input")
    parser.add_argument("-r", "--samplerate", type=int, default=22050, help="Sample rate (default 22050)")
    parser.add_argument("-c", "--channels", type=int, default=1, help="Number of channels (1=mono, 2=stereo)")
    parser.add_argument("-s", "--subtype", type=str, default="PCM_16", help="soundfile subtype, one of: PCM_16, PCM_24 orFLOAT")
    args =      parser.parse_args()
    # Create recorder instance
    recorder = VoiceRecorder(filename=args.filename, device_index=args.device, sample_rate=args.samplerate, channels=args.channels, format=args.subtype)

    # List available devices
    recorder.list_input_devices()

    device_choice = input("\nEnter device number (or press Enter for default): ").strip()
    if device_choice.isdigit():
        recorder.set_input_device(int(device_choice))

    print("Record manually (press Ctrl+C to stop)\n")
    recorder = VoiceRecorder( filename="manual_recording.wav")
    recorder.start()
    try:
        while True:
            time.sleep(0.5)
            print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\nStopping recording...")
        recorder.stop_recording()
    recorder.join()
    recorder.cleanup()

