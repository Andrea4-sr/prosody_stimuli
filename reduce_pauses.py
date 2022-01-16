#!/usr/bin/env python
# coding: utf-8

import os
from pydub import AudioSegment

def reduce_pause(audio_wav, pau_onset, pau_offset, crossfade=5):
    # check that the pause is m> 20ms
    if  (pau_offset - pau_onset)*1000 > 20:
        to_remove_onset_ms = pau_onset*1000 + 25 # this is in ms. Keeping it in ms as that's what pydub uses
        to_remove_offset_ms = pau_offset*1000 - 25

        beg = audio_wav[:to_remove_onset_ms]
        end = audio_wav[to_remove_offset_ms:]
        new_audio = beg.append(end, crossfade=crossfade) # make the crossfade around 15ms , can change this parameter
    else:
        new_audio = audio_wav # do nothing
    return new_audio


def extract_details_for_crossfading(stim):
    pauses=[]
    for i, (audio, pause_onset, pause_offset, pause_duration) in enumerate(zip(stim['Audio_File'], stim['Pause_onset'], stim['Pause_offset'], stim['Pause_Duration'])):
        pause = [audio,[pause_onset, pause_offset, pause_duration]]
        pauses.append(pause)
        for index in range(len(pauses)-1):
            if pauses[index][0] == pauses[index+1][0]:
                new_pause=[pauses[index+1][1][0], pauses[index+1][1][1], pauses[index+1][1][2]]
                pauses[index].append(new_pause)
                pauses.pop(index+1)
    for item in pauses:
        for i,element in enumerate(item):
            count = item.count(element)
            if count == 2:
                item.pop(i)  
    dictOfPauses = {i[0] : sorted(i[1:]) for i in pauses}
    return dictOfPauses


def crossfade_wav_files_per_pause(dictionary_of_pauses_per_stimuli,outdir):
    for i, (audio, pauses) in enumerate(dictionary_of_pauses_per_stimuli.items()):
        #print(audio)
        new_path = outdir+audio[-12:-4]+'.wav'
        exists = os.path.isfile(new_path)
        if exists: # check if the audio wav already exists, to crossfade the new pause of same wav, previously manipulated wav
            audio_wav = AudioSegment.from_file(new_path)
            if len(pauses) > 1:
                durations = [x[2] for x in pauses] # extract the durations of the pauses in current-working wav
                indexes = list(range(len(pauses))) # list of the indexes of pauses in current-working wav
                for index, pause in enumerate(pauses):
                    if index != 0:
                        len_before = list(range(len(durations[:index]))) # make a list of indexes before current-on index
                        sum_pauses = [durations[index] for index in len_before]
                        sum_pauses = sum(sum_pauses) # calculate sum of previous found pauses in 
                        if sum_pauses != 0:
                            pauses[index][0] = pauses[index][0]-sum_pauses
                            pauses[index][1] = pauses[index][1]-sum_pauses
                            pause_onset=pause[0]
                            pause_offset=pause[1]
                            new_audio = reduce_pause(audio_wav, pause_offset, pause_onset, crossfade=5)
                            new_audio.export(new_path, format="wav")
                    else:
                        pause_onset = pause[0]
                        pause_offset = pause[1]
                        new_audio = reduce_pause(audio_wav, pause_offset, pause_onset, crossfade=5)
                        new_audio.export(new_path, format="wav")
        else:
            audio_wav = AudioSegment.from_file(audio)
            for pause in pauses: 
                pause_onset=pause[0]
                pause_offset=pause[1]
                new_audio=reduce_pause(audio_wav, pause_onset, pause_offset, crossfade=5)
                new_audio.export(new_path, format="wav")


if __name__ == '__main__':

    import argparse
    from create_initial_stimuli_dataframe import create_dataframe as initial_df

    parser = argparse.ArgumentParser(description='Read in a file or set of files.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('outdir', type=str, help='Give path to save crossfaded audio wavs.')
    parser.add_argument('paths', nargs='+', help="Give paths to all files.")
    args = parser.parse_args()

    # Parse paths
    brk_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.brk'])
    phn_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.phn'])
    syl_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.syl'])
    wrd_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.wrd'])
    wav_files = sorted([os.path.join(os.getcwd(), path) for path in args.paths if path[-4:] == '.wav'])

    stimuli = initial_df(phn_files, brk_files, syl_files, wrd_files, wav_files)

    dictionary_of_pauses_per_stimuli = extract_details_for_crossfading(stimuli)
    crossfade_wav_files_per_pause(dictionary_of_pauses_per_stimuli, args.outdir)


