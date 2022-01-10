#!/usr/bin/env python
# coding: utf-8

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import os, glob, openpyxl
import pandas as pd

def paths(path):  # given a path
    return glob.glob(path,recursive=True)  # this function returns all paths of all Phonemic Annotation Files with the extension ".lbl" in the project

def identify_brk_file(brk_file):
    brk_file = brk_file[-12:-4]
    return brk_file

def identify_phon_file(phn_file):
    phn_file = phn_file[-12:-4]
    return phn_file

def identify_audio_file(brk_file):
    audio_file = brk_file[-12:-4]
    return audio_file

def identify_sylfile(syl_file):
    syl_file = syl_file[-12:-4]
    return syl_file

def identify_wrdfile(wrd_file):
    wrd_file = wrd_file[-12:-4]
    return wrd_file

def identify_speaker(file):  # identify speaker of file passed
    speaker = file[0:3]
    return speaker

def identify_study_phase(file):  # identify study phase of file passed
    study_phase = file[-7]
    if study_phase != 'l':  # there are possibilities, "Labnews" or "Radio"
        study_phase = 'r'  # labelled sentences as part of the "Radio" study phase
    return study_phase

def read_prosodic_break_file(brk_file):  # read the file of Prosodic Annontated Breaks into a Pandas Dataframe
    df = pd.read_csv(brk_file, sep='\s+', header=None, names=['Onset', 'Prosodic Break Annotation'])
    return df

def read_phonemic_anno_file(phonemic_anno_file_path):  # read the file of Phonemic Annontated into a Pandas Dataframe
    df = pd.read_csv(phonemic_anno_file_path, sep='\s+', header=None, names=['Onset', 'Offset', 'Phonemic Annotation'], encoding='latin-1')
    return df

def read_word_file(wrd_file):  # read the file of Annontated Words into a Pandas Dataframe
    df = pd.read_csv(wrd_file, sep='\s+', header=None, names=['Onset', 'Offset', 'Annotated Word'], encoding='latin-1')
    return df

def read_syll_file(syll_file):  # read the file of Annontated Words into a Pandas Dataframe
    df = pd.read_csv(syll_file, sep='\s+', header=None, names=['Onset', 'Offset', 'Syllable'], encoding='latin-1')
    return df



def extract_idx_annotation_tuples(brk_df,
                                  phn_df):  # extract tuples of Dataframe indexes and their corresponding annotation
    index_pros_anno = []
    index_phon_anno = []
    index_break = brk_df.index
    index_phon = phn_df.index
    for row, anno in zip(index_break, brk_df['Prosodic Break Annotation']):
        index_pros_anno.append((row, anno))
    for row, anno in zip(index_phon, phn_df['Phonemic Annotation']):
        index_phon_anno.append((row, anno))
    return index_pros_anno, index_phon_anno  # returns list of tuples with structure [(df index, annotation),...]



def extract_index_seconds_tuples(pros_break_anno_df,
                                 phone_anno_df):  # extract tuples of Dataframe Indexes and their corresponding second
    index_pros_second = []
    index_phon_second = []
    index_break = pros_break_anno_df.index
    index_phon = phone_anno_df.index
    for row, onset in zip(index_break, pros_break_anno_df['Onset']):
        index_pros_second.append((row, onset))
    for row, onset, offset in zip(index_phon, phone_anno_df['Onset'], phone_anno_df['Offset']):
        index_phon_second.append((row, onset, offset))
    return index_pros_second, index_phon_second  # returns list of tuples with structure [(df index, second), ...]


def extract_sec_word_tuples(word_df):  # extract tuples of Dataframe indexes and their corresponding annotation
    onset_offset_word = []
    for onset, offset, word in zip(word_df['Onset'], word_df['Offset'], word_df['Annotated Word']):
        onset_offset_word.append((onset, offset, word))
    return onset_offset_word  # returns list of tuples with structure [(df index, annotation),...]



def extract_sec_syll_tuples(syll_df):  # extract tuples of Dataframe indexes and their corresponding annotation
    onset_offset_syllable = []
    for onset, offset, syllable in zip(syll_df['Onset'], syll_df['Offset'], syll_df['Syllable']):
        onset_offset_syllable.append((onset, offset, syllable))
    return onset_offset_syllable  # returns list of tuples with structure [(df index, annotation),...]



