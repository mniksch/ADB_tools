#!python3
'''
Module used by merge_nsc.py that specifies all the enrollment related
details, including an enumeration of all of the matching cases for
enrollment records from NSC or the database
'''

from datetime import date, datetime
from botutils.tabletools import tableclass as tc
from botutils.ADB import EnrollmentNamespace as e

def strYYYY_MM_DD_to_date(val):
    '''Helper function to convert a 'YYYY-MM-DD' string to a date'''
    if val: #checks for None or ''; will otherwise fail
        return datetime.strptime(val, '%Y-%m-%d').date()
    else:
        return None

def get_enr_field_list(from_db=False):
    '''Helper function to localize the specification of fields used'''
    fl = [  e.Student__c,
            e.College__c,
            e.Start_Date__c,
            e.End_Date__c,
            e.Date_Last_Verified__c,
            e.Status__c,
            e.Degree_Type__c,
            e.Data_Source__c,
            e.Degree_Text__c,
            e.Major_Text__c
            ]
    if from_db:
        fl.extend([e.Id, e.Withdrawal_reason__c, e.Withdrawal_code__c])
    return fl

def get_enrollments_and_chg_vartype(intake_raw, from_db=False):
    '''Helper function to get the exact fields for enrollments'''
    new_table = intake_raw.new_subtable(get_enr_field_list(from_db))
    new_table.apply_func_cols([ e.Start_Date__c,
                                e.End_Date__c,
                                e.Date_Last_Verified__c],
                                strYYYY_MM_DD_to_date)
    new_table.apply_func(e.Status__c, lambda x: None if x is '' else x)
    new_table.apply_func(e.Degree_Type__c, lambda x: None if x is '' else x)
    return new_table

def get_extra_correction(mr, school_type):
    '''Helper function to generate additional flags for badly formed
    database only enrollments'''
    degree_check = db_only_degree_check(mr[6], school_type)
    correction = ''
    if degree_check != mr[6]:
        correction = 'Changed Degree Type from '
        correction += (mr[6] if mr[6] else '<blank>')+' to '+degree_check
    if not mr[4]:
        if correction: correction += ', '
        correction += 'Missing Date Last Verified'
    
    if not mr[5]:
        if correction: correction += ', '
        correction += 'Missing Status'
    elif mr[5] == 'Matriculating':
        if mr[2]:
            if (date.today() - mr[2]).days > 0:
                if correction: correction += ', '
                correction += 'Matriculating enrollment set to start in'
                correction += ' the past (' + mr[2].strftime('%b %Y)')
        else:
            if correction: correction += ', '
            correction += 'Missing Start Date'

    if not mr[7]:
        if correction: correction += ', '
        correction += 'Missing Data Source'

    return correction

def db_only_degree_check(db_degree_type, school_type):
    ''' Helper function like the one below that works for DB only records'''
    if school_type == 'Military Enlistment':
        return 'Employment'
    elif school_type:
        school_degree = "Bachelor's" if ('4' in school_type
                                    ) else "Associate's or Certificate (TBD)"
    else:
        return db_degree_type

    if db_degree_type == school_degree:
        return db_degree_type
    elif not db_degree_type:
        return school_degree
    elif school_degree[0] == 'A' and db_degree_type[0] != 'A':
        if (db_degree_type[0] == 'C' or
            db_degree_type[0] == 'T' or
            db_degree_type[0] == 'E'):
            return db_degree_type
        else:
            return school_degree
    else:
        return db_degree_type



def degree_check(db_degree_type, nsc_degree_type, school_type):
    ''' Helper function that checks to make sure db_degree_type is rational
    before accepting it over nsc_degree_type. Rational in this context means
    not blank and not 'Bachelor's' at a non-4-year school'''
    # Note: if the status is graduated, it's better to take the NSC type
    if school_type == 'Military Enlistment':
        return 'Employment'
    elif school_type:
        school_degree = "Bachelor's" if ('4' in school_type
                                    ) else "Associate's or Certificate (TBD)"
    else: school_degree = nsc_degree_type
    if db_degree_type == school_degree:
        return db_degree_type
    elif not db_degree_type:
        return nsc_degree_type
    elif school_degree[0] == 'A' and db_degree_type[0] != 'A':
        if db_degree_type[0] == 'C':
            return db_degree_type
        else:
            return nsc_degree_type
    else:
        return db_degree_type

