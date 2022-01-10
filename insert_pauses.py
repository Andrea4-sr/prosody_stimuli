#!/usr/bin/env python
# coding: utf-8

from pydub import AudioSegment
from extract_stimuli_pairs import read_csv

def dictionary_paths_stimuli(list_stimuli):
    paths_dict={}
    items = [i.split("--") for i in list_stimuli]
    for x, y in zip(list_stimuli, items):
        paths_dict[x] = [int(y[1]), y [2]]
    return paths_dict

def sort_df_columns(df, column):
    return df.sort_values(by=[column],ascending=True)

def insert_pauses(path, pair, second, correct, outdir):

    audio_out_file = outdir+str(pair)+correct+".wav"

    # create 30ms of silence audio segment
    pause = AudioSegment.silent(duration=300)  #duration in milliseconds

    # read wav file to an audio segment
    stimuli = AudioSegment.from_wav(path)

    # read break second in milliseconds
    second = second * 1000

    # Define beg until pause and end after pause
    beg = stimuli[:second].append(pause)
    end = stimuli[second:]

    # Add above two audio segments
    final_stimuli = beg + end
    # Save modified audio
    return final_stimuli.export(audio_out_file, format="wav")

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Read in a file or set of files.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('chosen_pairs', type=str, help='Give path to csv with chosen stimuli pairs (after loss).')
    parser.add_argument('sliced', nargs='+', type=str, help='Give path to where sliced stimuli pairs are saved.')
    parser.add_argument('outdir', type=str, help='Give path to save stimuli with inserted pause')
    args = parser.parse_args()

    chosen_pairs_df = read_csv(args.chosen_pairs)
    chosen_pairs_df = sort_df_columns(chosen_pairs_df, "Pair_Index")
    #print(chosen_pairs_df)

    chosen_pairs = [pair for pair in chosen_pairs_df.Pair_Index]
    #print(len(chosen_pairs_df))

    chosen_pairs_list = [pair for pair in args.sliced] # list of sliced pairs stored
    #print(len(chosen_pairs_list))
    paths_dict = dictionary_paths_stimuli(chosen_pairs_list)
    #print(len(paths_dict))

    for pair, break_second, correct, (paths, num_correct) in zip(chosen_pairs_df.Pair_Index, chosen_pairs_df.Second_Break_to_Onset, chosen_pairs_df.Correct, sorted(paths_dict.items(), key=lambda item: item[1][0], reverse=False)):
        for paths, num_correct in paths_dict.items():
            if pair == num_correct[0] and correct == num_correct[1]:
                #print(pair, paths, num_correct[0], num_correct[1], break_second, correct)
                insert_pauses(paths, pair, break_second, correct, args.outdir)
    # print(len(count))
