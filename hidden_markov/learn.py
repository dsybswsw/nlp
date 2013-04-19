#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

RARE_TAG = '_RARE_'

DEFAULT_TAG = 'O'

NUMERIC = 'NUM'

ALL_CAP = 'ALL_CAP'

LAST_CAP = 'LAST_CAP'

RARE = 'RARE'

'''
choise = word : count words
choise = tag : count tags
'''
def count(in_file_path, choise):
    col = 3
    if choise == 'word':
        col = 3
    elif choise == 'tag':
        col = 2
    elif choise == 'pair':
        col = 4
    else :
        col = 3

    word_dict = {}
    in_file = open(in_file_path, 'r')
    for line in in_file.readlines():
        tokens = line.split()
        if len(tokens) != 4:
            continue
        flag =tokens[1]
        if flag != 'WORDTAG':
            continue
        count = int(tokens[0])
        word = tokens[3]
        if col == 2 or col == 3:
            word = tokens[col]
        elif col == 4:
            word = build_pair(tokens[2], tokens[3])
        else:
            word = tokens[3]

        if word_dict.has_key(word):
            word_dict[word] = word_dict[word] + count
        else:
            word_dict[word] = count
    in_file.close()
    return word_dict

def build_pair(token1, token2):
    return (token1,token2)
 
def count_words(in_file_path):
    return count(in_file_path, 'word')

def count_tags(in_file_path):
    return count(in_file_path ,'tag')

def count_word_tag_pairs(in_file_path):
    return count(in_file_path, 'pair')

def generate(in_file_path, out_file_path, tag_ngram_file_path):
    # get word count map.
    word_dict = count_words(in_file_path)

    in_file = open(in_file_path, 'r')
    out_file = open(out_file_path, 'w')
    tag_ngram = open(tag_ngram_file_path, 'w')

    for line in in_file.readlines():
        tokens = line.split()
        if tokens[1] != 'WORDTAG':
            tag_ngram.write(line.strip() + '\n')
            continue
        count = int(tokens[0])
        tag = tokens[2]
        word = tokens[3]
        if (not word_dict.has_key(word)) or (word_dict[word] < 5):
            word = tag_rare_word(word)
        new_line = str(count) + ' ' + tokens[1] + ' ' +  tag + ' ' + word + '\n'
        out_file.write(new_line)
    in_file.close()
    out_file.close()

def tag_rare_word(word):
    re = ''
    # return RARE_TAG
    if is_numeric(word):
        re = NUMERIC
    elif is_all_cap(word):
        re = ALL_CAP
    elif is_last_cap(word):
        re = LAST_CAP
    else:
        re = RARE
    return re

def is_numeric(word):
    for token in word:
        if token <= '9' and token >= '0':
            return True
    return False

def is_all_cap(word):
    for token in word:
        if token > 'Z' or token < 'A':
            return False
    return True

def is_last_cap(word):
    token = word[len(word) - 1]
    if token >= 'A' and token <= 'Z':
        return True
    else:
        return False

def test(in_file_path, dev_path, out_path):
    word_dict = count_words(in_file_path)
    tag_dict = count_tags(in_file_path)
    pair_dict = count_word_tag_pairs(in_file_path)
    dev = open(dev_path, 'r')
    out = open(out_path, 'w')
    for line in dev.readlines():
        word = line.strip()
        if len(word) == 0:
            out.write('\n')
            continue
        if (not word_dict.has_key(word)) or (word_dict[word] < 5):
            word = RARE_TAG
        max_prob = 0
        max_tag = DEFAULT_TAG
        for tag in tag_dict:
            tag_count = float(tag_dict[tag])
            key = build_pair(tag, word)
            prob = 0
            if (not pair_dict.has_key(key)):
                prob = 0
            else:
                pair_count = float(pair_dict[key])
                prob = pair_count / tag_count
            if prob > max_prob:
                max_prob = prob
                max_tag = tag
        out.write(line.strip() + ' ' + max_tag + '\n')
    dev.close()
    out.close()

def usage():
    print 'compute the emission probability'
    print '3 parameter need '
    print 're_count.py <option> <input> <output>'

def main():
    args = sys.argv
    if len(args) != 5:
        usage()
        exit()
    if args[1] == '0':
        generate(args[2], args[3], args[4])
    elif args[1] == '1':
        test(args[2], args[3], args[4])
    else:
        usage()

if __name__ == '__main__':
    main()
