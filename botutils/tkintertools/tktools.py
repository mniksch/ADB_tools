#!python3
'''
This file contains a set of utility functions to query users via a window
instead of having them enter options from a command line
'''
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from botutils.tkintertools import tk_config_options as c_options

#Need to add eventually
#class SingleInput(Frame):
#    def createWidgets(self, **options):
#        #ins is a list 0=value, 1=description, 2=vartype

class SingleFileName(Frame):
    def createWidgets(self, **options): 
        #ins is a list 0=value, 1=description 2='r' or 'w'
        self.desc = Label(self, text=self.ins[1],
                width=len(self.ins[1]), justify=RIGHT, **options)
        self.desc.pack(side=LEFT, expand=YES, fill=BOTH)
        self.CHG = Button(self, text=self.ins[0],
                command=self.trigger, **options)
        self.CHG.pack(side=RIGHT, expand=YES, fill=BOTH)
    def trigger(self):
        if self.ins[2] == 'r':
            val = askopenfilename(initialfile=self.ins[0])
        else:
            val = asksaveasfilename(initialfile=self.ins[0])
        self.CHG['text'] = val
        self.ins[0] = val
        self.CHG['width']=len(val)
    
    def __init__(self, root, ins, **options):
        Frame.__init__(self, root)
        self.pack()
        self.ins = ins
        self.createWidgets(**options)

class CheckPickApp(Frame):
    ''' class for working with the check_pick_from_list function'''
    def createWidgets(self, prompt, default, **options):
        self.desc = Message(self, text=prompt, width=500, **options)
        self.desc.pack(side=TOP, expand=YES, fill=BOTH)

        self.vars = []
        for option in self.pick_options:
            var = IntVar()
            Checkbutton(self,
                        text=option,
                        variable=var,
                        **options).pack(side=TOP, anchor=W)
            var.set(default)
            self.vars.append(var)

        Button(self, text='OK', command=self.endMe, **options).pack(
                side=TOP, expand=YES, fill=BOTH)

    def __init__(self, root, pick_list, prompt, default, **options):
        Frame.__init__(self, root)
        self.pack()
        self.pick_options = pick_list
        self.createWidgets(prompt, default, **options)

    def endMe(self):
        new_return = []
        for i in range(len(self.vars)):
            if self.vars[i].get(): new_return.append(self.pick_options[i])
        self.pick_options[0] = new_return
        self.master.destroy()

class ButtonPickApp(Frame):
    ''' class for working with get_buttons_answer function'''
    def createWidgets(self, prompt, **options):
        self.desc = Message(self, text=prompt, width=500, **options)
        #self.desc = Message(self, text=prompt, width=len(prompt), **options)
        self.desc.pack(side=TOP, expand=YES, fill=BOTH)
        for choice in self.pick_options:
            func = lambda choice=choice: self.endMe(choice)
            Button(self, text=choice, command=func, **options).pack(
                    side=TOP, expand=YES, fill=BOTH)
    def __init__(self, root, pick_list, prompt, **options):
        Frame.__init__(self, root)
        self.pack()
        self.pick_options = pick_list
        self.createWidgets(prompt, **options)
    def endMe(self, selected):
        #Kind of a hack, but this returns the selected value by putting
        #it at the top of the sent list for the calling function to inspect
        self.pick_options.insert(0, selected)
        self.master.destroy()


