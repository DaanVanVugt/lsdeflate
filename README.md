# Group numbered output in ls
Every now and then you stumble upon a directory that just has too. many. files.
If these files are numbered, you can use lsdeflate (aliased to lsd?) to reduce your cognitive load.

Installation is simple: put lsdeflate.py somewhere in your path and create an alias:

    alias lsd='ls -1 | lsdeflate.py'

## Contributing
This is still very crude software. Feel free to create pull requests for changes and improvements!
