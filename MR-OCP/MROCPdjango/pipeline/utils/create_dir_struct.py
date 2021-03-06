#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to create the directories necessary for the OCPIPELINE
"""

import os
import argparse
from shutil import move # For moving files

def create_dir_struct(resultDirs, derivFiles = None):
  '''
  @param resultDirs: Directories to hold results
  @type resultDirs: string

  @param derivFiles: The name of the derivatives files uploaded
  @type derivFiles: string
  '''

  newDir = ''
  if (derivFiles):
    for folder in resultDirs.split('/'):
      if (folder != ''):
        newDir += '/' + folder
        if not os.path.exists(newDir):
          os.makedirs(newDir)
        else:
          print "%s, already exists" % newDir

    for subfolder in ['derivatives/', 'rawdata/', 'graphs/', 'graphInvariants/']:
      if not os.path.exists(os.path.join(newDir, subfolder)):
        os.makedirs (os.path.join(newDir, subfolder))
      else:
        print "%s, already exists" % os.path.join(newDir, subfolder)

    ''' Move files into a derivative folder'''
    #### If duplicate proj,subj,session,site & scanID given - no duplicates for now #####
    for f in derivFiles:
      if not os.path.exists(os.path.join(resultDirs,'derivatives', f.split('/')[-1])):
        move(f, os.path.join(resultDirs, 'derivatives'))
    return

  for folder in resultDirs:
    if not os.path.exists(folder):
      os.makedirs(folder)
    else:
      print "%s, already exist" % folder

def main():
  parser = argparse.ArgumentParser(description='Create appropriate dir structure for a project')
  parser.add_argument('resultDir', action="store")
  parser.add_argument('derivFiles', action="store", default = None)

  result = parser.parse_args()

  create_dir_struct(result.resultDir, result.derivFiles)

if __name__ == '__main__':
  main()
