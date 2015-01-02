#!python3
'''
This module is designed for working with zip files
The main function takes a directory and replaces it with a zip file
'''
import zipfile
import os

def compress(filefolder):
    '''Will replace a folder with a zip file of the same name
       NOTE: will only work with a flat directory--does not nest'''
    zipfn = os.path.basename(filefolder) + '.zip'
    with zipfile.ZipFile(zipfn, 'w', zipfile.ZIP_DEFLATED) as myzip:
        os.chdir(filefolder)
        for file in os.listdir('.'):
            print('Compressing %s.' % file)
            myzip.write(file)
            os.remove(file)
    os.chdir('..')
    os.rmdir(filefolder)