def create_sec_anno_tuples(index_pros_anno, index_phon_anno, index_pros_second,
                           index_phon_second):  # create tuple of each second with its corresponding annotation based on same index
    sec_pros_break = []
    sec_phone = []
    for i, i_anno_tuple in enumerate(index_pros_anno):
        for idx, idx_sec_tuple in enumerate(index_pros_second):
            if i == idx:
                sec_pros_break.append((idx_sec_tuple[1], i_anno_tuple[1]))
    for i, i_phon_tuple in enumerate(index_phon_anno):
        for idx, idx_sec_tuple in enumerate(index_phon_second):
            if i == idx:
                sec_phone.append((idx_sec_tuple[1], idx_sec_tuple[2], i_phon_tuple[1],))
    return sec_pros_break, sec_phone  # returns list of tuples with structure [(second, annotation), ...]



def limited_by_four(sec_pros_break):  # extract groups of rows such that the group has a Prosodic Break of level '4' as the first and last element
    new_group = []
    groups = []
    for tupl in sec_pros_break:
        if tupl[1] == 4:
            new_group.append(tupl)
            new_group = [tupl]
            groups.append(new_group)
        else:
            new_group.append(tupl)

    return groups  # returns list of lists, each nested list is a stimuli group limited by Prosodic Breaks of level '4'



def middle_break_3(limit_four):  # given each group returned in def limited_by_four(sec_pros_break)
    stimuli_three = []
    for tupl in limit_four:
        lc = [elem[1] for elem in tupl]
        if lc.count(3) == 1:
            stimuli_three.append(tupl)
    return stimuli_three  # returns list of lists of only those groups which had ONE Prosodic Break of level '3'



def three_fours(
        sec_pros_break):  # extract groups of rows such that the group has  a Prosodic Break Level '4' on the rightmost and leftmost and in the middle
    new_group_4_4_4 = []
    final_groups_4_4_4 = []
    store = False
    for tupl in sec_pros_break:  # iterate over tuple(second, prosodic_break_annotation) in sec_pros_break list
        if tupl[1] == 4:  # if pros_break_annotation is '4' or '4-'
            store = True
            new_group_4_4_4.append(tupl)  # append the tuple to the list new_group
            lc = [elem[1] for elem in
                  new_group_4_4_4]  # list comprehension of the prosodic_annotations in each new_group
            if lc.count(4) == 3:  # check if there are exactly three '4' + '4-' breaks
                assert new_group_4_4_4[0][1] == 4, (new_group_4_4_4)
                assert new_group_4_4_4[0][-1] == 4, (new_group_4_4_4)
                final_groups_4_4_4.append(new_group_4_4_4)  # append the finished group to final_groups
                count = 0  # initialise a count for prosodic annotations found
                index = 0  # initialise index
                for idx, item in enumerate(new_group_4_4_4):  # iterate over indexes, tuple(sec,annotation)
                    if item[1] == 4:
                        count += 1
                    if count == 2:
                        index = idx
                        break
                new_group_4_4_4 = new_group_4_4_4[index:]
            continue
        if store:
            new_group_4_4_4.append(tupl)
    return final_groups_4_4_4



def middle_break_4(groups_4):  # check that stimuli Groups '4-4-4' do not have a Prosodic Break Level '3' as well
    final_groups = []
    for group in groups_4:
        lc = [elem[1] for elem in group]
        if lc.count(3) == 0:
            final_groups.append(group)
    return final_groups



def stimuli_length(stimuli):  # verify that the length of the stimuli is at least 3 seconds and maximum 5 seconds
    final_groups = []
    for item in stimuli:
        # if item[-1][0] - item[0][0] < 5.0:
        if item[-1][0] - item[0][0] < 5.0 and item[-1][0] - item[0][0] > 2.0:
            final_groups.append(item)
    return final_groups



def stimuli(secs_phn, good_len_groups):
    stimuli = []
    pause = 0
    for group in good_len_groups:
        for i, label in enumerate(secs_phn):
            if secs_phn[i][2] == 'PAU':
                pause_onset = secs_phn[i][0]
                pause_offset = secs_phn[i][1]
                if pause_onset >= group[0][0] and pause_offset <= group[-1][0]:
                    pause = secs_phn[i][1] - secs_phn[i][0]
                    stimuli.append([group, pause_onset, pause_offset])
    return stimuli



