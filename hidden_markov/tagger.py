#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__="Shiwei Wu <dsybswsw@gmail.com>"
__date__ ="$Mar 31, 2013"

import hmm
import sys

def usage():
    print './tagger.py <input> <output>'

def do_tag(input_file_path, output_file_path):
    # tagger = hmm.HmmTagger('out_gene.cnt', 'new_gene.cnt')
    tagger = hmm.HmmTagger('bigram_gene.cnt', 'rare_gene.cnt')
    input_file = open(input_file_path, 'r')
    output_file = open(output_file_path, 'w')
    split_query = []
    for line in input_file.readlines():
        token = line.strip() 
        if len(token) != 0:
            split_query.append(token)
        else:
            tags = tagger.get_tags(split_query)
            #print tags
            #print str(len(tags)) + ' ' + str(len(split_query)) 
            for i in range(len(tags)) :
                output_file.write(split_query[i] + ' ' + tags[i] + '\n')
            output_file.write('\n')
            split_query = []
    input_file.close()
    output_file.close()

def main():
    args = sys.argv
    if (len(args) != 3):
        usage()
        exit()
    input_file_path = args[1]
    output_file_path = args[2]
    do_tag(input_file_path, output_file_path)

if __name__ == '__main__': 
    main()
