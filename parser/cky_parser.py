#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__="Shiwei Wu <dsybswsw@gmail.com>"
__date__ ="$April 5, 2013"

import sys
import json

import config

START_SYMBOL = 'SBARQ'

RARE = '_RARE_'

RULE = '_RULE_'

PROB = '_PROB_'

S_INDEX = '_s_index_'

from math import log

'''
Implements a PCFG CKY parser.
'''
class Parser(object):
    def __init__(self, config_file):
        self.rules = {}
        self.non_terms = {}
        self.word_dict = {}
        self.non_term_rules = {}
        self.__initialize(config_file)

    def __load_word_dict(self, word_dict_file):
        dict_file = open(word_dict_file, 'r')
        for line in dict_file:
            tokens = line.split()
            word = tokens[0].strip()
            num = int(tokens[1])
            self.word_dict[word] = num
        dict_file.close()

    def __initialize(self, config_file):
        options = config.load_config(config_file)
        model_file = options['model']
        word_dict = options['word_dict']
        self.__load_model(model_file)
        self.__load_word_dict(word_dict)
        self.__init_term_rules()

    def __init_term_rules(self):
        for non_term in self.non_terms:
            self.non_term_rules[non_term] = []
        for rule in self.rules:
            self.non_term_rules[rule[0]].append(rule)
                
    def __load_model(self, model_file):
        model = open(model_file, 'r')
        for line in model.readlines():
            tokens = line.split(' ')
            if len(tokens) < 3:
                continue
            rule_type = tokens[1]
            num = int(tokens[0])
            symbol = tokens[2]
            if rule_type == 'NONTERMINAL':
                self.non_terms[symbol] = num
            elif rule_type == 'UNARYRULE' or rule_type == 'BINARYRULE':
                if self.non_terms.has_key(symbol):
                    self.non_terms[symbol] += num
                else:
                    self.non_terms[symbol] = num
                grammar = self.__build_grammar(tokens[2:len(tokens)])
                # print grammar
                self.rules[grammar] = num;

    def __build_grammar(self, rule_symbols):
        syms = []
        for token in rule_symbols:
            syms.append(token.strip())
        return tuple(syms)

    def _log_postier(rule):
        symbol = rule[0]
        symbol_count = self.non_terms[symbol]
        value = -float('inf')
        if self.rules.has_key(rule) and self.rules[rule] > 0:
            value = log(float(self.rules[rule])/float(symbol_count))
        return value
        
    def get_rule_prob(self, rule):
        # print rule
        if not self.rules.has_key(rule):                
            return -float('inf')
        else:
            value =  log(float(self.rules[rule]))
            # print value
            return value
        
    def _log_postier(self, rule):
        symbol = rule[0]
        if not self.non_terms.has_key(symbol) or not self.rules.has_key(rule):
            return -float('inf')
        symbol = rule[0]            
        non_term_num = self.non_terms[symbol]
        rule_num = self.rules[rule]
        if non_term_num == 0 or rule_num == 0:
            return -float('inf')
        return log(float(non_term_num)/float(rule_num))

    def decode(self, slots):
        n = len(slots)
        # initialize the chart lattice.
        lattice = [[{} for j in range (n + 1)] for i in range(n + 1)]
        '''
        comment by my wife, save the happiess here !
        woshigeyigedabaobao
        zhangzaishuzhuagnshang
        houlai diaoxialaile
        '''
        # initialize the first lattic line
        for i in range(1, n + 1):
            for non_term in self.non_terms:
                word = slots[i - 1].strip()
                if not self.word_dict.has_key(slots[i - 1]):
                    word = RARE
                # print non_term + '' + word 
                prob = self.get_rule_prob((non_term, word))
                lattice[i][i][non_term] = {}
                lattice[i][i][non_term][PROB] = prob
                lattice[i][i][non_term][RULE] = (non_term, word)
                lattice[i][i][non_term][S_INDEX] = i
                # print lattice[i][i]

        for k in range(1, n):
            for i in range (1, n + 1 - k):
                j = i + k
                max_prob = -float('inf')
                for non_term in self.non_term_rules:
                    symbol = non_term
                    lattice[i][j][symbol] = {}
                    max_rule = ()
                    max_prob = -float('inf')
                    max_s_id = i
                    for rule in self.non_term_rules[non_term]:
                        if len(rule) < 3:
                            # print rule
                            continue
                        rule_prob = self._log_postier(rule)
                        left = rule[1]
                        right = rule[2]
                        for s in range(i,j):
                            prob1 = lattice[i][s][left][PROB]
                            prob2 = lattice[s + 1][j][right][PROB]
                            prob = rule_prob + prob1 + prob2
                            if prob > max_prob:
                                max_prob = prob
                                max_rule = rule
                                max_s_id = s                            
                    lattice[i][j][symbol][PROB] = max_prob
                    lattice[i][j][symbol][RULE] = max_rule
                    lattice[i][j][symbol][S_INDEX] = max_s_id
        return lattice

    def extract_parsing_tree(self,lattice, start, end, symbol):
        if start == end:
            return [symbol, lattice[start][end][symbol][RULE][1]]
        s = lattice[start][end][symbol][S_INDEX]
        rule = lattice[start][end][symbol][RULE]
        print str(start) + ' ' + str(end) + ' '+ str(rule)
        left = rule[1]
        right = rule[2]
        left_tree = self.extract_parsing_tree(lattice, start, s, left)
        right_tree = self.extract_parsing_tree(lattice, s + 1, end, right)
        return [symbol, left_tree, right_tree]

    def parse(self, query):
        slots = query.split()
        lattice = self.decode(slots)
        # print len(lattice)
        n = len(slots)
        # print lattice[1][6]
        tree = self.extract_parsing_tree(lattice, 1, n, START_SYMBOL)
        return tree

if __name__ == '__main__':
    parser = Parser('config')
    tree = parser.parse('When was the bar-code invented ?')
    print tree
