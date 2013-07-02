# @Author: Disa Mhembere
# Example code of how to upload a previously built
# graph and run some invariants on it.

import urllib2
import argparse
import sys
import os

import zipfile
import tempfile

import webbrowser

def main():

  parser = argparse.ArgumentParser(description='Upload a single or multiple graphs, & possibly lcc\'s via a single zipped dir. \
                                  Base url -> http://www.mrbrain.cs.jhu.edu/disa/graphupload/')
  parser.add_argument('url', action="store", help='url is http://mrbrain.cs.jhu.edu/disa/graphupload/{l|lcc} where l|lcc means use the lcc. If no lcc is uploaded it will be computed. If you don\'t want to use lcc skip the l|lcc part')
  parser.add_argument('webargs', action="store", help='comma separated list (no spaces) of invariant types. E.g cc,tri,deg,mad,eig,ss1 for \
                      clustering coefficient, triangle count, degree, maximum average degree, eigen-pairs & scan statistic')
  parser.add_argument('zippedFile', action="store", help ='Data zipped directory with one or more graphs and OPTIONAL corresponding lcc(s) named correctly.')
  parser.add_argument('--convertToFormat', '-c', action='store', help='comma separated list of convert to formats. Currently choices: mat (result is npy)')

  result = parser.parse_args()

  if not (os.path.exists(result.zippedFile)):
    print "Invalid file name. Check the folder: " + result.zippedFile
    sys.exit()
  else:
    print "Loading file into memory.."

  # Create a temporary file to store zip contents in memory
  tmpfile = tempfile.NamedTemporaryFile()
  zfile = zipfile.ZipFile ( tmpfile.name, "w" )

  zfile.write(result.zippedFile)
  zfile.close()

  tmpfile.flush()
  tmpfile.seek(0)

#  Testing only: check the contents of a zip file.
#
#    rzfile = zipfile.ZipFile ( tmpfile.name, "r" )
#    ret = rzfile.printdir()
#    ret = rzfile.testzip()
#    ret = rzfile.namelist()
#    import pdb; pdb.set_trace()

  result.url = result.url if result.url.endswith('/') else result.url + '/' #

  if result.convertToFormat:
    result.webargs = result.webargs if result.webargs.endswith('/') else result.webargs + '/'

  result.convertToFormat = "" if not result.convertToFormat else result.convertToFormat
  
  try:
    ''' *IMPORTANT: HOW TO BUILD THE URL '''
    req = urllib2.Request ( result.url + result.webargs + result.convertToFormat, tmpfile.read() )  # concatenate project with assigned scanID & call url
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error %s" % (e.read())
    sys.exit(0)

  msg = response.read() # Use this response better
  print msg

  ''' Open up a tab in your browser to view results'''
  webbrowser.open(msg.split(' ')[3]) # This might change

#webbrowser.open('http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects' + redir)

if __name__ == "__main__":
  main()
