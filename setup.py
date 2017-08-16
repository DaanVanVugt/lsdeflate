from distutils.core import setup
setup(
  name = 'lsdeflate',
  packages = ['lsdeflate'], # this must be the same as the name above
  version = '0.3',
  description = 'Compress ls output by gathering numeric ranges into brace expansions',
  author = 'Daan van Vugt',
  author_email = 'daanvanvugt@gmail.com',
  url = 'https://github.com/exteris/mypackage', # use the URL to the github repo
  download_url = 'https://github.com/exteris/lsdeflate/archive/0.3.tar.gz', # I'll explain this in a second
  keywords = ['unix', 'ls', 'directory', 'clean'], # arbitrary keywords
  classifiers = [],
  scripts=['bin/lsdeflate'],
)
