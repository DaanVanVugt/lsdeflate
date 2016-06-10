# Group numbered output in ls
Every now and then you stumble upon a directory that just has too. many. files.
If these files are numbered, you can use `lsdeflate` to reduce your cognitive load.
![Demo](demo.png?raw=true)

## Installation
Installation is simple: put `lsdeflate.py` somewhere in your path and create an alias:

    alias lsd='ls -1 --color=always | lsdeflate.py | column'

This also columnates the output to the width of your terminal.
Colour output can cause the columnation to be less wide than expected.

## Contributing
This is still very crude software. Feel free to create pull requests for changes and improvements!
