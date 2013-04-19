#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__="Shiwei Wu <dsybswsw@gmail.com>"
__date__ ="$April 5, 2013"

def load_config(file_path):
    config = open(file_path, 'r')
    options = {}
    for line in config:
        key_value = line.split('=')
        if len(key_value) != 2:
            continue
        key = key_value[0].strip()
        value = key_value[1].strip()
        options[key] = value
    config.close()
    return options

