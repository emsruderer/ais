"""
Mel Spectrogram Tutorial
========================
This module demonstrates how to create and visualize Mel spectrograms from audio files.
Mel spectrograms are useful for audio analysis and can be applied to AIS warning audio.

Requires: librosa, matplotlib, numpy
Install: pip install librosa matplotlib numpy
"""
import torch
import torchcodec
import torchaudio

import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt


def load_audio(file_path, sr=22050):
    """
    Load an audio file and return the audio time series and sample rate.

    Args:
        file_path: Path to audio file (e.g., 'call.mp2')
        sr: Target sample rate (default 22050 Hz)

    Returns:
        y: Audio time series
        sr: Sample rate
    """
    y, sr = librosa.load(file_path, sr=sr)
    print(f"Loaded audio: duration={len(y)/sr:.2f}s, sample_rate={sr}Hz")
    return y, sr


def create_mel_spectrogram(y, sr, n_mels=128, fmax=8000):
    """
    Create a Mel spectrogram from audio time series.

    Args:
        y: Audio time series
        sr: Sample rate
        n_mels: Number of Mel bands (default 128)
        fmax: Maximum frequency (default 8000 Hz)

    Returns:
        mel_spec_db: Mel spectrogram in dB scale
    """
    # Compute Mel spectrogram
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, fmax=fmax)

    # Convert to dB scale
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    return mel_spec_db


def visualize_mel_spectrogram(mel_spec_db, sr, hop_length=512):
    """
    Visualize the Mel spectrogram using matplotlib.

    Args:
        mel_spec_db: Mel spectrogram in dB
        sr: Sample rate
        hop_length: Number of samples between frames
    """
    plt.figure(figsize=(12, 6))
    librosa.display.specshow(mel_spec_db, sr=sr, hop_length=hop_length,
                             x_axis='time', y_axis='mel', cmap='viridis')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel Spectrogram')
    plt.xlabel('Time (s)')
    plt.ylabel('Mel Frequency')
    plt.tight_layout()
    plt.show()


def analyze_audio_features(y, sr):
    """
    Extract additional audio features from time series.

    Args:
        y: Audio time series
        sr: Sample rate

    Returns:
        Dictionary of audio features
    """
    # RMS energy
    rms = librosa.feature.rms(y=y)[0]

    # Zero crossing rate
    zcr = librosa.feature.zero_crossing_rate(y)[0]

    # Spectral centroid
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    return {
        'rms_mean': np.mean(rms),
        'zcr_mean': np.mean(zcr),
        'spectral_centroid_mean': np.mean(spectral_centroid)
    }


def main():
    """
    Example usage: Analyze the AIS warning audio file.
    """
    # Load the AIS warning audio (adjust path if needed)
    audio_file = 'training_data/wavs/audio2.wav'

    try:
        y, sr = load_audio(audio_file)
        waveform, sample_rate = torchaudio.load(audio_file)

        print('start transform',chr(0x133), sample_rate )

        transform = torchaudio.transforms.MelSpectrogram(sample_rate=sample_rate,n_mels=256,n_fft=2048,hop_length=512)
        mel_spec = transform(waveform)

        print('mel_spec shape',mel_spec.shape)

        mel_spec_np = mel_spec.squeeze().numpy()
        mel_spec_db = librosa.power_to_db(mel_spec_np, ref=np.max)
        visualize_mel_spectrogram(mel_spec_db, sr)

        # Create Mel spectrogram
        mel_spec_db = create_mel_spectrogram(y, sr)
        print(f"Mel spectrogram shape: {mel_spec_db.shape}")

        # Visualize
        visualize_mel_spectrogram(mel_spec_db, sr)

        # Extract features
        features = analyze_audio_features(y, sr)
        print("\nAudio Features:")
        for key, value in features.items():
            print(f"  {key}: {value:.4f}")

    except FileNotFoundError:
        print(f"Error: Audio file '{audio_file}' not found.")
        print("Generate it first by running: python speech.py")


if __name__ == '__main__':
    main()
