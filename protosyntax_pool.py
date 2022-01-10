#!/usr/bin/env python
# coding: utf-8

import pandas as pd


def remove_duplicates(stimuli_df):
    stimuli_df = stimuli_df.drop_duplicates(['Stimuli_Onset', 'Stimuli_Offset'], keep='first', ignore_index=True)
    return stimuli_df


def remove_empty_breaks(stimuli_df):
    stimuli_df = stimuli_df[
        stimuli_df['Unnatural_Breaks'].map(len) != 0]  # drop rows which have empty unnatural breaks
    stimuli_df = stimuli_df[stimuli_df['Natural_Break_Second'].map(len) != 0]
    stimuli_df = stimuli_df.reset_index(drop=True)
    return stimuli_df


def remove_first_last_syllables(stimuli_df):
    # first remove the syllables  which aren't syllables
    stimuli_df.drop(columns=['Syllables_in_Stimuli'])
    stimuli_df["Syllables_in_Stimuli"] = stimuli_df["Syllables_in_Stimuli"].apply(
        lambda x: [t for t in x][1:-2])  # take only 'syll' tokens, after minus first+last
    stimuli_df["Syllables_in_Stimuli"] = stimuli_df["Syllables_in_Stimuli"].apply(
        lambda x: [(t[0], t[1], t[2], s + 1) for s, t in
                   enumerate(x)])  # take only 'syll' tokens, after minus first+last
    stimuli_df["Words_in_Stimuli"] = stimuli_df.apply(lambda x: [t for t in x.Words_in_Stimuli if
                                                                 t[1] >= x.Syllables_in_Stimuli[0][1] and t[0] <=
                                                                 x.Syllables_in_Stimuli[-1][0]], axis=1)
    return stimuli_df



def remove_natural_breaks_outside_syllable_limits(stimuli_df):
    natural_breaks_outside_limits = []
    for i, stimuli in enumerate(stimuli_df['Syllables_in_Stimuli']):
        syllable_offsets = [elem[1] for idx, elem in enumerate(stimuli)]
        # print(syllable_offsets)
        for idx, natural_break in enumerate(stimuli_df['Natural_Break_Second']):
            if i == idx:
                if natural_break[0] not in syllable_offsets:
                    natural_breaks_outside_limits.append(idx)
    stimuli_df = stimuli_df.drop(natural_breaks_outside_limits, axis=0)
    return stimuli_df



def remove_unnatural_breaks_outside_syllable_limits(stimuli_df):
    unnatural_breaks_correct_limits = []
    for idx, unnatural_breaks in enumerate(stimuli_df['Unnatural_Breaks']):
        unnatural_breaks_correct = []
        for unnatural in unnatural_breaks:
            for i, stimuli in enumerate(stimuli_df['Syllables_in_Stimuli']):
                if idx == i:
                    syllable_offsets = [elem[1] for idx, elem in enumerate(stimuli)]
                    # print(word_offsets)
                    if unnatural in syllable_offsets:
                        # print('offsets', syllable_offsets)
                        unnatural_breaks_correct.append(unnatural)
        unnatural_breaks_correct_limits.append(unnatural_breaks_correct)
    stimuli_df['Unnatural_Breaks'] = unnatural_breaks_correct_limits
    return stimuli_df



def extract_details_for_protosyntax_pool(stimuli_df):
    ps_prosodic_break_details = []

    """ extract unnatural and natural breaks with pair_index and correspoding label """
    for x, y in enumerate(stimuli_df['Stimuli_Onset']):
        for i, elements in enumerate(stimuli_df['Unnatural_Breaks']):
            if i == x:
                for elem in elements:
                    ps_prosodic_break_details.append([x, elem, 'Unnatural'])
        for i, elements in enumerate(stimuli_df['Natural_Break_Second']):
            if i == x:
                for elem in elements:
                    ps_prosodic_break_details.append([x, elem, 'Natural'])

    """ protosyntax_break_position_to_onset """
    for x, syllables in enumerate(stimuli_df['Syllables_in_Stimuli']):
        pos = 0
        for y, syll in enumerate(syllables):
            pos += 1  # increase count for each syllable in the current stimuli
            for i, elements in enumerate(stimuli_df['Unnatural_Breaks']):
                if x == i:  # do something only if it's the same pair index for both df columns
                    for y, elems in enumerate(elements):
                        if elems == syll[1]:  # check that the unnatural break is an offset of the syllable
                            for a, pros_breaks in enumerate(ps_prosodic_break_details):
                                if pros_breaks[0] == x and pros_breaks[1] == elems and pros_breaks[2] == 'Unnatural':
                                    pros_breaks.append(pos)
            for idx, items in enumerate(stimuli_df['Natural_Break_Second']):
                if x == idx:
                    for w, item in enumerate(items):
                        if item == syll[1]:
                            for a, pros_breaks in enumerate(ps_prosodic_break_details):
                                if pros_breaks[0] == x and pros_breaks[1] == item and pros_breaks[2] == 'Natural':
                                    pros_breaks.append(pos)

    """ add syllable count corresponding to each break """
    for ids, syllable_total in enumerate(stimuli_df['Syllable_Count_in_Stimuli']):
        # print(ids,syllable_total)
        for i, elements in enumerate(ps_prosodic_break_details):
            if elements[0] == ids:
                elements.append(syllable_total)

    """ protosyntax_second_break_to_offset """
    for a, b in enumerate(stimuli_df['Stimuli_Offset']):
        for i, elements in enumerate(ps_prosodic_break_details):
            if elements[0] == a:
                elements.append(b - elements[1])

    """ protosyntax_second_break_to_onset """
    for a, b in enumerate(stimuli_df['Stimuli_Onset']):
        for i, elements in enumerate(ps_prosodic_break_details):
            if elements[0] == a:
                elements.append(elements[1] - b)

    """ protosyntax_break_position_to_onset """
    for i, item in enumerate(ps_prosodic_break_details):
        item.append(item[4] - item[3])

    """ protosyntax_label """
    for item in ps_prosodic_break_details:
        item.append('Protosyntax')

    return ps_prosodic_break_details