class DropDownApp(Frame):
    ''' class for working with get_dropdown_answer function'''
    def createWidgets(self, prompt):
        self.PICKS = Listbox(self)
        for item in self.pick_options:
            self.PICKS.insert(END, item)

        self.QUIT = Button(self)
        self.QUIT['text'] = 'SUBMIT'
        self.QUIT['fg'] = 'blue'
        self.QUIT['command'] = self.endMe

        self.QUIT.pack({'side': 'right'})

        self.PICKS.pack({'side': 'right'})
        self.PROMPT = Label(self, text=prompt,
                                anchor='w',
                                relief='raised',
                                font=('Helvetica', '16'),
                                width=20,
                                wraplength=240)
        self.PROMPT.pack({'side': 'top'})

    def endMe(self):
        #Kind of a hack, but this returns the selected value by putting
        #it at the top of the sent list for the calling function to inspect
        self.pick_options.insert(0, 
                self.pick_options[self.PICKS.curselection()[0]])
        self.master.destroy()

    def __init__(self, root, pick_list, prompt):
        Frame.__init__(self, root)
        self.pack()
        self.pick_options = pick_list
        self.createWidgets(prompt)

class _get_filenames(Frame):
    def __init__(self, arg_dict, **options):
        Frame.__init__(self)
        self.pack()
        if len(arg_dict) > 1:
            lab_text = 'Please select filenames then click "OK"'
        else:
            lab_text = 'Please select filename then click "OK"'
        #Label(self,text=lab_text, width=len(lab_text),
        Message(self,text=lab_text, width=500,
              **options
                    ).pack(side=TOP, expand=YES, fill=BOTH)
        for fn in arg_dict.values():
            SingleFileName(self, fn, **options
                            ).pack(side=TOP, expand=YES, fill=BOTH)
        Button(self, text='OK', command=self.master.destroy, **options
                ).pack(side=BOTTOM, expand=YES, fill=BOTH)


        
def get_filenames(arg_dict):
    '''
    Function to grab a variable number of filenames as passed by the dict
    where values from the dictionary are two item lists--0=value and 1=label
    2='r' or 'w' to indicate planned file mode
    key
    '''
    fileGrabber = _get_filenames(arg_dict, **c_options.text)
    fileGrabber.mainloop()

def check_pick_from_list(options_list, prompt, default=1):
    '''
    This function will take a list of options and have a list of
    checks to select. If default=True, they will begin checked
    initially
    '''
    top = Tk()
    top.wm_title(prompt)
    sent_list = options_list[:]
    app = CheckPickApp(top, sent_list, prompt, default, **c_options.text)
    app.mainloop()
    return sent_list[0]

def get_buttons_answer(options_list, prompt):
    '''
    This function will take a list of options, each for it's own button and
    a prompt and return the item that the user selected
    '''
    top = Tk()
    top.wm_title(prompt)
    sent_list = options_list[:]
    app = ButtonPickApp(top, sent_list, prompt, **c_options.text)
    app.mainloop()
    return sent_list[0]

def get_yes_no(prompt):
    '''
    Wrapper function for calling get_buttons_answer as a yes_no option
    '''
    response = get_buttons_answer(['Yes', 'No'], prompt)
    if response == 'Yes':
        return True
    else:
        return False


def get_dropdown_answer(pick_list, prompt):
    '''
    This function will take a list of options for a dropdown along with
    a prompt and return the item that the user selected
    '''
    top = Tk()
    top.wm_title(prompt)
    sent_list = pick_list[:]
    app = DropDownApp(top, sent_list, prompt)
    app.mainloop()
    return sent_list[0]

if __name__ == '__main__':
    '''
    # for the get_dropdown_answer function
    sample_list = ['Red', 'Yellow', 'Green', 'Rainbow colored']
    prompt = 'Please select the color you love the most'
    response = get_dropdown_answer(sample_list,prompt)
    print('The user picked the (%s) campus.' % response)
    '''
    sample_list = ['Red', 'Yellow', 'Green', 'Rainbow colored']
    prompt = 'Please select the color you love the most'
    response = get_buttons_answer(sample_list,prompt)
    print('The user picked the (%s) campus.' % response)
    '''
    # For the get_filenames function
    ins = {'sch': ['filename','Pick a filename', 'w'],
            'out':['outfile','Pick an output file', 'r']}
    print('Prior to running: %s', str(ins))
    get_filenames(ins)
    print('After running: %s', str(ins))
    s = input('---(hit enter)---')
    '''

