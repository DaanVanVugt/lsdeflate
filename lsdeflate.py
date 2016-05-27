#!/usr/bin/env python
from __future__ import print_function
import sys
import re

NUM_RE = re.compile(r"([^0-9]*)([0-9]+)([^0-9]*)")

"""
return the head, number and tail of a file
"""
def match_numeric(line):
    return NUM_RE.match(line)

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
"""
def find_and_print_expansion(head,tail,nums):
    if (len(nums) > 1):
        (zeros,start,end) = find_expansion(nums)
        sys.stdout.write(create_expansion(head,zeros,start,end,tail))
    elif (len(nums) == 1):
        sys.stdout.write(head+nums[0]+tail)

k = None
nums = []
for line in sys.stdin:
    # Check for a number in the output
    m = match_numeric(line)
    if (m):
        k_old = k
        k = (m.group(1),m.group(3))
        if (k != k_old and k_old is not None):
            # Write out all lines we have
            find_and_print_expansion(k_old[0],k_old[1],nums)
            nums = []
        nums.append(m.group(2))
    else:
        # Write out all lines we have
        find_and_print_expansion(k[0],k[1],nums)
        nums = []

        # Write out this line
        sys.stdout.write(line)

if (len(nums) > 0):
    find_and_print_expansion(k[0],k[1],nums)