def natural_unnatural_breaks(stimuli):
    natural = []
    unnatural = []

    for i, group in enumerate(stimuli):
        N = []
        U = []
        for data in stimuli[i][0]:
            if data[1] == 3 or data[1] == 4:
                if data != stimuli[i][0][0] and data != stimuli[i][0][-1]:
                    N.append(data[0])
            if data[1] == 1:
                U.append(data[0])
        natural.append(N)
        unnatural.append(U)

    return natural, unnatural



def position_counts(natural, unnatural):
    natural_pos = []
    unnatural_pos = []
    for item in natural:
        natural_pos.append(len(item))
    for elem in unnatural:
        unnatural_pos.append(len(elem))
    return natural_pos, unnatural_pos



def words_in_sti(stimuli, words):
    words_all_stimuli = []

    for stimuli_group in stimuli:
        words_in_each_stimuli = []
        onset = stimuli_group[0][0][0]
        offset = stimuli_group[0][-1][0]
        for wrd_sec_tuple in words:
            word_onset = wrd_sec_tuple[0]
            word_offset = wrd_sec_tuple[1]
            word = wrd_sec_tuple[2]
            if word_onset >= onset and word_offset <= offset:
                words_in_each_stimuli.append(wrd_sec_tuple)
        words_all_stimuli.append(words_in_each_stimuli)

    return words_all_stimuli



def syllables_in_sti(stimuli, syllables):
    syll_all_stimuli = []

    for stimuli_group in stimuli:
        syll_in_each_stimuli = []
        onset = stimuli_group[0][0][0]
        offset = stimuli_group[0][-1][0]
        for syllable_secs_tuple in syllables:
            syll_onset = syllable_secs_tuple[0]
            syll_offset = syllable_secs_tuple[1]
            syll = syllable_secs_tuple[2]
            if syll_onset >= onset and syll_offset <= offset:
                syll_in_each_stimuli.append(syllable_secs_tuple)
        syll_all_stimuli.append(syll_in_each_stimuli)

    return syll_all_stimuli


def count_words_per_stim(words_per_stim):
    word_counts = []
    for words in words_per_stim:
        count = 0
        for i, tupl in enumerate(words):
            count += 1
        word_counts.append(count)
    return word_counts


def count_sylls_per_stim(sylls_per_stim):
    syll_counts = []
    for sylls in sylls_per_stim:
        count = 0
        for i, tupl in enumerate(sylls):
            count += 1
        syll_counts.append(count)
    return syll_counts


def create_dict():  # create dictionary to store extracted values
    data_dict = {'Audio File': list, 'Breaks File': list, 'Pauses File': list, 'Syllable File': list, 'Word File': list,
                 'Speaker': list, 'Study Phase': list, 'Break Type': list,
                 'Stimuli Onset': list, 'Stimuli Offset': list, 'Stimuli Duration': list, 'Pause onset': list,
                 'Pause offset': list,
                 'Pause Duration': list, 'Natural Break Second': list, 'Natural Breaks Count': list,
                 'Unnatural Breaks': list, 'Unnatural Breaks Count': list, 'Words in Stimuli': list,
                 'Word Count in Stimuli': list, 'Syllables in Stimuli': list, 'Syllable Count in Stimuli': list}
    return data_dict  # dictionary will be converted into Pandas Dataframe


