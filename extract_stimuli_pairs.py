#!/usr/bin/env python
# coding: utf-8


from pydub import AudioSegment
import pandas as pd

def read_csv(csv):
    return pd.read_csv(csv, sep='\t')

def slice_stimuli(audio, onset, offset, number, correct, savedir):
    # pydub does things in milliseconds
    onset = onset * 1000
    offset = offset * 1000
    wav = AudioSegment.from_wav(audio)

    stimuli = wav[onset:offset]
    return stimuli.export(savedir+'--'+str(number)+'--'+correct+'--'+'--'+'.wav', format='wav')

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Read in a file or set of files.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #parser.add_argument('finalpairs', type=str, help='Give path to csv with chosen stimuli pairs (after loss).')
    parser.add_argument('allstimuli', type=str, help='Give path to csv with all initial stimuli.')
    parser.add_argument('crossfaded', nargs='+', type=str, help='Give path to saved crossfaded audio wavs.')
    parser.add_argument('savedir', type=str, help='Give path to save sliced stimuli.')
    args = parser.parse_args()

    #final_pairs = read_csv(args.finalpairs)
    initial_stimuli = read_csv(args.allstimuli)
    initial_stimuli.drop_duplicates(['Stimuli_Onset', 'Stimuli_Offset'], keep='first', ignore_index=True)

    crossfaded = [audio for audio in args.crossfaded]
    #print(crossfaded)
    for pair, audio, onset, offset in zip(initial_stimuli.index, initial_stimuli.Audio_File, initial_stimuli.Stimuli_Onset, initial_stimuli.Stimuli_Offset):
        if audio[-12:] in [wav[-12:] for wav in crossfaded]:
            slice_stimuli(audio, onset, offset, pair, 'Natural', args.savedir)
            slice_stimuli(audio, onset, offset, pair, 'Unnatural', args.savedir)

