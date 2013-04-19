#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__="Shiwei Wu <dsybswsw@gmail.com>"
__date__ ="$April 5, 2013"

RARE_TAG = '_RARE_'

def re_write(org_path, word_count_path, dst_path):
    org_file = open(org_path, 'r')
    word_count_file = open(word_count_path, 'r')
    dst_file = open(dst_path, 'w')
    word_count = {}
    for wc in word_count_file.readlines():
        tokens = wc.split(' ')
        number = int(tokens[1])
        word = tokens[0]
        word_count[word] = number

    for line in org_file.readlines():
        tokens = line.split(' ')
        rule_type = tokens[1]
        if rule_type != 'UNARYRULE':
            dst_file.write(line.strip() + '\n')
        else:
            terminal = tokens[3].strip()
            if not word_count.has_key(terminal):
                terminal = RARE_TAG
            newline = tokens[0] + ' ' \
                + tokens[1] + ' ' + tokens[2] + ' ' + terminal
            dst_file.write(newline.strip() + '\n')
    word_count_file.close()
    org_file.close()
    dst_file.close()

if __name__ == '__main__':
    org_path = 'parse_train.counts.no_cutoff'
    word_count = 'word.count'
    dst_path = 'parse_train.counts.out'
    re_write(org_path, word_count, dst_path)
