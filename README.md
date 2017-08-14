# Group numbered output in ls
Every now and then you stumble upon a directory that just has too. many. files.
If these files are numbered, you can use `lsdeflate` to reduce your cognitive load.
![Demo](demo.png?raw=true)

## Installation
Installation is simple: put `lsdeflate.py` somewhere in your path and create an alias:

    alias lsd='ls -1 --color=always | lsdeflate.py'

## Contributing
This is still very crude software. Feel free to create pull requests for changes and improvements!


# Notes (not necessarily up to date)
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

