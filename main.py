#! /usr/bin/env python3
# coding: utf-8
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.attributes import attributes_filter
import pm4py
from pm4py.util.xes_constants import KEY_KEYS
from alpha_miner import Alpha
from heuristic_miner import Heuristic
import sys



def main(argv):
    log = xes_importer.apply('/Users/jenny/Downloads/datasets/L5.xes')
    tracefilter_log_pos = attributes_filter.apply_events(log, ["complete"],
                                         parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: "lifecycle:transition", attributes_filter.Parameters.POSITIVE: True})
    variants = pm4py.get_variants_as_tuples(tracefilter_log_pos)
    Alpha(variants.keys())
    Heuristic(variants.keys(), 1, 0.5)


 
   

if __name__ == "__main__":
    main(sys.argv)


