#!python3
'''
This module acts as a tool to reference Salesforce fields
in the Relationship__c object. Doing it this way allows other
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
Alum__c = 'Alum__c'
Related_to__c = 'Related_to__c'
Type_of_relationship__c = 'Type_of_relationship__c'
