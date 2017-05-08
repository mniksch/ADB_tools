#!python3
'''
This module acts as a tool to reference Salesforce fields
in the Contact object. Doing it this way allows other
instances of the alumni database to use these Python
tools, even if they have slightly different field names.
(In other words, this file can be edited to run later.)
'''
Id = 'Id'
IsDeleted = 'IsDeleted'
MasterRecordId = 'MasterRecordId'
AccountId = 'AccountId'
LastName = 'LastName'
FirstName = 'FirstName'
Salutation = 'Salutation'
Name = 'Name'
RecordTypeId = 'RecordTypeId'
OtherStreet = 'OtherStreet'
OtherCity = 'OtherCity'
OtherState = 'OtherState'
OtherPostalCode = 'OtherPostalCode'
OtherCountry = 'OtherCountry'
OtherLatitude = 'OtherLatitude'
OtherLongitude = 'OtherLongitude'
MailingStreet = 'MailingStreet'
MailingCity = 'MailingCity'
MailingState = 'MailingState'
MailingPostalCode = 'MailingPostalCode'
MailingCountry = 'MailingCountry'
MailingLatitude = 'MailingLatitude'
MailingLongitude = 'MailingLongitude'
Phone = 'Phone'
Fax = 'Fax'
MobilePhone = 'MobilePhone'
HomePhone = 'HomePhone'
OtherPhone = 'OtherPhone'
AssistantPhone = 'AssistantPhone'
ReportsToId = 'ReportsToId'
Email = 'Email'
Title = 'Title'
Department = 'Department'
AssistantName = 'AssistantName'
LeadSource = 'LeadSource'
Birthdate = 'Birthdate'
Description = 'Description'
OwnerId = 'OwnerId'
CreatedDate = 'CreatedDate'
CreatedById = 'CreatedById'
LastModifiedDate = 'LastModifiedDate'
LastModifiedById = 'LastModifiedById'
SystemModstamp = 'SystemModstamp'
LastActivityDate = 'LastActivityDate'
LastCURequestDate = 'LastCURequestDate'
LastCUUpdateDate = 'LastCUUpdateDate'
LastViewedDate = 'LastViewedDate'
LastReferencedDate = 'LastReferencedDate'
EmailBouncedReason = 'EmailBouncedReason'
EmailBouncedDate = 'EmailBouncedDate'
IsEmailBounced = 'IsEmailBounced'
Jigsaw = 'Jigsaw'
JigsawContactId = 'JigsawContactId'
College_Credits_Accumulated__c = 'College_Credits_Accumulated__c'
Actual_College_Graduation_Date__c = 'Actual_College_Graduation_Date__c'
Associate_s_Degree__c = 'Associate_s_Degree__c'
Bachelor_s_Degree__c = 'Bachelor_s_Degree__c'
College_Graduated_From__c = 'College_Graduated_From__c'
College_Status__c = 'College_Status__c'
Cumulative_College_GPA__c = 'Cumulative_College_GPA__c'
Currently_Enrolled_At__c = 'Currently_Enrolled_At__c'
EFC_from_FAFSA__c = 'EFC_from_FAFSA__c'
Ethnicity__c = 'Ethnicity__c'
Expected_Graduation_Date__c = 'Expected_Graduation_Date__c'
First_Generation_College_Student__c = 'First_Generation_College_Student__c'
Low_Income__c = 'Low_Income__c'
#Low_Income__c = 'Lunch_Status__c'
Full_Name__c = 'Full_Name__c'
Gender__c = 'Gender__c'
Highest_ACT_Score__c = 'Highest_ACT_Score__c'
HS_Final_GPA__c = 'HS_Final_GPA__c'
#HS_Final_GPA__c = 'HS_Unweighted_GPA__c'
HS_Class__c = 'HS_Class__c'
Latest_FAFSA_Date__c = 'Latest_FAFSA_Date__c'
Latest_Transcript__c = 'Latest_Transcript__c'
Marital_Status__c = 'Marital_Status__c'
Not_pursuing_higher_ed_at_this_time__c = 'Not_pursuing_higher_ed_at_this_time__c'
Pell_Eligible__c = 'Pell_Eligible__c'
Secondary_email__c = 'Secondary_email__c'
Network_Student_ID__c = 'Network_Student_ID__c'
Special_Education__c = 'Special_Education__c'
Picture_ID__c = 'Picture_ID__c'
Picture__c = 'Picture__c'
High_School__c = 'High_School__c'
Last_Successful_Contact__c = 'Last_Successful_Contact__c'
Last_Outreach__c = 'Last_Outreach__c'
Persistence_Status__c = 'Persistence_Status__c'
Current_Status__c = 'Current_Status__c'
AdminFlag__c = 'AdminFlag__c'
Campus_Email__c = 'Campus_Email__c'
Facebook_ID__c = 'Facebook_ID__c'
Email_to_Text__c = 'Email_to_Text__c'
Twitter_Handle__c = 'Twitter_Handle__c'
rollupAttendingBachelors__c = 'rollupAttendingBachelors__c'
rollupAttendingAssociates__c = 'rollupAttendingAssociates__c'
rollupMatriculating__c = 'rollupMatriculating__c'
rollupGraduated4__c = 'rollupGraduated4__c'
rollupGraduated2__c = 'rollupGraduated2__c'
rollupGraduatedTrade__c = 'rollupGraduatedTrade__c'
rollupAttended4__c = 'rollupAttended4__c'
rollupAttended2__c = 'rollupAttended2__c'
rollupAttendingTrade__c = 'rollupAttendingTrade__c'
College_Attainment__c = 'College_Attainment__c'
Needs_NSC_Review__c = 'Needs_NSC_Review__c'
NSC_Review_Reason__c = 'NSC_Review_Reason__c'
Final_PS_Address__c = 'Final_PS_Address__c'
Final_PS_Home_Phone__c = 'Final_PS_Home_Phone__c'
Mother_cell__c = 'Mother_cell__c'
Father_cell__c = 'Father_cell__c'
Parent_1_Name__c = 'Parent_1_Name__c'
Parent_2_Name__c = 'Parent_2_Name__c'
Parent_1_email__c = 'Parent_1_email__c'
Parent_2_email__c = 'Parent_2_email__c'
Planned_follow__c = 'Planned_follow__c'
High_School_Advisor__c = 'High_School_Advisor__c'
Direness_Coding__c = 'Direness_Coding__c'
ROI_Return_on_Investment_Coding__c = 'ROI_Return_on_Investment_Coding__c'
Days_overdue_for_follow_up__c = 'Days_overdue_for_follow_up__c'
Overdue_for_follow_up__c = 'Overdue_for_follow_up__c'
Risk_Variable__c = 'Risk_Variable__c'