def very_diff_start_date(mr, show_status=False):
    '''Helper function to assemble the flag notes for these cases'''
    db_start = mr[13]
    db_end = mr[14]
    nsc_start = mr[2]
    nsc_end = mr[3]
    phrase = 'Database has '
    if show_status: phrase += (mr[16] if mr[16] else '<unknown>') + ' '
    phrase += db_start.strftime('%m/%d/%y-') if db_start else '<unknown>-'
    phrase += db_end.strftime('%m/%d/%y') if db_end else 'present'
    phrase += ' and NSC has '
    if show_status: phrase += mr[5] + ' '
    phrase += nsc_start.strftime('%m/%d/%y-')
    phrase += nsc_end.strftime('%m/%d/%y') if nsc_end else 'present'
    return phrase

def mostly_nsc_enr_update(mr, acc_dict, tricky_SD=False):
    # Id, SD, ED, DLV, Status, DegreeType, Data Source, Degree_Text, Major_Text
    if tricky_SD:
        if not mr[13]:
            sd = mr[2]
        else:
            if (mr[2] - mr[13]).days > 365:
                sd = mr[13] # keep DB start date--enrollment probably under-
                            # reported, e.g. for undocumented
            else:
                sd = mr[2]  # go with NSC start date, alum prob delayed start
    else:
        sd = mr[2]
    return [    mr[21],                 # Id
                sd,                     # Start Date
                mr[3],                  # End Date
                mr[4],                  # Date Last Verified
                mr[5],                  # Status
                degree_check(mr[17],mr[6], acc_dict[mr[1]][1]),
                mr[7],                  # Data Source
                mr[8] if mr[8] else mr[19], # Degree Text
                mr[9] if mr[9] else mr[20], # Major Text
           ]

def mostly_db_enr_update(mr, acc_dict, ed_from_nsc, tricky_SD=False):
    # Id, SD, ED, DLV, Status, DegreeType, Data Source, Degree_Text, Major_Text
    if tricky_SD:
        if not mr[13]:
            sd = mr[2]
        else:
            if (mr[2] - mr[13]).days > 365:
                sd = mr[13] # keep DB start date--enrollment probably under-
                            # reported, e.g. for undocumented
            else:
                sd = mr[2]  # go with NSC start date, alum prob delayed start
    else:
        sd = mr[2]
    return [    mr[21],                 # Id
                sd,                     # Start Date
                mr[3] if ed_from_nsc else mr[14], # End Date
                mr[15],                  # Date Last Verified
                mr[16],                 # Status
                degree_check(mr[17],mr[6], acc_dict[mr[1]][1]),
                (mr[18] if mr[18]=='Transcript/Grade Report'
                        else 'Coordinator Verified'),     # Data Source
                mr[8] if mr[8] else mr[19], # Degree Text
                mr[9] if mr[9] else mr[20], # Major Text
           ]

def deg_con_flag(mr, acc_dict):
    '''helper function to do the flag for records that changed degree type
    but otherwise had no changes'''
    new_deg = degree_check(mr[17],mr[6], acc_dict[mr[1]][1])
    if new_deg != mr[17] and mr[17]:
        flag_text = 'Changed enrollment type from ' +mr[17]
        flag_text += ' to ' + new_deg + ': '
        flag_text += acc_dict[mr[1]][0]
        flag_text += mr[2].strftime(' (%b %Y start)')
        return [mr[0], True, flag_text]
    else:
        return None

