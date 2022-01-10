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
    parser.add_argument('finalpairs', type=str, help='Give path to csv with chosen stimuli pairs (after loss).')
    parser.add_argument('allstimuli', type=str, help='Give path to csv with all initial stimuli.')
    parser.add_argument('savedir', type=str, help='Give path to save sliced stimuli')
    args = parser.parse_args()

    final_pairs = read_csv(args.finalpairs)
    initial_stimuli = read_csv(args.allstimuli)
    initial_stimuli.drop_duplicates(['Stimuli_Onset', 'Stimuli_Offset'], keep='first', ignore_index=True)


    for audio, onset, offset, final_pair in zip(initial_stimuli.Audio_File, initial_stimuli.Stimuli_Onset, initial_stimuli.Stimuli_Offset,  final_pairs.Pair_Index):
        if final_pair in [index for index in initial_stimuli.index]:
            slice_stimuli(audio, onset, offset, final_pair, 'Natural', args.savedir)
            slice_stimuli(audio, onset, offset, final_pair, 'Unnatural', args.savedir)