def store_stimuli_in_dict(data_dict, suitable_groups_4, suitable_groups_3, audio_path, break_files, pau_files,
                          syl_files, wrd_files, speaker, study_phase, natural_breaks_4, natural_breaks_3,
                          unnatural_breaks_4, unnatural_breaks_3, natural_pos_4, natural_pos_3, unnatural_pos_4,
                          unnatural_pos_3, words_per_stim_4, words_per_stim_3, sylls_per_stim_4, sylls_per_stim_3,
                          wrd_c_3, wrd_c_4, syll_c_3, syll_c_4):
    brk_file = []
    pau_file = []
    wav_file = []
    syll_file = []
    wrd_file = []
    speakers = []
    study_phases = []
    brk_type = []
    pau_onset = []
    pau_offset = []
    pau_duration = []
    stimuli_onset = []
    stimuli_offset = []
    stimuli_duration = []
    words_per_stimuli = []
    sylls_per_stimuli = []
    word_counts = []
    syll_counts = []
    natural_breaks = []
    unnatural_breaks = []
    natural_positions = []
    unnatural_positions = []

    for g_list, words, word_count, syllables, syll_count, natural_break, unnatural_break, nat_break_pos, unnat_break_pos, struct in zip(
            [suitable_groups_4, suitable_groups_3], [words_per_stim_4, words_per_stim_3], [wrd_c_4, wrd_c_3],
            [sylls_per_stim_4, sylls_per_stim_3], [syll_c_4, syll_c_3], [natural_breaks_4, natural_breaks_3],
            [unnatural_breaks_4, unnatural_breaks_3], [natural_pos_4, natural_pos_3],
            [unnatural_pos_4, unnatural_pos_3], ['4-4-4', '4-3-4']):
        for i, item in enumerate(g_list):
            wav_file.append(audio_path)
            brk_file.append(break_files)
            pau_file.append(pau_files)
            syll_file.append(syl_files)
            wrd_file.append(wrd_files)
            speakers.append(speaker)
            study_phases.append(study_phase)
            brk_type.append(struct)
            pau_onset.append(item[-2])
            pau_offset.append(item[-1])
            pau_duration.append(item[-1] - item[-2])
            try:
                stimuli_onset.append(g_list[i][0][0][0])
                stimuli_offset.append(g_list[i][0][-1][0])
                stimuli_dur = g_list[i][0][-1][0] - g_list[i][0][0][0]
                stimuli_duration.append(stimuli_dur)
            except IndexError:
                pass
        for idx, word in enumerate(words):
            words_per_stimuli.append(words[idx])
        for index, syllable in enumerate(syllables):
            sylls_per_stimuli.append(syllables[index])
        for x, w_count in enumerate(word_count):
            word_counts.append(word_count[x])
        for y, s_count in enumerate(syll_count):
            syll_counts.append(syll_count[y])
        for i, natural in enumerate(natural_break):
            natural_breaks.append(natural)
        for ix, unnatural in enumerate(unnatural_break):
            unnatural_breaks.append(unnatural)
        for a, nat_positions in enumerate(nat_break_pos):
            natural_positions.append(nat_positions)
        for b, unnat_positions in enumerate(unnat_break_pos):
            unnatural_positions.append(unnat_positions)

    data_dict['Audio File'] = wav_file
    data_dict['Breaks File'] = brk_file
    data_dict['Pauses File'] = pau_file
    data_dict['Syllable File'] = syll_file
    data_dict['Word File'] = wrd_file
    data_dict['Speaker'] = speaker
    data_dict['Study Phase'] = study_phase
    data_dict['Break Type'] = brk_type
    data_dict['Pause onset'] = pau_onset
    data_dict['Pause offset'] = pau_offset
    data_dict['Pause Duration'] = pau_duration
    data_dict['Stimuli Onset'] = stimuli_onset
    data_dict['Stimuli Offset'] = stimuli_offset
    data_dict['Stimuli Duration'] = stimuli_duration
    data_dict['Words in Stimuli'] = words_per_stimuli
    data_dict['Syllables in Stimuli'] = sylls_per_stimuli
    data_dict['Word Count in Stimuli'] = word_counts
    data_dict['Syllable Count in Stimuli'] = syll_counts
    data_dict['Natural Break Second'] = natural_breaks
    data_dict['Unnatural Breaks'] = unnatural_breaks
    data_dict['Natural Breaks Count'] = natural_positions
    data_dict['Unnatural Breaks Count'] = unnatural_positions

    return data_dict


def pool():  # create dictionary to store extracted values
    pool_df = {'Pair Index': list, 'Second Break': list, 'Position': list, 'Correct': list, 'Task': list}
    return pool_df  # dictionary will be converted into Pandas Dataframe

