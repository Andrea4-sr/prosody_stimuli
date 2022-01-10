#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from tqdm import tqdm
import sys
import numpy as np 
import random
from scipy.stats import entropy
from scipy.spatial.distance import cosine



class Dataset_Lexical_Loss:
    
    def __init__(self, pool, out_csv, tgt_utt=4000): # df_A = correct and df_B = incorrect
        """ df is df from tsv_A + tsv_B """
        self.tgt_utt = tgt_utt

        self.pool = pool # passed dataframe
        self.pairsindex=list(self.pool.Pair_Index.unique()) # list of unique indexes of self.pool, just the total of stimuli we'll have in the end

        
        output_dirname = os.path.dirname(os.path.abspath(out_csv))
        print("output dirname is", output_dirname)
        if not os.path.isdir(output_dirname):
            os.makedirs(output_dirname, exist_ok=True)

        print("Initialising logs")

        self.log_file = os.path.join(output_dirname, "annealing_log.csv")
        self.init_logs()
        
    
        self.out_file = out_csv
        self.log_every = 1

        print("Randomly initialising the df") # randomly initialises my df with matched pairs
        self.init_selection()

        self.prec_loss = sys.float_info.max
        
        # remove the pairs index
        self.pairsindexchoice = list(self.pool.Pair_Index.unique())
        
    def init_selection(self):
        
        self.df = pd.DataFrame(columns=self.pool.columns) # empty dataframe with same columns as passed df 
       
        init_nat = self.pool[self.pool['Correct'] == 'Natural'] # bag with all natural positions per stimuli

        self.pool_unnat = self.pool.drop(init_nat.index)  # bag with all unnatural positions per stimuli
        
        init_unnat = self.pool[self.pool['Correct'] == 'Unnatural'] # bag with all natural positions per stimuli
   
        self.pool_nat = self.pool.drop(init_unnat.index)  # bag with all natural positions per stimuli

        
        for pairindex in self.pairsindex:
            init_unnat = self.pool[(self.pool['Pair_Index'] == pairindex) & (self.pool['Correct'] == "Unnatural")].sample(1, random_state=29)
            init_nat = self.pool[(self.pool['Pair_Index'] == pairindex) & (self.pool['Correct'] == "Natural")].sample(1, random_state=29)
            self.df = self.df.append(init_unnat) # to empty self.df, append an unnatural one of the same pair_index
            self.df = self.df.append(init_nat) # to empty self.df, append a natural one of the same pair_index
            self.pool_unnat = self.pool.drop(init_unnat.index) # drop the above appended unnatural option from the pool with all the unnatural options
            self.pool_nat = self.pool.drop(init_nat.index) # drop the above appended natural option from the pool with all the natural options

            
    def init_logs(self):
        # we first empty log file
        open(self.log_file, 'w').close()
        # and then write header
        with open(self.log_file, 'a') as fin:
            fin.write('iter,nb_accepted_moves,duration_onset_distrib_loss,position_onset_distrib_loss,duration_offset_distrib_loss,position_offset_distrib_loss,duration_onset_distance_loss,position_onset_distance_loss,duration_offset_distance_loss,position_offset_distance_loss,final_loss\n')


    def move(self):
        
       
        pairindex = random.choice(self.pairsindexchoice) # 
        # correctness row random.choice(["natural", "unnatural"])
        row_frommatch_nat = self.df[(self.df['Pair_Index'] == pairindex) & (self.df['Correct'] == "Natural")].sample(1)
        row_frompool_nat = self.pool[(self.pool['Pair_Index'] == pairindex) & (self.pool['Correct'] == "Natural")].sample(1)
        
        row_frommatch_unnat = self.df[(self.df['Pair_Index'] == pairindex) & (self.df['Correct'] == "Unnatural")].sample(1)
        row_frompool_unnat = self.pool[(self.pool['Pair_Index'] == pairindex) & (self.pool['Correct'] == "Unnatural")].sample(1)

        self.pool = self.pool.drop(row_frompool_nat.index).append(row_frommatch_nat)
        self.df = self.df.drop(row_frommatch_nat.index).append(row_frompool_nat)
        
        self.pool = self.pool.drop(row_frompool_unnat.index).append(row_frommatch_unnat)
        self.df = self.df.drop(row_frommatch_unnat.index).append(row_frompool_unnat)
        
        made_move = [row_frommatch_nat, row_frompool_nat, row_frommatch_unnat, row_frompool_unnat]
        return made_move

    def revert_move(self, made_move):
        
        row_frommatch_nat = made_move[0]
        row_frompool_nat = made_move[1]
        row_frommatch_unnat = made_move[2]
        row_frompool_unnat = made_move[3]

        self.pool = self.pool.drop(row_frommatch_nat.index).append(row_frompool_nat)
        self.df = self.df.drop(row_frompool_nat.index).append(row_frommatch_nat)
        
        self.pool = self.pool.drop(row_frommatch_unnat.index).append(row_frompool_unnat)
        self.df = self.df.drop(row_frompool_unnat.index).append(row_frommatch_unnat)


    
    # losses

    @staticmethod
    def kl_divergence(p, q):
        return entropy(np.array(p).astype(float),np.array(q).astype(float))


    @staticmethod
    def euclidean_distance(p, q):
        size = len(p) if hasattr(p, '__len__') else 1
        return np.linalg.norm(p-q) / size

    @staticmethod
    def distance_norm(p, q): # definitely wrong TODO
        return np.linalg.norm(p-q) / max([p,q])  #https://stats.stackexchange.com/questions/79706/normalizing-difference-between-two-real-values-to-0-1-interval
    

    def loss(self):
        duration_onset_distrib_loss = self.duration_onset_distrib_loss() # loss on duration distrib
        position_onset_distrib_loss = self.position_onset_distrib_loss() # loss on duration distrib
        duration_offset_distrib_loss = self.duration_offset_distrib_loss()
        position_offset_distrib_loss = self.position_offset_distrib_loss()
        duration_onset_distance_loss = self.duration_onset_distance_loss()
        position_onset_distance_loss = self.position_onset_distance_loss()
        duration_offset_distance_loss = self.duration_offset_distance_loss()
        position_offset_distance_loss = self.position_offset_distance_loss()
        loss = (duration_onset_distrib_loss + position_onset_distrib_loss + duration_offset_distrib_loss + position_offset_distrib_loss +duration_onset_distance_loss+position_onset_distance_loss+duration_offset_distance_loss+position_offset_distance_loss) / 8
        return loss , [duration_onset_distrib_loss,position_onset_distrib_loss,duration_offset_distrib_loss,position_offset_distrib_loss,duration_onset_distance_loss,position_onset_distance_loss,duration_offset_distance_loss,position_offset_distance_loss, loss]


    def duration_onset_distrib_loss(self):
        p = self.df[self.df['Correct']=="Natural"].Second_Break_to_Onset.sort_values()
        q = self.df[self.df['Correct']=="Unnatural"].Second_Break_to_Onset.sort_values()
        return self.kl_divergence(p,q)
    
    def position_onset_distrib_loss(self):
        p = self.df[self.df['Correct']=="Natural"].Position_from_Onset.sort_values()
        q = self.df[self.df['Correct']=="Unnatural"].Position_from_Onset.sort_values()
        return self.kl_divergence(p,q)
    
    def duration_offset_distrib_loss(self):
        p = self.df[self.df['Correct']=="Natural"].Second_Break_to_Offset.sort_values()
        q = self.df[self.df['Correct']=="Unnatural"].Second_Break_to_Offset.sort_values()
        return self.kl_divergence(p,q)
    
    def position_offset_distrib_loss(self):
        p = self.df[self.df['Correct']=="Natural"].Position_from_Offset.sort_values()
        q = self.df[self.df['Correct']=="Unnatural"].Position_from_Offset.sort_values()
        return self.kl_divergence(p,q)
    
    
    def position_onset_distance_loss(self):
        a = np.array(self.df[self.df["Correct"] == "Natural"]['Position_from_Onset'].sort_values()).astype('float32')
        b = np.array(self.df[self.df["Correct"] == "Unnatural"]['Position_from_Onset'].sort_values()).astype('float32')
        loss = cosine(a, b)
        return loss
    
    def duration_onset_distance_loss(self):
        a = np.array(self.df[self.df["Correct"] == "Natural"]['Second_Break_to_Onset'].sort_values()).astype('float32')
        b = np.array(self.df[self.df["Correct"] == "Unnatural"]['Second_Break_to_Onset'].sort_values()).astype('float32')
        loss = cosine(a, b)
        return loss
    
    def position_offset_distance_loss(self):
        a = np.array(self.df[self.df["Correct"] == "Natural"]['Position_from_Offset'].sort_values()).astype('float32')
        b = np.array(self.df[self.df["Correct"] == "Unnatural"]['Position_from_Offset'].sort_values()).astype('float32')
        loss = cosine(a, b)
        return loss
    
    def duration_offset_distance_loss(self):
        a = np.array(self.df[self.df["Correct"] == "Natural"]['Second_Break_to_Offset'].sort_values()).astype('float32')
        b = np.array(self.df[self.df["Correct"] == "Unnatural"]['Second_Break_to_Offset'].sort_values()).astype('float32')
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
            
            if curr_loss > self.prec_loss:
                # We revert move, prec_loss is not updated
                self.revert_move(made_move)
            else:
                # We keep move, prec_loss becomes curr_loss
                self.prec_loss = curr_loss
                nb_accepted_moves += 1

            if nb_accepted_moves % self.log_every == 0:
                self.write_logs(loss_details, iter, nb_accepted_moves)
        self.final_loss = curr_loss

        return self.final_loss

    
    def write_logs(self, loss, iter, nb_accepted_moves):
        # Header is :
        # iter,nb_accepted_moves,loss
        with open(self.log_file, 'a') as fin:
            fin.write(",".join(map(str, [iter, nb_accepted_moves, loss[0], loss[1], loss[2], loss[3], loss[4], loss[5], loss[6], loss[7], loss[8]]))+'\n')
            
            
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

    df_lexical_pool = pd.read_csv(args.pool, sep=',')
    #print(df_lexical_pool)

    MD = Dataset_Lexical_Loss(df_lexical_pool, args.output_tsv, tgt_utt=args.tgt_utt)
    MD.run_sim_annealing(n_iter=args.n_iter)
    MD.df.to_csv(args.output_tsv, sep='\t', index=False)
    MD.df.to_excel('chosen_pairs_lexical_task.xlsx')


