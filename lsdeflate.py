#!/usr/bin/env python
"""
Deflate output from `ls -1` by gathering groups of files.
The most important here are numbered groups of files, since those are likely to
use the most screen space and have the least complexity.
Rules for gathering files:
    * Perform at most a double expansion (2 brace expressions, count)
      * Of which one before and one after the dot (each part)
      * First perform basename matching, look for extension overlap later
    * The size of each expanded block should be < 1/2 of basename length (length)
      * Only for string matches
    * Allow zero-length expansions
    * Match only full extensions
    * Number sequences must be expressible as bash sequences
      * Start, stop, stride or list (max length 6, no sequence as sublist)

Other important design criteria:
    * Do not require sorted input
        * Input-order independent algorithm
            * Required for reliable front-and-back matching
    * Run quickly, and scale well (better than O(n^2))

Other ideas:
    * Do not match files of different type (symlink, folder, file)
      * This allows highlighting based on type to be reused
      * No substitute for permission-based highlighting, used in many shells
      * Otherwise, add a / for folders?

## Example cases
a.txt, b.txt -> {a,b}.txt
abla.txt, b.txt -> no (count)
blabla.txt, b.txt -> no (length)
a1c.txt, b1d.txt -> no (count)
alpha1.txt, alpha.txt -> alpha{,1}.txt
alpha.txt, alpha.doc -> alpha.{txt,doc}
alpha1.txt, alpha2.txt, alpha1.doc, alpha2.doc -> alpha{1,2}.{txt,doc}
a1.txt, a2.doc, a2.txt -> a2.doc, a{1,2}.txt
### Series examples
Here are some examples of series we should be able to resolve, in order of importance.
0 1 2 3 4 -> {0..4}
0 2 4 5 -> {0..4..2} 5 # extra check for shortness? Just listing is better here
0 2 3 4 6 -> {0..6..2} 3
0 4 8 16 20 -> {0..8..4} {16..20..4} # shortness check again!
### Preference examples
Which would we rather have?
a.txt, b.txt, c.txt, a.doc, b.doc -> {a,b,c}.txt, {a,b}.doc
or {a,b}.{txt,doc}, c.doc?
I think the former, so let's do expansion inside an extension first.

## Rough description of the algorithm
* Collect all filenames, group by extension
* For each extension group:
    First pass:
        Extract numbers for set with same head and tail (possibly (both) empty)
            Take \d+[.]?\d? and convert it to an integer
                (storing position of decimal and number length)
            Do not support multiple sets of numbers yet, just take the first one
            Sort the numbers
            (1) Calculate elementwise differences
            Find the longest block-sequence. Sum the block to get the longest period
                From the start of the block-sequence, go forwards and backwards
                    find matching elements and save them with the sequence
                Restart at (1) unless the sequence is empty
        Write set of matching range expansions
    Second pass (future work):
        On all unmatched files:
            Sort by minimum required head and tail match [1]

            
* Perform full-extension match only between outputs of above simplification
  * Do not allow partial extensions
  * Ignore any patterns in results on basename match

[1] Since we require at most a half-basename match there must be a significant
head or tail match, of at least 1/4th (rounded down) 

"""
from __future__ import print_function
import sys
import itertools
import numpy as np
import re
from collections import defaultdict

SEQUENCE_WITH_NUM_REGEX=re.compile(r"^([^0-9]*)(\d*)(.*)$")
# Captures the prefix, a number (possibly empty string) and a suffix
# will capture the first number only


"""
Print an enumeration expansion
"""
def print_enum_expansion(head,tail,values):
    print("%s{%s}%s"%(head,min,','.join(values)))


"""
Split a list of names into a dict where the key is the extension and the value
is a list of basenames"
"""
def group_names_by_ext(lines):
    names = [line.rstrip().rsplit('.', 1) for line in lines] # split on last dot
    ext_groups = {}
    for name in names:
        if len(name) == 2:
            ext = '.'+name[1]
        else:
            ext = ''
        ext_groups.setdefault(ext, []).append(name[0])
    return ext_groups

"""
Convert a list of numbers into a set of ranges, with optional increment and no overlap.

Perhaps we can do something clever here with a fourier transform?
For now we have a simple algorithm:
    Calculate difference between numbers
    Split into ranges where this step is constant.
"""
def list_to_ranges(lst):
    diffs = lst[1:] - lst[:-1] # between elements
    block_edges = np.nonzero(diffs[1:] != diffs[:-1]) # true if timestep changed after i+1
    block_edges = np.append(np.insert(block_edges, 0,0), tmp.shape[0]-1)
    ranges = []
    for a, b in zip(block_edges[:-1], block_edges[1:]):
        ranges.append((lst[a], lst[b], diffs[a+1]))
    return ranges


if __name__ == "__main__":
    grouped_names = group_names_by_ext(sys.stdin)

    # First group inside basename
    all_out = []
    for ext in grouped_names:
        basenames = grouped_names[ext]
        # Extract the numeric and non-numeric parts
        # Store into dict by tuple (prefix,suffix) if there is a number found
        # or directly put basename in output list
        grouped_numbers_str = defaultdict(list)
        output = []
        for basename in basenames:
            m = re.match(SEQUENCE_WITH_NUM_REGEX, basename)
            prefix, num, suffix = [m.group(i) for i in [1,2,3]]
            if (len(num) == 0): # no match
                output.append(basename)
            else:
                grouped_numbers_str[(prefix,suffix)].append(num)

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
                for min,max,step in ranges:
                    if (step == 1):
                        step_s = ""
                    else:
                        step_s = "..%d"%step
                    output.append("%s{%s..%s%s}%s"%(key[0],min,max,step_s,key[1]))
        # gather output
        all_out = all_out + list(map(lambda s: s + ext, output))
    all_out.sort()
    print("\n".join(all_out))
