#! /usr/bin/env python3
# coding: utf-8
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.attributes import attributes_filter
import pm4py
from pm4py.util.xes_constants import KEY_KEYS
from alpha_miner import Alpha
import os
import sys



def main(argv):
    log = xes_importer.apply('/Users/jenny/Downloads/datasets/L1.xes')
    variants = pm4py.get_variants_as_tuples(log)
    Alpha(variants.keys())

   

if __name__ == "__main__":
    main(sys.argv)