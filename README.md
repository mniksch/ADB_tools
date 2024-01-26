# ADB Tools
Various Python tools for working with a Salesforce alumni database

## Requirements
To use, install the packages in requirements.txt

## Working with Salesforce
In order to export and update data (only FixCurrentlyEnrolledAt.py updates directly), you
will need to store your Salesforce credentials locally in the botutils/ADB/ssfLogin.py file:

```python
user = 'yourusername@x.org'
password = 'yourpassword'
token = 'yourtoken'
```

The token can be requested from Salesforce under user profile in the "My Personal Information" section
and will be reset after every password change.

## BackupAll.py

This file is designed to save local archives of main Salesforce tables as csv files.
Run this first to check the setup of your ssfLogin.py file and to see if there are
any other issues with your setup.

## import_nsc.py

Used for processing an NSC detail csv file to prepare for import into an empty Salesforce instance.

## merge_nsc.py

Used as a second step after import_nsc.py to compare the results of the NSC data to what was
already in the database.

## sf_reports.py

Used to generate a Spreadsheet with multiple tabs of analysis about the college persistence of students
in the Salesforce database.

## FixCurrentlyEnrolledAt.py

Depending on the setup of your Salesforce system, there are some patterns of Enrollment update that
will break a "Currently Enrolled At" field. This file loops through all students in the database
and updates this field based on all of their current "Attending" enrollments.

## Caveat Emptor

Some of this code is 9+ years old and hasn't been rigorously tested outside the setup for Noble.
Use at your own risk.
