#!python3
'''Functions for determining college persistence.
Includes Class for storing all persistence information about a student that is
initialized by passing all the enrollment records for the student'''

from datetime import date, datetime


class Persistence():
    '''Class to store information about college persistence for a single
    student'''

    def _create_check_dates(self, hs_class, end_date):
        '''internal function to create a list of dates used to pinpoint
        whether a student was or wasn't enrolled each term'''
        self.check_dates = []
        cur_year = hs_class
        cur_date = date(cur_year, 10, 15)
        while cur_date <= end_date:
            self.check_dates.append(cur_date)
            if cur_date.month == 10:
                cur_year += 1
                cur_date = date(cur_year, 1, 20)
            elif cur_date.month == 1:
                cur_date = date(cur_year, 8, 31)
            else:
                cur_date = date(cur_year, 10, 15)

    def _set_sem(self, sem, status, college, grad):
        '''Helper function for initializing summary variables'''
        if grad == 'Both':
            self.status_semester[sem] = status
            self.college_semester[sem] = college
            self.grad_status_semester[sem] = status
            self.grad_college_semester[sem] = college
        if grad =='Status':
            self.status_semester[sem] = status
            self.college_semester[sem] = college
        else:
            self.grad_status_semester[sem] = status
            self.grad_college_semester[sem] = college



    def __init__(self, hs_class, aa_h, end_date, enrollments, account_d):
        '''hs_class is an integer year
           aa_h is a boolean on whether to treat student as AA or Hispanic
           end_date is a date after which we assume enrollments are invalid
           enrollments is a list of lists with the following columns:
               0: College (text that matches the key in account_d)
               1: Degree Type (text)
               2: Start Date (date or None)
               3: End Date (date or None)
               4: Status (text)
           account_d is a dictionary with key=college_id of lists with elements:
               0: Name (text)
               1: College Type (text)
               2: NCESid (text)
               3, 4: 6 yr grad (Overall and AA/H) % or None
               5, 6: 6 yr xfer (Overall and AA/H) % or None
               7: 1st year (overall) retention % or None
               '''
        self.grad_yr = hs_class
        self.is_aa_h = aa_h
        self._create_check_dates(hs_class, end_date)

        self.semesters = len(self.check_dates) # semesters is actually trime..

        #_enr lists will contain the college id for each enrollment
        self._ms_enr = [None]*self.semesters
        self._4yr_enr = [None]*self.semesters
        self._2yr_enr = [None]*self.semesters
        self._trade_enr = [None]*self.semesters
        self._enr_count = [0]*self.semesters

        for enr in enrollments:
            if is_real_enr(enr[4]):
                for sem in range(len(self.check_dates)):
                    if enr_on_check_date(enr[2], enr[3], self.check_dates[sem]):
                        self._enr_count[sem] += 1
                        if enr[1] == "Bachelor's":
                            self._4yr_enr[sem] = enr[0]
                        elif enr[1] == "Master's":
                            self._ms_enr[sem] = enr[0]
                        elif (enr[1] == "Associate's" or
                                 enr[1] == "Associate's or Certificate (TBD)"):
                            self._2yr_enr[sem] = enr[0]
                        elif (enr[1] == 'Certificate' or
                                 enr[1] == 'Trade/Vocational'):
                            self._trade_enr[sem] = enr[0]
                        #Add a double check degree type vs institution type?

        #_grad lists will contain the college id for each grad event
        #These will repeat to the final semester after the initial one
        self._4yr_grad = [None]*self.semesters
        self._2yr_grad = [None]*self.semesters
        self._trade_grad = [None]*self.semesters
        self._ms_grad = [None]*self.semesters
        for enr in enrollments:
            if enr[4] == 'Graduated' and enr[3]:
                for sem in range(len(self.check_dates)):
                    if self.check_dates[sem] >= enr[3]:
                        if enr[1] == "Bachelor's":
                            self._4yr_grad[sem] = enr[0]
                        elif enr[1] == "Master's":
                            self._ms_grad[sem] = enr[0]
                        elif (enr[1] == "Associate's" or
                              enr[1] == "Associate's or Certificate (TBD)"):
                            self._2yr_grad[sem] = enr[0]
                        elif (enr[1] == 'Certificate' or
                             enr[1] == 'Trade/Vocational'):
                            self._trade_grad[sem] = enr[0]

        # Summary fields: highest graduation + highest attainment
        # (these two will differ for AA/Trade grads enrolled in college)
        self.grad_status_semester = [None]*self.semesters
        self.grad_college_semester = [None]*self.semesters
        self.status_semester = [None]*self.semesters
        self.college_semester = [None]*self.semesters
        self.col_name_semester = [None]*self.semesters
        self.col_nces_semester = [None]*self.semesters
        self.col_type_semester = [None]*self.semesters
        self.grad_rate_semester = [None]*self.semesters #from college_semester
        self.ret_rate_semester = [None]*self.semesters
        self.simple_status = [None]*self.semesters
        self.simple_4yr_status = [None]*self.semesters
        self.persist_through_sem = -1
        self.persist_true = True
        self.persist_col = None
        self.earned_BA_in_sem = -1

        for sem in range(self.semesters):
            # These are in order of least to most important
            if self._trade_enr[sem]:
                self._set_sem(sem, "Trade/Vocational",self._trade_enr[sem],
                                                        'Status')
            if self._trade_grad[sem]:
                self._set_sem(sem, "Trade Degree",self._trade_grad[sem],'Both')
            if self._2yr_enr[sem]:
                self._set_sem(sem, "Associate's",self._2yr_enr[sem], 'Status')
            if self._2yr_grad[sem]:
                self._set_sem(sem, "2yr Degree",self._2yr_grad[sem], 'Both')
            if self._4yr_enr[sem]:
                self._set_sem(sem, "Bachelor's", self._4yr_enr[sem], 'Status')
            if self._4yr_grad[sem]:
                self._set_sem(sem, "4yr Degree",self._4yr_grad[sem], 'Both')
                if self.persist_true:
                    self.persist_true = False
                    if self.college_semester[sem] == self.persist_col:
                        self.persist_through_sem = sem
                if self.earned_BA_in_sem == -1:
                    self.earned_BA_in_sem = sem
            if self._ms_enr[sem]:
                self._set_sem(sem, "Master's", self._ms_enr[sem], 'Status')
            if self._ms_grad[sem]:
                self._set_sem(sem, 'Grad Degree', self._ms_grad[sem], 'Both')

            if (self.grad_status_semester[sem] == 'Grad Degree' or
                self.grad_status_semester[sem] == '4yr Degree' or
                self.status_semester[sem] == "Master's" or
                self.status_semester[sem] == "Bachelor's"):
                self.simple_4yr_status[sem] = 'In college/graduated'
                self.simple_status[sem] = 'In college/graduated'
            elif (self.grad_status_semester[sem] == '2yr Degree' or
                  self.status_semester[sem] == "Associate's"):
                self.simple_status[sem] = 'In college/graduated'
                self.simple_4yr_status[sem] = 'Not in college'
            else:
                self.simple_status[sem] = 'Not in college'
                self.simple_4yr_status[sem] = 'Not in college'

            # Final coding for the given semester
            self.set_grad_rates(sem, aa_h, account_d)

            # Code some number of semesters persisting variables
            if sem == 0:
                if self.college_semester[sem]:
                    self.persist_col = self.college_semester[sem]
                    self.persist_through_sem = sem
                else:
                    self.persist_true = False
            else:
                if self.persist_true:
                    if self.college_semester[sem] == self.persist_col:
                        self.persist_through_sem = sem
                    else:
                        self.persist_true = False

        self.has_grad_4yr = True if self._4yr_grad[-1] else False
        self.has_grad_2yr = True if self._2yr_grad[-1] else False
        self.has_trade = True if self._trade_grad[-1] else False
        self.persist_through_sem = self.fix_persist_fields(
                                        self.persist_through_sem)
        self.earned_BA_in_sem = self.fix_persist_fields(
                                        self.earned_BA_in_sem)


    def fix_persist_fields(self,sem):
        '''Helper function to convert the legend from date index to a semester
        cutoff; e.g. if sem=2 (8/31 year after HS graduation), adjusts to 2'''
        if sem == -1:
            return 0
        r_map = {0:1, 1:2, 2:2}
        return (sem//3)*2 + r_map[sem%3]

    def set_grad_rates(self, sem, aa_h, account_d):
        '''
        Sets the grad rate fields for a given semester (each lists) based
        on the college referenced in the list self.college_semester. All
        three lists should be referenced by sem:
            self.grad_rate_semester
            self.ret_rate_semester 
            self.col_nces_semester
            self.col_name_semester
            self.col_type_semester
        account_d is a dictionary with key=college_id of lists with elements:
           0: Name (text)
           1: College Type (text)--'4 yr', '2 yr', 'Trade'
           2: NCESid (text)
           3, 4: 6 yr grad (Overall and AA/H) % or None
           5, 6: 6 yr xfer (Overall and AA/H) % or None
           7: 1st year (overall) retention % or None
        '''
        if self.college_semester[sem]:
            if self.grad_college_semester[sem] == self.college_semester[sem]:
                # This bumps it up to 100% if we're stopped at "graduate"
                self.col_name_semester[sem] = None
                self.col_nces_semester[sem] = None
                self.col_type_semester[sem] = 'Grad'
                self.grad_rate_semester[sem]=1.0
                self.ret_rate_semester[sem]=1.0
                return
            col_data = account_d[self.college_semester[sem]]
        else:
            return # the fields are already initialized to None
        self.col_name_semester[sem] = col_data[0]
        self.col_nces_semester[sem] = col_data[2]
        self.col_type_semester[sem] = col_data[1]
        if col_data[1] == '4 yr' or col_data[1] == '2 yr':
            if not aa_h:
                self.grad_rate_semester[sem] = col_data[3]
                self.ret_rate_semester[sem] = col_data[7]
                if col_data[1] == '2 yr' and col_data[5]:
                    self.grad_rate_semester[sem] += col_data[5]/2.0
            else:
                self.grad_rate_semester[sem] = col_data[4]

                if col_data[3] and col_data[4] and col_data[7]:
                    gr_diff = col_data[3] - col_data[4] # aa/h disadvantage
                    if (gr_diff/2 < col_data[7]) and (gr_diff > 0):
                        self.ret_rate_semester[sem] = col_data[7] - gr_diff/2
                    else:
                        self.ret_rate_semester[sem] = col_data[7]

                else: # one of the two grad rates is not defined
                    self.ret_rate_semester[sem] = col_data[7]
                
                if col_data[1] == '2 yr' and col_data[6]:
                    self.grad_rate_semester[sem] += col_data[6]/2.0
                
        else:
            self.grad_rate_semester[sem] = 0.0
            self.ret_rate_semester[sem] = 0.0


    def give_simple_persistence(self, ba_only=False):
        '''Returns simple yes/no status for each semester of college (and
        ignores the August graduation check date'''
        ret = []
        for sem in range(self.semesters):
            if self.check_dates[sem].month != 8:
                if ba_only:
                    ret.append(self.simple_4yr_status[sem])
                else:
                    ret.append(self.simple_status[sem])
        return ret

    def give_detailed_persistence(self):
        '''Returns a simple list of persistence data'''
        ret = []
        for sem in range(self.semesters):
            ret.extend([self.check_dates[sem],
                        self.status_semester[sem],
                        self.college_semester[sem],
                        self.grad_status_semester[sem],
                        self.grad_college_semester[sem]])
        return ret

    def __repr__(self):
        race_text = 'is AA/H' if self.is_aa_h else 'is not AA/H'
        return 'Alum from ' + str(self.grad_yr) + ' ' + race_text +' '+ str(
                len(self.check_dates)) +' semesters possible ' + str(
                        sum(self._enr_count)) + ' total enrolled'

def is_real_enr(status):
    '''Returns a boolean on whether it's a status code we care about'''
    return ( status == 'Attending' or
             status == 'Graduated' or
             status == 'Withdrew' or
             status == 'Transferred out')

def enr_on_check_date(start, end, check):
    if not start: return False
    if start <= check:
        if end: # a terminated enrollment
            if check <= end:
                return True
            else: # ending before the check date
                return False
        else: # hasn't ended yet (so covers the check date)
            return True
    else: # happened after the check date
        return False

def is_AAH(race_eth):
    '''Returns a boolean on whether the student should be counted as African
    American or Hispanic'''
    return (race_eth == 'African American' or
            race_eth == 'Hispanic' or
            race_eth == 'Multicultural' or
            race_eth == 'Multi-Cultural' or
            race_eth == 'Native American' or
            race_eth == 'Pacific Islander')

def create_classes(con, acc, enr, end_date):
    '''Returns a dictionary of Persistence records--one per student'''
    per_stats = {}
    account_d = acc.create_dict_list('Id',
                                     ['Name', 'College Type','NCESid',
                                      '6 yr grad', '6 yr grad AA/H',
                                      '6 yr transfer', '6 yr transfer AA/H',
                                      '1st yr retention'])
    for student in con:
        student_enr = [i[2:] for i in enr if i[1] == student[0]]
        student_AAH = is_AAH(student[3])
        per_stats[student[0]] = Persistence(int(student[9]), # HS Class
                                            student_AAH,
                                            end_date,
                                            student_enr,
                                            account_d)

    return per_stats