def fuzzy_start_match(db_start, nsc_start):
    '''helper function to see if start dates are close enough to ignore
    discrepancy and quietly accept NSC version'''
    daysdiff = (db_start-nsc_start).days
    if -60 < daysdiff < 131:
        return True
    else:
        return False

class MatchCase():
    ''' Base class for working with all the various types of matching. The
    two main functions for matching and for generating output will be
    sub-classed, but this provides the basic structure '''
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

    # matched record consists of first the NSC table then the DB
    def enr_update(self, mr, acc_dict):
        return None
    def new_enr(self, mr):
        return None
    def con_flag(self, mr, acc_dict):
        return None

#---------Cases for comparing records in both the DB and NSC-----------
# The classes below each define a specific type of match and are evaluated
# in order per the 'build_match_cases' function
class PerfectMatch(MatchCase):
    def comp(self, db, nsc):
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         db[2] == nsc[2] and # Start Date
                         db[3] == nsc[3] and # End Date
                         db[5] == nsc[5]     # Status
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        return deg_con_flag(mr, acc_dict)


class PerfectMatchFuzzyStart(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         db[3] == nsc[3] and # End Date
                         db[5] == nsc[5] and # Status
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        return deg_con_flag(mr, acc_dict)

#For all cases below here, it's assumed the end date doesn't exactly match
class SCSt_GG_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         nsc[5] == 'Graduated' and # Status
                         db[5] ==  'Graduated' and # Status
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        return deg_con_flag(mr, acc_dict)

class SCSt_G_Other_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         nsc[5] == 'Graduated' and # Status
                         db[5] !=  'Graduated' and # Status
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        flag_text = 'New unreported graduation (was ' +mr[16]+ '): '
        flag_text += acc_dict[mr[1]][0]
        flag_text += mr[3].strftime(' (%b %Y)')
        return [mr[0], True, flag_text]

class SCSt_A_TW_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         nsc[5] == 'Attending' and # Status
                         (db[5] == 'Transferred out' or
                          db[5] == 'Withdrew') and
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        flag_text = 'NSC indicates still attending (was ' +mr[16]+ '): '
        flag_text += acc_dict[mr[1]][0]
        flag_text += mr[2].strftime(' (%b %Y start')
        if mr[14]: # an actual end date was in the system
            flag_text += mr[14].strftime(' was %m/%d/%Y end)')
        else:
            flag_text += ')'
        return [mr[0], True, flag_text]

class SCSt_AA_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         nsc[5] == 'Attending' and # Status
                         db[5] ==  'Attending' and # Status
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        return deg_con_flag(mr, acc_dict)

class SCSt_A_G_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         nsc[5] == 'Attending' and # Status
                         db[5] ==  'Graduated' and # Status
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_db_enr_update(mr, acc_dict, ed_from_nsc=False)

    def con_flag(self, mr, acc_dict):
        flag_text = 'Graduation not confirmed ('+mr[5]+' in NSC): '
        flag_text += acc_dict[mr[1]][0]
        flag_text += mr[2].strftime(' (%b %Y start)')
        return [mr[0], True, flag_text]

class SCSt_TW_G_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         (nsc[5] == 'Transferred out' or
                          nsc[5] == 'Withdrew') and # Status
                         db[5] ==  'Graduated' and # Status
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_db_enr_update(mr, acc_dict, ed_from_nsc=True)

    def con_flag(self, mr, acc_dict):
        flag_text = 'Graduation not confirmed ('+mr[5]+' in NSC): '
        flag_text += acc_dict[mr[1]][0]
        flag_text += mr[2].strftime(' (%b %Y start)')
        return [mr[0], True, flag_text]

class SCSt_TW_A_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         (nsc[5] == 'Transferred out' or
                          nsc[5] == 'Withdrew') and # Status
                         db[5] ==  'Attending' and # Status
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        flag_text = 'New unreported left college: '
        flag_text += acc_dict[mr[1]][0]
        flag_text += mr[2].strftime(' (%b %Y start)')
        return [mr[0], True, flag_text]

class SCSt_TW_TW_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         (nsc[5] == 'Transferred out' or
                          nsc[5] == 'Withdrew') and # Status
                         (db[5] == 'Transferred out' or
                          db[5] == 'Withdrew') and
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        return deg_con_flag(mr, acc_dict)


class SCSt_A_Matr_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         nsc[5] == 'Attending' and # Status
                         (db[5] == 'Matriculating' or
                          db[5] == 'Did not matriculate') and
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        flag_text = 'NSC indicates actually enrolled (was ' +mr[16]+ '): '
        flag_text += acc_dict[mr[1]][0]
        flag_text += mr[2].strftime(' (%b %Y start)')
        return [mr[0], True, flag_text]


class SCSt_TW_Matr_Match(MatchCase):
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         (nsc[5] == 'Transferred out' or
                          nsc[5] == 'Withdrew') and # Status
                         (db[5] == 'Matriculating' or
                          db[5] == 'Did not matriculate') and
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict)

    def con_flag(self, mr, acc_dict):
        flag_text = 'NSC indicates actually enrolled then withdrew'
        
        flag_text += ' (was ' +mr[16]+ '): ' +acc_dict[mr[1]][0]
        flag_text += mr[2].strftime(' (%b %Y start)')
        return [mr[0], True, flag_text]