def break_down_protosytax_pool_data(protosyntax_pool_data):
    ps_pair_index = [elem[0] for elem in protosyntax_pool_data]
    ps_prosodic_break = [elem[1] for elem in protosyntax_pool_data]
    ps_correct = [elem[2] for elem in protosyntax_pool_data]
    ps_position_offset = [elem[3] for elem in protosyntax_pool_data]
    ps_total_sylls = [elem[4] for elem in protosyntax_pool_data]
    ps_second_break_to_offset = [elem[5] for elem in protosyntax_pool_data]
    ps_second_break_to_onset = [elem[6] for elem in protosyntax_pool_data]
    ps_position_onset = [elem[7] for elem in protosyntax_pool_data]
    ps_task = [elem[8] for elem in protosyntax_pool_data]
    return ps_pair_index, ps_prosodic_break, ps_correct, ps_position_offset, ps_total_sylls, ps_second_break_to_offset, ps_second_break_to_onset, ps_position_onset, ps_task



def pool_dictionary_protosyntax():  # create dictionary to store extracted values
    pool_dict = {'Pair_Index': list, 'Prosodic_Break': list, 'Second_Break_to_Onset': list,
                 'Second_Break_to_Offset': list, 'Position_from_Onset': list, 'Position_from_Offset': list,
                 'Total_Num_of_Syllables': list, 'Correct': list, 'Task': list}
    return pool_dict  # dictionary will be converted into Pandas Dataframe


def pool_dataframe_protosyntax(pool_dict_protosyntax, pair_index, prosodic_break, second_break_to_onset,
                               second_break_to_offset, position_from_onset, position_from_offset, syllable_total,
                               correct, task):
    pool_dict_protosyntax['Pair_Index'] = pair_index
    pool_dict_protosyntax['Prosodic_Break'] = prosodic_break
    pool_dict_protosyntax['Second_Break_to_Onset'] = second_break_to_onset
    pool_dict_protosyntax['Second_Break_to_Offset'] = second_break_to_offset
    pool_dict_protosyntax['Position_from_Onset'] = position_from_onset
    pool_dict_protosyntax['Position_from_Offset'] = position_from_offset
    pool_dict_protosyntax['Total_Num_of_Syllables'] = syllable_total
    pool_dict_protosyntax['Correct'] = correct
    pool_dict_protosyntax['Task'] = task
    pool_df = pd.DataFrame.from_dict(pool_dict_protosyntax)
    return pool_df


def check_same_number_of_unique_pairs(protosyntax_pool_df):
    if sorted(protosyntax_pool_df[protosyntax_pool_df['Correct'] == 'Natural'].Pair_Index.unique()) == sorted(
            protosyntax_pool_df[protosyntax_pool_df['Correct'] == 'Unnatural'].Pair_Index.unique()):
        return True


def create_protosyntax_pool():
    stimuli_df = remove_duplicates(stimuli)
    stimuli_df = remove_empty_breaks(stimuli_df)
    stimuli_df = remove_first_last_syllables(stimuli_df)
    stimuli_df = remove_natural_breaks_outside_syllable_limits(stimuli_df)
    stimuli_df = remove_unnatural_breaks_outside_syllable_limits(stimuli_df)
    stimuli_df = remove_empty_breaks(stimuli_df)
    protosyntax_pool_data = extract_details_for_protosyntax_pool(stimuli_df)
    ps_pair_index, ps_prosodic_break, ps_correct, ps_position_offset, ps_total_sylls, ps_second_break_to_offset, ps_second_break_to_onset, ps_position_onset, ps_task = break_down_protosytax_pool_data(
        protosyntax_pool_data)
    pool_dict_protosyntax = pool_dictionary_protosyntax()
    protosyntax_pool_df = pool_dataframe_protosyntax(pool_dict_protosyntax, ps_pair_index, ps_prosodic_break,
                                                     ps_second_break_to_onset, ps_second_break_to_offset,
                                                     ps_position_onset, ps_position_offset, ps_total_sylls, ps_correct,
                                                     ps_task)
    if check_same_number_of_unique_pairs(protosyntax_pool_df) == True:
        print("The number of unique pairs of Natural and Unnatural Breaks matches!")
        return protosyntax_pool_df
    else:
        print("The number of unique pairs for Natural and Unnatural Breaks does not match. ")


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
    protosyntax_task_pool = create_protosyntax_pool()
    protosyntax_task_pool.to_csv(os.path.join(os.getcwd(), 'protosyntax_task_pool.csv'))
