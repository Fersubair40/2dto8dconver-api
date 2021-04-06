import numpy as np
from tqdm import tqdm
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
from argparse import ArgumentParser
from  os import  system
from sys import argv

reverberance = 50
SECONDS = 3500
MIN_FADE_VOL = -15.0
FADE_TIME = 1000


def convert(inputfile, outputfile, period):
    if period < 0:
        period = period * (-1)
    elif period == 0:
        period = 200
    audio = AudioSegment.from_file(inputfile, format='mp3')
    audio = audio + AudioSegment.silent(duration=SECONDS)
    left = audio.pan(-1)
    right = audio.pan(1)
    faded_left = AudioSegment.silent(duration=0)
    faded_right = AudioSegment.silent(duration=0)
    fileinfo = MP3(inputfile, ID3=EasyID3)

    i = 0

    while len(faded_left) < len(audio):
        faded_left += left[i:i + SECONDS - FADE_TIME].fade(from_gain=MIN_FADE_VOL, start=0,
                                                           duration=SECONDS - FADE_TIME)
        faded_left += left[i + SECONDS - FADE_TIME:i + SECONDS]
        i += SECONDS
        faded_left += left[i:i + SECONDS - FADE_TIME].fade(to_gain=MIN_FADE_VOL, start=0, duration=SECONDS - FADE_TIME)
        faded_left += left[i + SECONDS - FADE_TIME:i + SECONDS] + MIN_FADE_VOL
        i += SECONDS

    i = 0

    while len(faded_right) < len(audio):
        faded_right += right[i:i + SECONDS - FADE_TIME].fade(to_gain=MIN_FADE_VOL, start=0,
                                                             duration=SECONDS - FADE_TIME)
        faded_right += right[i + SECONDS - FADE_TIME:i + SECONDS] + MIN_FADE_VOL
        i += SECONDS
        faded_right += right[i:i + SECONDS - FADE_TIME].fade(from_gain=MIN_FADE_VOL, start=0,
                                                             duration=SECONDS - FADE_TIME)
        faded_right += right[i + SECONDS - FADE_TIME:i + SECONDS]
        i += SECONDS

    eightD = AudioSegment.empty()
    pan = 0.9 * np.sin(np.linspace(0, 2 * np.pi, period))
    chunks = list(enumerate(audio[::100]))

    for i, chunk in tqdm(chunks, desc='Converting', unit='chunks', total=len(chunks)):
        if len(chunk) < 100:
            continue
        newChunk = chunk.pan(pan[i % period])
        eightD = eightD + newChunk

    final = faded_right.overlay(faded_left)
    final = final[:len(audio[:-SECONDS])]

    final.export(outputfile, format='mp3')


# def tags(info):
#     ret = dict()
#     ret['title'] = info['title'][0]
#     ret['album'] = info['album'][0]
#     ret['artist'] = info['artist'][0]
#     ret['genre'] = info['genre'][0]
#     return ret


if __name__ == '__main__':
    parser = ArgumentParser(description='Convert to 8D.')
    parser.add_argument('-i', type=str, required=True, help='input file')
    parser.add_argument('-o', type=str, default=parser.parse_args().i[:-4] + ' - 8D.mp3',
                        help='output file (default: fileName - 8D.mp3)')
    parser.add_argument('-period', type=int, default=200, help='panning period (default: 200)')
    args = parser.parse_args()

    convert(args.i, args.o, args.period)