class SCStMatch(MatchCase): # Temporary case to catch S/C/St matches
    def comp(self, db, nsc):
        if not db[2]: #makes sure the database has a non-blank start date
            return False
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         fuzzy_start_match(db[2], nsc[2]) # Start Date
                       ) else False

class SC_StatusMatch(MatchCase):
    def comp(self, db, nsc):
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         db[5] == nsc[5]      # Status
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict, tricky_SD=True)

    def con_flag(self, mr, acc_dict):
        if mr[13]: # only flag if coordinator entered a start date
            flag_text = 'Date discrepancy ('
            flag_text += very_diff_start_date(mr)
            flag_text += '): ' +acc_dict[mr[1]][0]
            return [mr[0], True, flag_text]
        else:
            return None
 
class SC_anything_G_Match(MatchCase):
    def comp(self, db, nsc):
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         db[5] == 'Graduated'      # Status
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_db_enr_update(mr, acc_dict, ed_from_nsc=False,
                                                  tricky_SD=True)

    def con_flag(self, mr, acc_dict):
        flag_text = 'Graduation not confirmed (NSC has ' + mr[5] + ')'
        flag_text += ' and date discrepancy ('
        flag_text += very_diff_start_date(mr)
        flag_text += '): ' +acc_dict[mr[1]][0]
        return [mr[0], True, flag_text]
 
class SC_G_anything_Match(MatchCase):
    def comp(self, db, nsc):
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1] and # College
                         nsc[5] == 'Graduated'      # Status
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict, tricky_SD=True)

    def con_flag(self, mr, acc_dict):
        flag_text = 'New unreported graduation (was ' + mr[16] + ')'
        flag_text += ' and date discrepancy ('
        flag_text += very_diff_start_date(mr)
        flag_text += '): ' +acc_dict[mr[1]][0]
        return [mr[0], True, flag_text]

class SCMatch(MatchCase): # Catch-all case that must come last
    def comp(self, db, nsc):
        return True if ( db[0] == nsc[0] and # Student
                         db[1] == nsc[1]     # College
                       ) else False

    def enr_update(self, mr, acc_dict):
        return mostly_nsc_enr_update(mr, acc_dict, tricky_SD=True)

    def con_flag(self, mr, acc_dict):
        flag_text = 'Discrepancies ('
        flag_text += very_diff_start_date(mr, show_status=True)
        flag_text += '): ' +acc_dict[mr[1]][0]
        return [mr[0], True, flag_text]


