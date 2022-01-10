#!/usr/bin/env python
# coding: utf-8

import pandas as pd

def remove_duplicates(stimuli_df):
    stimuli_df = stimuli_df.drop_duplicates(['Stimuli_Onset', 'Stimuli_Offset'], keep='first', ignore_index=True)
    return stimuli_df

def remove_empty_breaks(stimuli_df, column_words, column_syllables):
    stimuli_df = stimuli_df[stimuli_df[column_words].map(len) != 0]
    stimuli_df = stimuli_df[stimuli_df[column_syllables].map(len) != 0]
    stimuli_df = stimuli_df.reset_index(drop=True)
    return stimuli_df

def retrieve_word_syll_pos(list_syll, list_words):
    new_words = []
    t=0
    for i in range(len(list_syll)):
        if list_syll[i][1] in [t[1] for t in list_words]:
            new_words.append((list_words[t][0], list_words[t][1], list_words[t][2], list_syll[i][3]))
            t+= 1
    return new_words
            

def get_correct_syllables(stimuli_df):
    
    # first remove the syllables  which arent syllables
    stimuli_df["Syllables_in_Stimuli_corr"] = stimuli_df["Syllables_in_Stimuli"].apply(lambda x: [t for t in x if t[2] == "syl"][1:-2]) # take only 'syll' tokens, after minus first+last
    stimuli_df["Syllables_in_Stimuli_corr"] = stimuli_df["Syllables_in_Stimuli_corr"].apply(lambda x: [(t[0], t[1], t[2], s+1) for s,t in enumerate(x) ]) # take only 'syll' tokens, after minus first+last

    # remove words with offsets before first syll offset and after last syll onset
    #stim_rem_dupls["Words_in_Stimuli_corr"] = stim_rem_dupls.apply(lambda x: [t for t in x.Words_in_Stimuli if t[1] >= x.Syllables_in_Stimuli_corr[0][1] and t[0] <= x.Syllables_in_Stimuli_corr[-1][0]], axis=1)
    stimuli_df["Words_in_Stimuli_corr"] = stimuli_df.apply(lambda x: [t for t in x.Words_in_Stimuli if t[1] >= x.Syllables_in_Stimuli_corr[0][1] and t[0] <= x.Syllables_in_Stimuli_corr[-1][0] and t[2] != "__"], axis=1)
    stimuli_df["Words_in_Stimuli_corr"] = stimuli_df.apply(lambda x: retrieve_word_syll_pos(x.Syllables_in_Stimuli_corr, x.Words_in_Stimuli_corr) , axis=1)
    
    # take syllables with offsets different than word offsets 
    stimuli_df["Syllables_in_Stimuli_corr_final"] = stimuli_df.apply(lambda x: [t for t in x.Syllables_in_Stimuli_corr if t[1] not in [y[1] for y in x.Words_in_Stimuli_corr]], axis=1 )
    stimuli_df = stimuli_df.drop("Syllables_in_Stimuli_corr", axis=1)

    return stimuli_df


# run remove_empty_breaks() again
"""Syllables which have offsets also present in the word offsets are removed. 
If a syllable offset is also a word offset, the syllable is only a natural option (between words),
not a natural option (within words)."""
#stim_rem_dupls[stim_rem_dupls['Syllables_in_Stimuli_corr'].map(len) == 1]


# run remove_empty_breaks() again
"""Syllables which have offsets also present in the word offsets are removed. 
If a syllable offset is also a word offset, the syllable is only a natural option (between words),
not a natural option (within words)."""
#remove_empty_breaks(stimuli_df)

"""When we remove the between words options from the syllables, there might be some stimuli which are left
with no option for an unnatural position (say, if all the words in the stimuli are monosyllabic), thus we remove those
which have no syllable options left (no unnatural options left)"""
#stim_rem_dupls[stim_rem_dupls['Syllables_in_Stimuli_corr_final'].map(len) == 0]
#stim_rem_dupls=stim_rem_dupls[stim_rem_dupls['Syllables_in_Stimuli_corr_final'].map(len) != 0]


def get_lexical_pool(stimuli_df):
    
    lexical_pool_df_unnatural= stimuli_df.explode(['Syllables_in_Stimuli_corr_final']).drop(['Words_in_Stimuli', 'Words_in_Stimuli_corr', 'Syllables_in_Stimuli'],axis=1)
    lexical_pool_df_unnatural['Stimuli_details']=lexical_pool_df_unnatural['Syllables_in_Stimuli_corr_final']
    lexical_pool_df_unnatural['Correct'] = 'Unnatural'
    lexical_pool_df_natural= stimuli_df.explode(['Words_in_Stimuli_corr']).drop(['Syllables_in_Stimuli_corr_final','Words_in_Stimuli', 'Syllables_in_Stimuli'],axis=1)
    lexical_pool_df_natural['Stimuli_details']=lexical_pool_df_natural['Words_in_Stimuli_corr']
    lexical_pool_df_natural['Correct'] = 'Natural'
    
    return lexical_pool_df_unnatural, lexical_pool_df_natural                                                 


def ensure_same_number_of_unique_pairs(lexical_pool_df_natural,lexical_pool_df_unnatural):
    if sorted(lexical_pool_df_natural[lexical_pool_df_natural['Correct']=='Natural'].index.unique()) == sorted(lexical_pool_df_unnatural[lexical_pool_df_unnatural['Correct']=='Unnatural'].index.unique()):
        return True
    else:
        print('The number of unique pair indexes does not match. This can mean two things: either there are more unique indexes in the natural pool or in the unnatural pool. If there are more unique indexes in the natural pool, there are some unique indexes that are missing in the unnatural pool (in the syllable break pool). If so, this could be due to a stimuli with all monosyllabic words.')
        

