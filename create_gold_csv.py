#!/usr/bin/env python
# coding: utf-8

from extract_stimuli_pairs import read_csv
import pandas as pd

def create_gold_csv(initial_stimuli, chosen_stimuli):
    csv_df = pd.DataFrame(columns=['id','filename','voice','type','subtype','correct','transcription'])
    for stimuli in chosen_stimuli:



if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Read in a file or set of files.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('initial_pairs', type=str, help='Give path to csv with initial stimuli dataframe')
    parser.add_argument('chosen_pairs', type=str, help='Give path to csv with chosen stimuli pairs (after loss).')
    parser.add_argument('outdir', type=str, help='Give path to save csv in files where final stimuli pairs are stored')
    args = parser.parse_args()