class NotInDB_status(MatchCase):
    def __init__(self, name, status):
        self.name = name
        self.status = status
    def comp(self, db, nsc):
        return True if (db[0] is None and # 
                        nsc[5] == self.status
                        ) else False

    def new_enr(self, mr):
        return mr[0:10]
    def con_flag(self, mr, acc_dict):
        flag_text = 'NSC indicates previously unreported enrollment ('
        flag_text += self.status + '): '
        flag_text += acc_dict[mr[1]][0]
        flag_text += mr[2].strftime(' (%b %Y start)')
        return [mr[0], True, flag_text]

#-------------end of the MatchCase subclasses------------------------
def build_match_cases():
    '''The below should be an instance of every MatchCase subclass from above'''
    return [
            PerfectMatch('Perfect Match'),
            PerfectMatchFuzzyStart('Perfect Match w Start +/- 60 days off'),
            SCSt_GG_Match('Graduation match chg end dates'),
            SCSt_G_Other_Match('Unexpected graduation (had different status)'),
            SCSt_AA_Match('Attending match chg end dates'),
            SCSt_TW_TW_Match('T/W match chg end dates'),
            SCSt_A_Matr_Match('Attending but DB had DNM/Matriculating'),
            SCSt_A_G_Match('Graduation not confirmed (Attending)'),
            SCSt_A_TW_Match('Attending but DB had T/W'),
            SCSt_TW_G_Match('Graduation not confirmed (T/W)'),
            SCSt_TW_A_Match('Unreported left college (was Attending)'),
            SCSt_TW_Matr_Match('Trans/Withd but DB had DNM/Matriculating'),
            SCStMatch('(Error) Student-College-Start Match (unspecified)'),
            SC_StatusMatch('Status matches, but different start dates'),
            SC_anything_G_Match('Graduation not confirmed and diff start ds'),
            SC_G_anything_Match('Unexpected graduation w diff start ds'),
            SCMatch('Non-grad Student-College Match w diff start & status'),
            NotInDB_status('(NSC only) New attending enrollment', 'Attending'),
            NotInDB_status('(NSC only) New graduated enrollment', 'Graduated'),
            NotInDB_status('(NSC only) New transferred out enrollment',
                            'Transferred out'),
            NotInDB_status('(NSC only) New withdrew enrollment', 'Withdrew'),
            ]

#---------Cases for looking only at records with DB info not in NSC--------

class OnlyInDB_ignoreDegreeType(MatchCase):
    def __init__(self, name, degree_type):
        self.name = name
        self.degree_type = degree_type
    def __repr__(self):
        return self.name
    def comp(self, db):
        return (True if db[6] == self.degree_type else False)

class OnlyInDB_ignoreStatus(MatchCase):
    def __init__(self, name, status):
        self.name = name
        self.status = status
    def __repr__(self):
        return self.name
    def comp(self, db):
        return (True if db[5] == self.status else False)

class OnlyInDB(MatchCase):
    def __init__(self, name, status):
        self.name = name
        self.status = status
    def __repr__(self):
        return self.name
    def comp(self, db):
        return (True if db[5] == self.status else False)

    # matched record consists of first the NSC table then the DB
    def enr_update(self, mr, acc_dict):
        db_degree_type = mr[6]
        new_degree = db_only_degree_check(db_degree_type, acc_dict[mr[1]][1])
        if db_degree_type == new_degree:
            return None
        else:
            return [mr[10],mr[2],mr[3],mr[4],mr[5],new_degree,
                    mr[7],mr[8],mr[9]]

    def new_enr(self, mr):
        return None

    def con_flag(self, mr, acc_dict):
        flag_text = ''
        if (mr[5] == 'Attending' or
            mr[5] == 'Graduated' or
            mr[5] == 'Withdrew' or
            mr[5] == 'Transferred out'):
            flag_text = mr[5] + ' enrollment not confirmed by NSC'
        extra_correction = get_extra_correction(mr, acc_dict[mr[1]][1])
        if extra_correction:
            if flag_text: flag_text += ' and '
            flag_text += extra_correction
        if flag_text:
            flag_text += ': ' + acc_dict[mr[1]][0]
            flag_text += mr[2].strftime(' (%b %Y start)') if mr[2] else ''
            return [mr[0], True, flag_text]
        else:
            return None

