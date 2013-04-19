#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__="Shiwei Wu <dsybswsw@gmail.com>"
__date__ ="$Mar 31, 2013"

import sys
#import math
import learn
from math import log

from collections import defaultdict

LAST_BEST = 'last_best'
PROB = 'prob'
RARE_TAG = '_RARE_'

class HmmTagger(object):
    '''
    hidden markov tagger
    '''
    def __init__(self, tag_ngram_file_path, emission_file_path):
        print 'init function'
        self.tag_ngrams = {}
        self.__init_tag_ngram(tag_ngram_file_path)
        self.__init_emissions(emission_file_path)
        self.ngram = 3
        self.tag_num = len(self.tag_dict)

    def __init_tag_ngram(self,tag_ngram_file_path):
        tag_ngram_file = open(tag_ngram_file_path, 'r')
        for line in tag_ngram_file.readlines():
            tokens = line.split()
            count = int(tokens[0])
            grams = tokens[2: len(tokens)]
            key = HmmTagger._build_key(grams)
            if self.tag_ngrams.has_key(key):
                self.tag_ngrams[key] += count
            else:
                self.tag_ngrams[key] = count

    def __init_emissions(self, emission_file_path):
        self.tag_dict = learn.count_tags(emission_file_path)
        self.pair_dict = learn.count_word_tag_pairs(emission_file_path)
        self.word_dict = learn.count_words(emission_file_path)
        self.__get_tag_2gram_dict()
        
    def __get_tag_2gram_dict(self):
        self.tag_2grams = []
        for tag1 in self.tag_dict:
            for tag2 in self.tag_dict:
                self.tag_2grams.append(self._build_key([tag1,tag2]))

    def __calculate_emission(self, word, tag):
        if len(word) == 0:
            return None
        if not self.word_dict.has_key(word):
            word = learn.tag_rare_word(word)
        a = 0.001
        if self.tag_dict.has_key(tag):
            tag_count = float(self.tag_dict[tag])        
            word_size = float(len(self.word_dict))
            key = learn.build_pair(tag, word)
            prob = 0
            if (not self.pair_dict.has_key(key)):
                prob = a / (tag_count + word_size * a)
            else:
                pair_count = float(self.pair_dict[key])
                prob = (pair_count + a) / (tag_count + word_size * a)
            return prob
        else:
            return 0.0
    
    @staticmethod
    def _build_key(tokens):
        return tuple(tokens)
    
    def __postier(self, y_i, y_i_1, y_i_2):
        down_key = HmmTagger._build_key([y_i_2, y_i_1])
        up_key = HmmTagger._build_key([y_i_2, y_i_1, y_i])
        down = float(self.tag_ngrams[down_key])
        up = float(self.tag_ngrams[up_key])
        return up /down

    def print_tag_dict(self):
        for key in self.tag_ngrams:
            print key

    # calculate the state probability in the begining of the sentence.
    def __init_first_state(self, word):
        tag_states = {}
        for tag in self.tag_dict:
            trans_prob = self.__postier(tag, '*', '*')                
            emis = self.__calculate_emission(word,tag)
            temp_prob = self.__cal_prob_log(1, trans_prob, emis)
            last_best = '*'
            key = ('*', tag)
            state = HmmTagger.__build_state(temp_prob, last_best)
            tag_states[key] = state
        return tag_states

    def viterbi_decode(self,query):
        ngram = self.ngram
        query_len = len(query)
        # print emissions
        states = [{} for i in range(query_len)]
        # compute emiissions of a query        
        states[0] = self.__init_first_state(query[0])
        for idx in range(len(query) - 1):
            i = idx + 1
            word = query[i]
            tag_states = {}
            for tag_gram in self.tag_2grams:
                last_states = states[i - 1]
                v = tag_gram[1]
                u = tag_gram[0]
                emis = self.__calculate_emission(word,v)
                max_prob = - float('inf')
                max_last_tag = ''
                for last_tag in last_states:  
                    if last_tag[1] != u:
                        continue
                    w = last_tag[0]
                    last_prob = last_states[last_tag][PROB]
                    trans_prob = self.__postier(v, u, w)
                    temp_prob = self.__cal_prob_log(last_prob, trans_prob, emis)
                    # print 'temporal prob:' + str(temp_prob)
                    if temp_prob > max_prob:
                        max_prob = temp_prob
                        max_last_tag = last_tag
                state = HmmTagger.__build_state(max_prob, max_last_tag)
                tag_states[(u,v)] = state
            states[i] = tag_states
        return states

    def __cal_prob_log(self, state_prob, trans_prob, emission):
        temp_prob = log(emission) + state_prob + log(trans_prob)
        #return state_prob + trans_prob + emission        
        return temp_prob
                                
    @staticmethod
    def __build_state(value, last_best):
        state = {}
        state[PROB] = value
        state[LAST_BEST] = last_best
        return state
                
    def __compute_emissions(self, query):
        query_len = len(query)
        emissions = [defaultdict(float) for i in range(query_len)]
        for i in range(query_len):
            dict_i = defaultdict(float)
            for tag in self.tag_ngrams:
                word = query[i]
                dict_i[tag] = self.calculate_emission(tag, word)
            emissions.append(dict_i)
        return emissions
            
    def get_tags(self, split_query):
        states = self.viterbi_decode(split_query)
        length = len(split_query)
        tags = [str(0) for i in range(length)]
        if len(states) != len(tags):
            print str(len(states)) + ' ' + str(len(tags))
            return None
        last_state = states[length - 1]
        max_key = HmmTagger.__pick_max(last_state)
        # print max_key
        last_key = last_state[max_key][LAST_BEST]
        tags[length - 1] = max_key[1]
        for i in range(length-1):
            index = length - 2 - i
            now_state = states[index]
            tags[index] = last_key[1]
            last_key = now_state[last_key][LAST_BEST]
            # print last_key
        return tags

    @staticmethod
    def __pick_max(state):
        # print 'print the last state'
        # print state
        max_prob = - float('inf')
        max_key = ''
        for key in state:
            if state[key][PROB] > max_prob:
                max_key = key
                max_prob = state[key][PROB]
        return max_key

if __name__ == '__main__': 
    tagger = HmmTagger('bigram_gene.cnt', 'rare_gene.cnt')
    query_str = 'comparison with alkaline phosphatases and 5 - nucleotidase'
    tags = tagger.get_tags(query_str.split())
    print tags
