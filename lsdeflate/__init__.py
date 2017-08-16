#!/usr/bin/env python
from __future__ import print_function
import itertools
import numpy as np
import re
from collections import defaultdict

SEQUENCE_WITH_NUM_REGEX=re.compile(r"^(.*[^0-9])(\d\d\d*)(.*)$")
# Captures the prefix, a number (possibly empty string) and a suffix
# will capture the first number only


"""
Split a list of names into a dict where the key is the extension and the value
is a list of basenames"
"""
def group_names_by_ext(lines):
    names = [line.rstrip().rsplit('.', 1) for line in lines] # split on last dot
    ext_groups = defaultdict(list)
    for name in names:
        if len(name) == 2:
            ext = '.'+name[1]
        else:
            ext = ''
        ext_groups[ext].append(name[0])
    return ext_groups


"""
Convert a list of numbers into a set of ranges, with optional increment

Perhaps we can do something clever here with a fourier transform?
For now do a simple recursive algorithm:
    Find the longest sequence
    Subtract this from the list
    recurse
"""
def list_to_ranges(lst):
    if not isinstance(lst, np.ndarray): lst = np.asarray(lst)
    if lst.shape[0] == 0: return []
    if lst.shape[0] == 1: return [(lst[0],lst[0],1)]
    diffs = lst[1:] - lst[:-1] # between elements
    block_edges = np.asarray(np.nonzero(diffs[1:] != diffs[:-1]))+1 # indices where the diffs have changed
    block_edges = np.append(np.insert(block_edges, 0,0), lst.shape[0]-1)
    block_lengths = block_edges[1:] - block_edges[:-1]
    longest_block = np.argmax(block_lengths)
    istart = block_edges[longest_block]
    iend   = block_edges[longest_block+1]
    rest = np.zeros(lst.shape[0]-1-iend+istart,dtype=np.int)
    rest[:istart] = lst[:istart]
    rest[istart:] = lst[iend+1:]
    return sorted([(lst[istart],lst[iend],diffs[istart])] + list_to_ranges(rest),
                  key=lambda x:x[0])


"""
Takes a set of basenames and calculate ranges
"""
def group_basenames(basenames):
    # Extract the numeric and non-numeric parts
    # Store into dict by tuple (prefix,suffix) if there is a number found
    # or directly put basename in output list
    grouped_numbers_str = defaultdict(list)
    output = []
    for basename in basenames:
        m = re.match(SEQUENCE_WITH_NUM_REGEX, basename)
        if m is not None:
            prefix, num, suffix = [m.group(i) for i in [1,2,3]]
            if (len(num) == 0): # no match
                output.append(basename)
            else:
                grouped_numbers_str[(prefix,suffix)].append(num)
        else:
            output.append(basename)

    # Now that we have a set of numbers, find sequences
    for key in grouped_numbers_str:
        # Skip those were we only have one match
        if (len(grouped_numbers_str[key]) < 2):
            output.append(key[0] + grouped_numbers_str[key][0] + key[1])
            continue
        tmp = np.fromiter(map(int, grouped_numbers_str[key]), dtype=np.int)
        sort_order = np.argsort(tmp)

        # Work around bug in numpy. If len(sort_order) == 1 we can just not sort
        if (sort_order.shape[0] > 1):
            sort_order = np.s_[:]
        tmp = tmp[sort_order]
        tmp_s = grouped_numbers_str[key][sort_order]

        # if there are just 2 we cannot run the algorithm, just return both
        if (tmp.shape[0] <= 2):
            for num_s in tmp_s:
                output.append(key[0] + num_s + key[1])
        else:
            ranges = list_to_ranges(tmp)
            for imin,imax,step in ranges:
                smin = grouped_numbers_str[key][imin]
                smax = grouped_numbers_str[key][imax]
                # Remove leading zeros
                n_leading_zero = len(smax) - len(smax.lstrip('0'))
                # Remove trailing zeros and rescale step
                n_trailing_zero = len(smax) - len(smax.rstrip('0'))


                # Check how many of the trailing zeros we can take
                n_zero_step = np.log10(step)
                if (n_zero_step % 1 != 0): n_zero_step = 0
                n = min(int(n_zero_step), n_trailing_zero)
                tail = "0"*n
                head = "0"*n_leading_zero

                if n > 0: step = step/(10**n)
                if (step == 1):
                    step_s = ""
                else:
                    step_s = "..%d"%step

                if (n == 0): n = -len(smax) # selecting -0 doesn't work
                smin = smin[n_leading_zero:-n]
                smax = smax[n_leading_zero:-n]

                if (smin == smax):
                    output.append("%s%s%s%s%s"%(key[0],head,smin,tail,key[1]))
                else:
                    output.append("%s%s{%s..%s%s}%s%s"%(
                        key[0],head,smin, smax, step_s, tail, key[1]))
    return output
