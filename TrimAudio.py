
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os


def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)

def SilenceTrimmer(File,directory):
    # Load your audio.
    song = AudioSegment.from_mp3(File)

    # Split track where the silence is 2 seconds or more and get chunks using 
    # the imported function.
    chunks = split_on_silence (
        # Use the loaded audio.
        song, 
        # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
        min_silence_len = 10000,
        # Consider a chunk silent if it's quieter than -16 dBFS.
        # (You may want to adjust this parameter.)
        silence_thresh = song.dBFS-10,
        seek_step=100,
        keep_silence=1000
    )
    print("\nExporting chunks to "+str(directory))
    # Process each chunk with your parameters
    for i, chunk in enumerate(chunks):
        # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
        silence_chunk = AudioSegment.silent(duration=500)

        # Add the padding chunk to beginning and end of the entire chunk.
        audio_chunk = silence_chunk + chunk + silence_chunk

        # Normalize the entire chunk.
        normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

        # Export the audio chunk with new bitrate.
        
        normalized_chunk.export(
            os.path.join(str(directory),"chunk{0}.mp3".format(i)),
            bitrate = "192k",
            format = "mp3"
        )


def OneClipTrimmer(File,directory):
    # Load your audio.
    song = AudioSegment.from_mp3(File)

    # Split track where the silence is 2 seconds or more and get chunks using 
    # the imported function.
    chunks = split_on_silence (
        # Use the loaded audio.
        song, 
        # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
        min_silence_len = 10000,
        # Consider a chunk silent if it's quieter than -16 dBFS.
        # (You may want to adjust this parameter.)
        silence_thresh = song.dBFS-10,
        seek_step=100,
        keep_silence=1000
    )
    print("\nExporting chunks to "+str(directory))
    FinalClip=AudioSegment.silent(duration=500)
    for i in chunks:
        silence_chunk = AudioSegment.silent(duration=500)
        audio_chunk = silence_chunk + i + silence_chunk
        normalized_chunk = match_target_amplitude(audio_chunk, -20.0)
        FinalClip=FinalClip+normalized_chunk
    FinalClip.export(
        os.path.join(str(directory),"VoicesNoSilence.mp3".format(i)),
        bitrate = "192k",
        format = "mp3"
    )