def append_natural_and_unnatural_pools(lexical_pool_df_natural,lexical_pool_df_unnatural):
    if ensure_same_number_of_unique_pairs(lexical_pool_df_natural,lexical_pool_df_unnatural) == True:
        lexical_pool_df = lexical_pool_df_unnatural.append(lexical_pool_df_natural, ignore_index=False)
        lexical_pool_df['Unique_Indexes'] = lexical_pool_df.index
        lexical_pool_df=lexical_pool_df.reset_index(drop=True)
        return lexical_pool_df
    else:
        print('Function ensure_same_number_of_unique_pairs() did not return True, which means the unique pairs in both of the pools do not match. They need to match in order to merge them.')

def determine_syllable_and_break_positions(lexical_pool_df):
    lexical_pool_df["Syll_Pos_from_Onset"] = lexical_pool_df.apply(lambda x:x.Stimuli_details[3], axis=1) #if type(x.Stimuli_details)!=float else False, axis=1)
    lexical_pool_df["Syll_Pos_from_Offset"] = lexical_pool_df.Syllable_Count_in_Stimuli - lexical_pool_df.Syll_Pos_from_Onset
    lexical_pool_df['Offsets'] = lexical_pool_df.apply(lambda x: x.Stimuli_details[1], axis=1)
    lexical_pool_df["Second_from_Onset"] = lexical_pool_df.Offsets-lexical_pool_df.Stimuli_Onset
    lexical_pool_df["Second_from_Offset"] = lexical_pool_df.Stimuli_Offset-lexical_pool_df.Offsets
    
    return lexical_pool_df


def pool_dictionary(): # create dictionary to store extracted values
    pool_dict = {'Pair_Index':list, 'Second_Break_to_Onset':list, 'Second_Break_to_Offset':list, 'Position_from_Onset':list, 'Position_from_Offset':list, 'Total_Num_of_Syllables':list, 'Total_Num_of_Words':list,'Correct':list, 'Task': list}
    return pool_dict # dictionary will be converted into Pandas Dataframe


def pool_dataframe(pool_dict, pair_index, second_break_to_onset, second_break_to_offset, position_from_onset, position_from_offset, syllable_total, word_total, correct, task):
    pool_dict['Pair_Index'] = pair_index
    pool_dict['Second_Break_to_Onset'] = second_break_to_onset
    pool_dict['Second_Break_to_Offset'] = second_break_to_offset
    pool_dict['Position_from_Onset'] = position_from_onset
    pool_dict['Position_from_Offset'] = position_from_offset
    pool_dict['Total_Num_of_Syllables'] = syllable_total
    pool_dict['Total_Num_of_Words'] = word_total
    pool_dict['Correct'] = correct
    pool_dict['Task'] = task
    pool_df = pd.DataFrame.from_dict(pool_dict)
    return pool_df



def add_extra_columns_for_more_stats(lexical_task_pool):
    lexical_task_pool['Syllables_before_Break'] = lexical_task_pool.Total_Num_of_Syllables-lexical_task_pool.Position_from_Offset
    lexical_task_pool['Syllables_after_Break'] = lexical_task_pool.Total_Num_of_Syllables-lexical_task_pool.Position_from_Onset
    return lexical_task_pool


def create_lexical_pool():
    stimuli_df = get_correct_syllables(remove_empty_breaks(remove_duplicates(stimuli), 'Words_in_Stimuli', 'Syllables_in_Stimuli'))
    stimuli_df_final= remove_empty_breaks(stimuli_df, 'Words_in_Stimuli_corr', 'Syllables_in_Stimuli_corr_final')
    lexical_pool_df_unnatural, lexical_pool_df_natural = get_lexical_pool(stimuli_df_final)
    lexical_pool_df = determine_syllable_and_break_positions(append_natural_and_unnatural_pools(lexical_pool_df_natural, lexical_pool_df_unnatural))
    lexical_pool_dict = pool_dictionary()
    lexical_task_pool = pool_dataframe(lexical_pool_dict, lexical_pool_df.Unique_Indexes,
                                       lexical_pool_df.Second_from_Onset, lexical_pool_df.Second_from_Offset,
                                       lexical_pool_df.Syll_Pos_from_Onset, lexical_pool_df.Syll_Pos_from_Offset,
                                       lexical_pool_df.Syllable_Count_in_Stimuli, lexical_pool_df.Word_Count_in_Stimuli,
                                       lexical_pool_df.Correct, task='Lexical')
    return lexical_task_pool

if __name__ == "__main__":

    import argparse, os
    from create_initial_stimuli_dataframe import create_dataframe as initial_df

    parser = argparse.ArgumentParser(description='Read in a file or set of files.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('paths', nargs='+', help='Give paths to all files.')
    args = parser.parse_args()

    # Parse paths
    brk_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.brk'])
    phn_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.phn'])
    syl_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.syl'])
    wrd_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.wrd'])
    wav_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.wav'])

    # print(brk_files)
    stimuli = initial_df(phn_files, brk_files, syl_files, wrd_files, wav_files)
    lexical_task_pool = create_lexical_pool()
    lexical_task_pool.to_csv(os.path.join(os. getcwd(),'lexical_task_pool.csv'))