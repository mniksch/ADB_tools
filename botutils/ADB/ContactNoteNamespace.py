#!python3
'''
This module acts as a tool to reference Salesforce fields
in the Contact_Note__c object. Doing it this way allows other
instances of the alumni database to use these Python
tools, even if they have slightly different field names.
(In other words, this file can be edited to run later.)
'''
Id = 'Id'
IsDeleted = 'IsDeleted'
Name = 'Name'
CreatedDate = 'CreatedDate'
CreatedById = 'CreatedById'
LastModifiedDate = 'LastModifiedDate'
LastModifiedById = 'LastModifiedById'
SystemModstamp = 'SystemModstamp'
Contact__c = 'Contact__c'
Subject__c = 'Subject__c'
Comments__c = 'Comments__c'
Date_of_Contact__c = 'Date_of_Contact__c'
Comm_Status__c = 'Comm_Status__c'
Mode_of_Communication__c = 'Mode_of_Communication__c'
Discussion_Category__c = 'Discussion_Category__c'
Initiated_by_alum__c = 'Initiated_by_alum__c'
Action_Item_for_Followup__c = 'Action_Item_for_Followup__c'
Action_Item_Completed__c = 'Action_Item_Completed__c'
Action_Required__c = 'Action_Required__c'
Action_Item_Due_Date__c = 'Action_Item_Due_Date__c'
