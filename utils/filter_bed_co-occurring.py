#!/usr/bin/env python3

import sys
import os
import argparse
from random import choice

## Read input options
# Options
parser = argparse.ArgumentParser()
parser.add_argument("-i", dest = "input", type = str, help = "Sorted BED file (can be gzipped)")
parser.add_argument("-d", dest = "dist", type = int, default = 500, help = "Minimum distance between BED entries")
parser.add_argument("-c", dest = "col", type = int, help = "Which column should be used for breaking ties (1-based)")
parser.add_argument("-t", dest = "ties", type = str, help = "Use [min,max] for ties")

args = parser.parse_args()


## Auxiliary functions

def open_maybe_gzipped(filename):
    with open(filename, 'rb') as test_read:
        byte1, byte2 = test_read.read(1), test_read.read(1)
        if byte1 and ord(byte1) == 0x1f and byte2 and ord(byte2) == 0x8b:
            f = gzip.open(filename, mode='rt')
        else:
            f = open(filename, 'rt')
    return f


if args.ties == "max":
    def keep_previous(current, previous):
        if current == previous:
            return choose([True, False])
        else: 
            keep = previous > current 
            return keep
elif args.ties == "min":
    def keep_previous(current, previous):
        if current == previous:
            return choose([True, False])
        else: 
            keep = previous < current
            return keep
else:
    sys.exit("""Comparison should be either "min" or "max"!""")


## Main script

infile    = args.input
min_dist  = args.dist
val_index = args.col - 4

with open_maybe_gzipped(infile) as input_stream:
        
        # Read first line separately
        previous_line = input_stream.readline().strip()
        previous_bed_info = previous_line.split("\t")
        previous_chrom = previous_bed_info.pop(0) 
        previous_start = int(previous_bed_info.pop(0))
        previous_end   = int(previous_bed_info.pop(0))
        previous_value = float(previous_bed_info[val_index])

        # Read rest of the file
        for line in input_stream:
            line = line.strip()
            bed_info = line.split("\t")
            chrom = bed_info.pop(0)
            start = int(bed_info.pop(0))
            end   = int(bed_info.pop(0))
            value = float(bed_info[val_index])
            # print(value)
            
            # We are in the same chromosome
            if chrom == previous_chrom:
                dist_from_last = abs(start - previous_end)
                
                # Entries are far enough apart - print previous entry and update values
                if dist_from_last > min_dist:
                    print(previous_line)
                    previous_chrom = chrom
                    previous_start = start
                    previous_end   = start
                    previous_value = value
                    previous_line  = line
                
                # Entries are too close - decide which we want to keep
                else:
                    keep = keep_previous(value, previous_value)
                    
                    # Current value is desirable - update everything
                    if not keep:
                        previous_line = line
                        previous_chrom = chrom
                        previous_start = start
                        previous_end   = start
                        previous_value = value
                    # else: do nothing - we discard current value
            
            # We changed chromosomes - print previous and update values
            else:
                print(previous_line)
                previous_chrom = chrom
                previous_start = start
                previous_end   = start
                previous_value = value
                previous_line  = line
            # print(*[previous_chrom, previous_start, previous_end, previous_value] + bed_info)
        # Print last line
        print(previous_line)
# We're done