def build_db_only_cases():
    return [
            OnlyInDB_ignoreDegreeType('(DB Only) Employment', 'Employment'),
            OnlyInDB_ignoreDegreeType('(DB Only) Trade/Vocational',
                                      'Trade/Vocational'),
            OnlyInDB_ignoreDegreeType('(DB Only) Certificate', 'Certificate'),
            OnlyInDB('(DB Only) Attending', 'Attending'),
            OnlyInDB('(DB Only) Withdrew', 'Withdrew'),
            OnlyInDB('(DB Only) Transferred out', 'Transferred out'),
            OnlyInDB('(DB Only) Graduated', 'Graduated'),
            OnlyInDB('(DB Only) Matriculating', 'Matriculating'),
            OnlyInDB('(DB Only) <empty status>', None),
            OnlyInDB_ignoreStatus('(DB Only) Did not matriculate',
                                  'Did not matriculate'),
           ]

def find_matches(db_enr, nsc_enr):
    ''' Main function for comparing the two tables (with columns as specified
    in get_enr_field_list above) and then returning two dictionaries of the
    matching cases. Dictionaries will have the table data index as the key
    with a two item list--the matching case as item 0 and the index of the
    second item (in the other table) as item 1'''
    db_enr_map = {}
    nsc_enr_map = {}
    match_table = []

    match_cases = build_match_cases() # a list of MatchCase subclasses
    db_only_cases = build_db_only_cases() # to be parsed separately

    #Now for every student in the NSC table, look for matches
    students = set(nsc_enr.get_column(e.Student__c))
    print('Processing %d students.' % len(students))
    student_count = 0
    for student in students:
        student_count += 1
        if student_count % 50 == 0: print('.',end='', flush=True)
        if student_count % 500 == 0: print(student_count, flush=True)

        # These are temporary lists that we'll pop rows off of
        # for every match (they'll be traversed backwards for this)
        nsc_student = list(nsc_enr.get_match_rows(e.Student__c, student))
        db_student = list(db_enr.get_match_rows(e.Student__c, student))
        db_blank = [None]*10 # for using to pass to MatchCases w/ db_null
        
        for case in match_cases:
            if not nsc_student: # we've matched all the nsc rows
                break; # move on to the next student
            else:
                for i in reversed(range(len(nsc_student))):
                    for j in reversed(range(len(db_student))): #maybe empty
                        if case.comp(db_student[j],nsc_student[i]):
                            nsc_index = nsc_student[i][-1]
                            db_index = db_student[j][-1]
                            db_enr_map[db_index] = [case, nsc_index]
                            nsc_enr_map[nsc_index] = [case, db_index]
                            match_row = [case]
                            match_row.extend(nsc_student.pop(i))
                            match_row.extend(db_student.pop(j))
                            match_table.append(match_row)
                            break;
                    else:
                        if case.comp(db_blank,nsc_student[i]):
                            nsc_index = nsc_student[i][-1]
                            nsc_enr_map[nsc_index] = [case, None]
                            match_row = [case]
                            match_row.extend(nsc_student.pop(i))
                            match_table.append(match_row)


    print(student_count, flush=True)

    # Now pass through all the remaining enrollments from the database
    # that didn't match
    db_only = [row for row in db_enr.rows() if row[-1] not in db_enr_map]
    print('Now passing through %d remaining db_only records.' % len(db_only))
    for case in db_only_cases:
        for i in reversed(range(len(db_only))):
            if case.comp(db_only[i]):
                db_index = db_only[i][-1]
                db_enr_map[db_index] = [case, None]
                match_row = [case]
                match_row.extend(db_only.pop(i))
                match_table.append(match_row)

    return (db_enr_map, nsc_enr_map, match_table)

