#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__="Shiwei Wu <dsybswsw@gmail.com>"
__date__ ="$April 5, 2013"

import sys
import json

RARE_TAG = '_RARE_'

class Counter(object):
    '''
    count the terminal symbols in the corpus.
    '''
    def __init__(self, corpus_file_path):
        self.trees = []
        self.word_counts = {}
        corpus = open(corpus_file_path, 'r')
        for line in corpus.readlines():
            self.trees.append(json.loads(line))
        
        for tree in self.trees:
            self.count_tree_term(tree)

    # Do word count for the terminal numbers in a tree.
    def count_tree_term(self, tree):
        if isinstance(tree, basestring):
            if not self.word_counts.has_key(tree):
                self.word_counts[tree] = 1
            else :
                self.word_counts[tree] += 1
            return

        if len(tree) == 3:            
            # Recursively count the children.
            self.count_tree_term(tree[1])
            self.count_tree_term(tree[2])
        elif len(tree) == 2:
            # It is a unary rule.
            self.count_tree_term(tree[1])
    
    def show(self):
        # print self.word_counts
        for key in self.word_counts:
            if self.word_counts[key] >= 5:
                print key + ' ' + str(self.word_counts[key])
                
    def write_new_trees(self, new_tree_file):
        tree_file = open(new_tree_file, 'w')
        for tree in self.trees:
            new_tree = self.replace_rare(tree)
            tree_file.write(json.dumps(new_tree) + '\n')
    
    def replace_rare(self, tree):
        if isinstance(tree, basestring):
            return tree
        if len(tree) == 3:            
            # Recursively modify the children.
            tree[1] = self.replace_rare(tree[1])
            tree[2] = self.replace_rare(tree[2])
        elif len(tree) == 2:
            # It is a unary rule.
            word = tree[1]
            if not self.word_counts.has_key(word) or self.word_counts[word] < 5:
                tree[1] = RARE_TAG
        return tree

def main(input_file):
    counter = Counter(input_file)
    counter.show()
    #counter.write_new_trees('parse_train.tree')

def usage():
    sys.stderr.write("""
    Usage: python oov_count.py [tree_file]
        Print the counts of a corpus of trees.\n""")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)
    main(sys.argv[1])
