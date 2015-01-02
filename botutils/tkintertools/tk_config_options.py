#!python3
'''
Simply file for storing default windowing look and feel
'''
from tkinter import *

common = {
        'bg':       '#003D78', #Noble colors
        'padx':     5,
        'pady':     5,
        'relief':   RAISED,
    }

text = common.copy()
text['font']=('Helvetica', '10', 'bold')
text['fg']='#DEB407' #Noble colors
