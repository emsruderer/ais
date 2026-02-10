"""direct audio output using PyAudio """

import json
from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
import pyaudio


SAMPLE_RATE = 44100  # Standard CD-quality sample rate
CHUNKSIZE = 1024

# Load your audio file (MP3, WAV, etc.)
# Convert to mono to keep things simple
# Normalize the waveform to range [-1, 1]

GETALLEN_PATH = "./getallen_44100.wav"
getallen_segment = AudioSegment.from_file(GETALLEN_PATH) +4
getallen = getallen_segment.set_channels(1)
getallen = np.array(getallen_segment.get_array_of_samples()).astype(np.float32)
getallen = getallen[SAMPLE_RATE*1:]
getallen /= np.max(np.abs(getallen))
silent = np.zeros(int(SAMPLE_RATE*0.1), dtype=np.float32)

honderdtallen = getallen[CHUNKSIZE*5550:]


# Extract raw audio waarschuwing as a NumPy array
WARNING_PATH = "./waarschuwing.wav"
waarschuwing_segment = AudioSegment.from_file(WARNING_PATH) -6
waarschuwing = waarschuwing_segment.set_channels(1)
waarschuwing = np.array(waarschuwing_segment.get_array_of_samples()).astype(np.float32)
waarschuwing /= np.max(np.abs(waarschuwing))

# Get sample rate (frames per second)
sample_rate = waarschuwing_segment.frame_rate

# Print summary
print(f"Audio duration: {len(waarschuwing)/sample_rate:.2f} seconds")
print(f"Sample rate: {sample_rate} Hz")

# Plot waveform using matplotlib
def plot_waveform(waarschuwing, sample_rate = SAMPLE_RATE):
    plt.figure(figsize=(12, 4))
    plt.plot(waarschuwing, color='slateblue')
    plt.title("Original Audio Waveform")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Initialize PyAudio
p = pyaudio.PyAudio()


for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(f"Device {i}: {dev['name']} (Output: {dev['maxOutputChannels'] > 0})")

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=SAMPLE_RATE,
    output=True,
    output_device_index=1  # Uncomment to use a specific device
)
CHUNKSIZE = 1024
num_chunks1 = len(waarschuwing) // CHUNKSIZE + 1

print(f"Total chunks: {num_chunks1} (full)")
SHOW_WAVEFORM = True

def create_audio_chunks(stream, s, index):
    """ Play a chunk of audio waarschuwing from start to end """
    #for (start,end) in index:
    b = index[0] * CHUNKSIZE
    e = index[1] * CHUNKSIZE
    chunk = s[b:e]
    print(f"Playing getal {index[0]}..{index[1]}")
    if SHOW_WAVEFORM:
        plot_waveform(chunk)
    return np.concatenate([chunk,silent])



INDEX_TIEP = 1
INDEX_AFSTAND =  3
INDEX_CPA = 5
INDEX_TCPA = 7
INDEX_PEILING = 9
INDEX_SNELHEID = 11

with open("warn.json", "r", encoding="utf-8") as f:
    index_warn = json.load(f)

with open("index_0.json", "r", encoding="utf-8") as f:
    index_0 = json.load(f)
with open("index_100.json", "r", encoding="utf-8") as f:
    index_100 = json.load(f)

SHOW_WAVEFORM = False
#plot_waveform(waarschuwing, SAMPLE_RATE)

#play_audio_chunks(stream, getallen, index[1])
chunks0 = create_audio_chunks(stream, waarschuwing, index_warn[0]) # waarschuwoing 1..110
chunks1 = create_audio_chunks(stream, waarschuwing, index_warn[1]) # type
chunks2 = create_audio_chunks(stream, waarschuwing, index_warn[2]) # afstand
chunks3 = create_audio_chunks(stream, honderdtallen, index_100[8]) # 100 meter
chunks4 = create_audio_chunks(stream, waarschuwing, index_warn[4]) # cpa
chunks5 = create_audio_chunks(stream, getallen, index_0[75]) # .. meter
chunks6 = create_audio_chunks(stream, waarschuwing, index_warn[6]) # tcpa
chunks7 = create_audio_chunks(stream, getallen, index_0[60]) # .. minuten
chunks8 = create_audio_chunks(stream, waarschuwing, index_warn[8]) # peiling
chunks9 = create_audio_chunks(stream, getallen, index_0[90]) #  .. graden
chunks10 = create_audio_chunks(stream, waarschuwing, index_warn[10]) # snelheid
chunks11 = create_audio_chunks(stream, getallen, index_0[25]) # 15 knopen
chunks12 = create_audio_chunks(stream, waarschuwing, index_warn[12]) # einde waarschuwing

chunks = np.concatenate([chunks0, chunks1, chunks2, chunks3, chunks4, chunks5,\
                        chunks6, chunks7, chunks8, chunks9, chunks10, chunks11, chunks12])

rij = (chunks * 32767).astype(np.int16).tobytes()
stream.write(rij)

plot_waveform(chunks, SAMPLE_RATE)

stream.stop_stream()
stream.close()
p.terminate()