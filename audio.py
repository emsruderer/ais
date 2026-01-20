
import wave
import pyaudio

# the file name output you want to record into
FILENAME= "recorded.wav"
# set the chunk size of 1024 samples
CHUNK = 1024
# sample format
FORMAT = pyaudio.paInt16
# mono, change to 2 if you want stereof= "recor
CHANNELS    = 1
# 44100 samples per second
SAMPLE_RATE  = 44100
RECORD_SECONDS = 5


def get_audio():
    """initialize PyAudio object"""
    p = pyaudio.PyAudio()
    # open stream object as input & output
    stream = p.open(format=FORMAT,
                    channels = CHANNELS  ,
                    rate=SAMPLE_RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)
    return p, stream

def audio_stop(p):
    """terminate pyaudio object"""
    p.terminate()

def record_audio(stream, record_seconds=RECORD_SECONDS ):
    """
    Docstring for recording

    :param stream: Description
    :param record_seconds: Description
    """
    frames = []
    for i in range(int(SAMPLE_RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        # if you want to hear your voice while recording
        #stream.write(data)
        print(i,end=' ')
        frames.append(data)
    stream.stop_stream()
    stream.close()
    print("Finished recording.")
    return frames



p, s = get_audio()
frames = record_audio(s)
audio_stop(p)
# save audio file
# open the file in 'write bytes' mode
wf = wave.open(FILENAME, "wb")
# set the CHANNELS
wf.setnchannels(CHANNELS)
# set the sample format
wf.setsampwidth(p.get_sample_size(FORMAT))
# set the sample rate
wf.setframerate(SAMPLE_RATE )
# write the frames as bytes
wf.writeframes(b"".join(frames))
# close the file
wf.close()
