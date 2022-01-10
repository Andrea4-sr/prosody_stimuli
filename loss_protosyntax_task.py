#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from tqdm import tqdm
import os, sys, openpyxl, random
import numpy as np
from scipy.stats import entropy
from scipy.spatial.distance import cosine

class Dataset_Protosyntax_Loss:

    def __init__(self, pool, out_csv, tgt_utt=4000):
        """ df is df from tsv_A + tsv_B """
        self.tgt_utt = tgt_utt

        self.pool = pool  # passed dataframe
        self.pairsindex = list(
            self.pool.Pair_Index.unique())  # list of unique indexes of self.pool, just the total of stimuli we'll have in the end

        output_dirname = os.path.dirname(os.path.abspath(out_csv))
        print("output dirname is", output_dirname)
        if not os.path.isdir(output_dirname):
            os.makedirs(output_dirname, exist_ok=True)

        print("Initialising logs")

        self.log_file = os.path.join(output_dirname, "annealing_log_protosyntax.csv")
        self.init_logs()

        self.out_file = out_csv
        self.log_every = 1

        print("Randomly initialising the df")  # randomly initialises my df with matched pairs
        self.init_selection()

        self.prec_loss = sys.float_info.max

        # remove the pirs index
        self.pairsindexchoice = list(self.pool.Pair_Index.unique())

    def init_selection(self):

        self.df = pd.DataFrame(columns=self.pool.columns)  # empty dataframe with same columns as passed df

        init = self.pool[self.pool['Correct'] == 'Natural']  # bag with all natural positions per stimuli
        self.df = self.df.append(init)  # bag with all natural positions per stimuli
        self.pool = self.pool.drop(init.index)

        for pairindex in self.pairsindex:
            init = self.pool[(self.pool['Pair_Index'] == pairindex) & (self.pool['Correct'] == "Unnatural")].sample(1,
                                                                                                                    random_state=29)
            self.df = self.df.append(
                init)  # self.df with all natural positions, append an unnatural one of the same pair_index
            self.pool = self.pool.drop(
                init.index)  # drop the above appended unnatural option from the pool with all the unnatural options

    def init_logs(self):
        # we first empty log file
        open(self.log_file, 'w').close()
        # and then write header
        with open(self.log_file, 'a') as fin:
            fin.write(
                'iter,nb_accepted_moves,duration_onset_distrib_loss,position_onset_distrib_loss,duration_offset_distrib_loss,position_offset_distrib_loss,duration_onset_distance_loss,position_onset_distance_loss,duration_offset_distance_loss,position_offset_distance_loss,final_loss\n')

    def move(self):

        pairindex = random.choice(self.pairsindexchoice)  # randomly select a pair
        row_frommatch = self.df[(self.df['Pair_Index'] == pairindex) & (self.df['Correct'] == "Unnatural")].sample(1)
        row_frompool = self.pool[(self.pool['Pair_Index'] == pairindex) & (self.pool['Correct'] == "Unnatural")].sample(
            1)

        self.pool = self.pool.drop(row_frompool.index).append(row_frommatch)
        self.df = self.df.drop(row_frommatch.index).append(row_frompool)

        made_move = [row_frommatch, row_frompool]
        return made_move

    def revert_move(self, made_move):

        row_frommatch = made_move[0]
        row_frompool = made_move[1]

        self.pool = self.pool.drop(row_frommatch.index).append(row_frompool)
        self.df = self.df.drop(row_frompool.index).append(row_frommatch)

    # losses
    # @staticmethod
    # def kl_divergence(p, q):
    #     return np.sum(np.where(p != 0, p * np.log(p / q), 0))

    @staticmethod
    def kl_divergence(p, q):
        # print(p)
        # print(q)
        return entropy(np.array(p).astype(float), np.array(q).astype(float))

    @staticmethod
    def euclidean_distance(p, q):
        size = len(p) if hasattr(p, '__len__') else 1
        return np.linalg.norm(p - q) / size

    @staticmethod
    def distance_norm(p, q):  # definitely wrong TODO
        # is it even useful? ciould just use euclidean dist. Shouldn't change anything as all i want is both to converge. So even if one converges before the other doesn't matter
        #        return 1 - (np.linalg.norm(p-q) / max([p,q]) ) #https://stat
        return np.linalg.norm(p - q) / max([p,
                                            q])  # https://stats.stackexchange.com/questions/79706/normalizing-difference-between-two-real-values-to-0-1-interval

    def loss(self):
        duration_onset_distrib_loss = self.duration_onset_distrib_loss()  # loss on duration distrib
        position_onset_distrib_loss = self.position_onset_distrib_loss()  # loss on duration distrib
        duration_offset_distrib_loss = self.duration_offset_distrib_loss()
        position_offset_distrib_loss = self.position_offset_distrib_loss()
        duration_onset_distance_loss = self.duration_onset_distance_loss()
        position_onset_distance_loss = self.position_onset_distance_loss()
        duration_offset_distance_loss = self.duration_offset_distance_loss()
        position_offset_distance_loss = self.position_offset_distance_loss()
        loss = (
                           duration_onset_distrib_loss + position_onset_distrib_loss + duration_offset_distrib_loss + position_offset_distrib_loss + duration_onset_distance_loss + position_onset_distance_loss + duration_offset_distance_loss + position_offset_distance_loss) / 8
        return loss, [duration_onset_distrib_loss, position_onset_distrib_loss, duration_offset_distrib_loss,
                      position_offset_distrib_loss, duration_onset_distance_loss, position_onset_distance_loss,
                      duration_offset_distance_loss, position_offset_distance_loss, loss]

    def duration_onset_distrib_loss(self):
        p = self.df[self.df['Correct'] == "Natural"].Second_Break_to_Onset.sort_values()
        q = self.df[self.df['Correct'] == "Unnatural"].Second_Break_to_Onset.sort_values()
        return self.kl_divergence(p, q)

    def position_onset_distrib_loss(self):
        p = self.df[self.df['Correct'] == "Natural"].Position_from_Onset.sort_values()
        q = self.df[self.df['Correct'] == "Unnatural"].Position_from_Onset.sort_values()
        return self.kl_divergence(p, q)

    def duration_offset_distrib_loss(self):
        p = self.df[self.df['Correct'] == "Natural"].Second_Break_to_Offset.sort_values()
        q = self.df[self.df['Correct'] == "Unnatural"].Second_Break_to_Offset.sort_values()
        return self.kl_divergence(p, q)

    def position_offset_distrib_loss(self):
        p = self.df[self.df['Correct'] == "Natural"].Position_from_Offset.sort_values()
        q = self.df[self.df['Correct'] == "Unnatural"].Position_from_Offset.sort_values()
        return self.kl_divergence(p, q)

    def position_onset_distance_loss(self):
        a = np.array(self.df[self.df["Correct"] == "Natural"]['Position_from_Onset'].sort_values()).astype('float32')
        b = np.array(self.df[self.df["Correct"] == "Unnatural"]['Position_from_Onset'].sort_values()).astype('float32')
        loss = cosine(a, b)
        return loss

    def duration_onset_distance_loss(self):
        a = np.array(self.df[self.df["Correct"] == "Natural"]['Second_Break_to_Onset'].sort_values()).astype('float32')
        A_dur = np.nanmean(a, dtype='float32')
        b = np.array(self.df[self.df["Correct"] == "Unnatural"]['Second_Break_to_Onset'].sort_values()).astype(
            'float32')
        B_dur = np.nanmean(b, dtype='float32')
        loss = cosine(a, b)
        return loss

    def position_offset_distance_loss(self):
        a = np.array(self.df[self.df["Correct"] == "Natural"]['Position_from_Offset'].sort_values()).astype('float32')
        A_dur = np.nanmean(a, dtype='float32')
        b = np.array(self.df[self.df["Correct"] == "Unnatural"]['Position_from_Offset'].sort_values()).astype('float32')
        B_dur = np.nanmean(b, dtype='float32')
        loss = cosine(a, b)
        return loss

    def duration_offset_distance_loss(self):
        a = np.array(self.df[self.df["Correct"] == "Natural"]['Second_Break_to_Offset'].sort_values()).astype('float32')
        A_dur = np.nanmean(a, dtype='float32')
        b = np.array(self.df[self.df["Correct"] == "Unnatural"]['Second_Break_to_Offset'].sort_values()).astype(
            'float32')
        B_dur = np.nanmean(b, dtype='float32')
        loss = cosine(a, b)
        return loss

    def run_sim_annealing(self, n_iter):

        nb_accepted_moves = 0
        # Should implement a threshold based stop rule
        for iter in tqdm(range(n_iter)):

            # Make a move
            made_move = self.move()

            # Compute loss and decide if move should be revert or not
            curr_loss, loss_details = self.loss()
            # print('current loss',curr_loss)

            if curr_loss > self.prec_loss:
                # We revert move, prec_loss is not updated
                self.revert_move(made_move)
            else:
                # We keep move, prec_loss becomes curr_loss
                self.prec_loss = curr_loss
                # print('loss of accepted move', self.prec_loss)
                nb_accepted_moves += 1
                # print('accepted moves', nb_accepted_moves)

            if nb_accepted_moves % self.log_every == 0:
                self.write_logs(loss_details, iter, nb_accepted_moves)
        self.final_loss = curr_loss
        # print('final loss', self.final_loss)

        return self.final_loss

    def write_logs(self, loss, iter, nb_accepted_moves):
        # Header is :
        # iter,nb_accepted_moves,loss
        with open(self.log_file, 'a') as fin:
            fin.write(",".join(map(str, [iter, nb_accepted_moves, loss[0], loss[1], loss[2], loss[3], loss[4], loss[5],
                                         loss[6], loss[7], loss[8]])) + '\n')


if __name__ == "__main__":
    import argparse, os

    parser = argparse.ArgumentParser(description='Read in a file or set of files.')
    parser.add_argument("pool", help="path to the dataset A")
    parser.add_argument("output_tsv", type=str, help="path to the output tsv")

    parser.add_argument("--tgt_utt", type=int, help='target number of utterances (A+B)', default=2000)
    parser.add_argument("--n_iter", type=int, help='num iter for matching algo', default=15000)
    parser.add_argument("--check_file_exists", help='if path to audio dir is given, only keep those existing in path',
                        default=None)

    parser.parse_args()
    args = parser.parse_args()

    df_protosyntax_pool = pd.read_csv(args.pool, sep=',')
    #print(df_protosyntax_pool)

    MD = Dataset_Protosyntax_Loss(df_protosyntax_pool, args.output_tsv, tgt_utt=args.tgt_utt)
    MD.run_sim_annealing(n_iter=args.n_iter)
    MD.df.to_csv(args.output_tsv, sep='\t', index=False)
    MD.df.to_excel('chosen_pairs_protosyntax_task.xlsx')