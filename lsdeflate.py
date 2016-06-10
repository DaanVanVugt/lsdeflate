#!/usr/bin/env python
from __future__ import print_function
import sys
import itertools
import os.path

"""
Match the head and tail common between two files
"""
def match_head(line, line2):
    return os.path.commonprefix([line,line2])
def match_tail(line, line2):
    return os.path.commonprefix([line[::-1],line2[::-1]])[::-1]

"""
Create a parameter expansion
"""
def create_expansion(head,zeros,start,end,tail):
    return "%s%s{%s..%s}%s"%(head, zeros, start, end, tail)

"""
find a parameter expansion (ignores leading zeros)
very dumb implementation, only checks the min and maximum, no stride supported yet
"""
def find_expansion(nums):
    if (len(nums) > 0):
        imax = max(nums, key=int)
        imin = min(nums, key=int)
        zeros = str(imax).zfill(len(nums[0]))[:-len(str(imax))]
        return (zeros,imin,imax)
    else:
        return ("",None,None)

"""
Find an expansion and print it

Algorithm: 
    remove head and tail from cache
    if numeric:
        sort
        find min, max
        find next lowest min value (min')
        step up in steps of min'-min until end or no match
            repeat if necessary
        print
    if non-numeric:
        print brace expansion
"""
def find_and_print_expansion(cache, head, tail):
    if len(head) > 0: cache = [s[len(head):] for s in cache]
    if len(tail) > 0: cache = [s[:-len(tail)] for s in cache]
    if cache[0].isnumeric():
        cache.sort(key=int)
        while len(cache) > 0:
            to_delete = []
            for i, elem in enumerate(cache):
                if i == 0: min = elem
                elif i == 1: step = int(elem) - int(min)
                else:
                    if (int(cache[i]) - int(cache[i-1]) != step):
                        print_numeric_expansion(head,tail,min,cache[i-1],step)
                        to_delete = range(0,i-1)
                        break # out of for loop
            if (len(to_delete) > 0):
                for i in to_delete: del cache[i]
            else:
                print_numeric_expansion(head,tail,min,cache[-1],step)
                break
    else:
        print("%s{%s}%s"%(head,','.join(cache),tail))

"""
Print a numeric expansion
"""
def print_numeric_expansion(head,tail,min,max,step=1):
    if (step == 1):
        print("%s{%s..%s}%s"%(head,min,max,tail))
    else:
        print("%s{%s..%s..%s}%s"%(head,min,max,step,tail))


# Prepare variables
line2 = sys.stdin.readline().strip()
cache = []
head_old = ""
tail_old = ""
for line in sys.stdin:
    cache.append(line2)
    line = line.strip()
    head = match_head(line,line2)
    tail = match_tail(line,line2)

    # Test if we should put these in the same bin
    # Only allowable difference is a single integer at the end of the head
    # This allows for zero and non-zero padded numbers
    l = len(head) - len(head_old)
    if (l == 0):
        head_same = (head == head_old)
    elif (l == 1):
        head_same = head[-1].isnumeric()
    elif (l == -1):
        head_same = head_old[-1].isnumeric()
    else:
        head_same = False

    line2 = line
    # Print if there was a match and it is gone now
    if (head_old != "" and tail_old != "" and not (tail == tail_old and head_same)):
        # Compare first and last element instead of last 2
        find_and_print_expansion(cache, match_head(cache[0],cache[-1]), match_tail(cache[0],cache[-1]))
        cache = []
        head_old = ""
        tail_old = ""
    else:
        head_old = head
        tail_old = tail
find_and_print_expansion(cache, match_head(cache[0],cache[-1]), match_tail(cache[0],cache[-1]))