def create_dataframe(phn_files, brk_files, syl_files, wrd_files, wav_files):
    lst=[]
    for phn_file, brk_file, syl_file, wrd_file, wav_file in zip(phn_files, brk_files, syl_files, wrd_files, wav_files):
        phonemic_filename = identify_phon_file(phn_file)
        prosodic_filename=identify_brk_file(brk_file)
        audio_file = identify_audio_file(brk_file)
        syllable_file = identify_sylfile(syl_file)
        word_file = identify_wrdfile(wrd_file)
        speaker = identify_speaker(phonemic_filename)
        study_phase = identify_study_phase(phonemic_filename)
        prosodic_break_dataframe = read_prosodic_break_file(brk_file)
        phonemic_anno_dataframe = read_phonemic_anno_file(phn_file)
        words_dataframe = read_word_file(wrd_file)
        syllable_dataframe= read_syll_file(syl_file)
        words = extract_sec_word_tuples(words_dataframe)
        syllables = extract_sec_syll_tuples(syllable_dataframe)
        index_pros_annotation_tuples, index_phon_annotation_tuples = extract_idx_annotation_tuples(prosodic_break_dataframe, phonemic_anno_dataframe)
        index_sec_break_tuples, index_sec_phon_tuples = extract_index_seconds_tuples(prosodic_break_dataframe,phonemic_anno_dataframe) # extracts index column with seconds column
        second_break_tuples, second_phonemes_tuples = create_sec_anno_tuples(index_pros_annotation_tuples, index_phon_annotation_tuples, index_sec_break_tuples, index_sec_phon_tuples)
        pros_breaks_limited_by_four = limited_by_four(second_break_tuples)
        stimuli_groups_four_three_four = middle_break_3(pros_breaks_limited_by_four)
        stimuli_groups_three_fours = three_fours(second_break_tuples)
        stimuli_groups_three_fours_no_threes = middle_break_4(stimuli_groups_three_fours)
        check_stimuli_length_threes = stimuli_length(stimuli_groups_four_three_four)
        check_stimuli_length_fours = stimuli_length(stimuli_groups_three_fours_no_threes)
        suitable_groups_3 = stimuli(second_phonemes_tuples, check_stimuli_length_threes)
        suitable_groups_4 = stimuli(second_phonemes_tuples, check_stimuli_length_fours)
        natural_breaks_3, unnatural_breaks_3 = natural_unnatural_breaks(suitable_groups_3)
        natural_pos_3, unnatural_pos_3 = position_counts(natural_breaks_3, unnatural_breaks_3)
        natural_breaks_4, unnatural_breaks_4 = natural_unnatural_breaks(suitable_groups_4)
        natural_pos_4, unnatural_pos_4 = position_counts(natural_breaks_4, unnatural_breaks_4)
        words_per_stim_4 = words_in_sti(suitable_groups_4, words)
        words_per_stim_3 = words_in_sti(suitable_groups_3, words)
        sylls_per_stim_4 = syllables_in_sti(suitable_groups_4, syllables)
        sylls_per_stim_3 = syllables_in_sti(suitable_groups_3, syllables)
        w_count_3 = count_words_per_stim(words_per_stim_3)
        w_count_4 = count_words_per_stim(words_per_stim_4)
        syll_count_3 = count_sylls_per_stim(sylls_per_stim_3)
        syll_count_4 = count_sylls_per_stim(sylls_per_stim_4)
        dic_template = create_dict()
        data_dict = store_stimuli_in_dict(dic_template, suitable_groups_4, suitable_groups_3, audio_file, prosodic_filename, phonemic_filename, syllable_file, word_file, speaker, study_phase, natural_breaks_4, natural_breaks_3, unnatural_breaks_4, unnatural_breaks_3, natural_pos_4, natural_pos_3, unnatural_pos_4, unnatural_pos_3, words_per_stim_4, words_per_stim_3, sylls_per_stim_4, sylls_per_stim_3, w_count_3, w_count_4, syll_count_3, syll_count_4)
        df = pd.DataFrame.from_dict(data_dict)
        lst.append(df)

    stim = pd.concat(lst, ignore_index=True)
    #no_equivalent_wav = list()

    for index, audio, file in zip(stim.index, stim['Audio File'],stim['Breaks File']):
        if file in [wav_file[-12:-4] for wav_file in wav_files]:
            stim.loc[stim['Audio File'] == audio, ['Audio File']] = wav_file[:-12]+file+'.wav'

    stim = stim[stim['Audio File'].map(len) > 10]
    stim.columns = [c.replace(' ', '_') for c in stim.columns]
    return stim

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Read in a file or set of files.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('paths', nargs='+', help='Give paths to all files.')
    args = parser.parse_args()

    # Parse paths
    brk_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:]=='.brk'])
    phn_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:]=='.phn'])
    syl_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:]=='.syl'])
    wrd_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:]=='.wrd'])
    wav_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:]=='.wav'])

    #print(brk_files)
    stim = create_dataframe(phn_files, brk_files, syl_files, wrd_files, wav_files)
    stim.to_csv('stimuli_initial_dataframe.csv', sep='\t')
