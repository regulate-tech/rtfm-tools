# Readme for Google Drive Analysis Tool

A descriptive guide to the scripts for analysing files on Google Drive. For technical requirements please see the SETUP.md file.

## WHO

You store files on Google Drive using several different personal and/or Workspace accounts.

## WHAT

You want to move files between your Google Drive accounts and/or local storage and need to information about them to make sure they keep working in any new location.

## WHY

You have built up a library of files in one Google Drive account but now need to move them to another account as your work evolves and for resilience. You may also want to have a local copy of the files that will work properly.

## WHERE

You will run the Google App Scripts online from within your Google Drive account. 

## WHEN

This would normally be run as a one-off exercise as you set up a new Google Drive account and want to bring files in from another Drive. You may also want to run it periodically if you have set this up for resilience purposes to create backups on another Drive or locally. 

## HOW

1. you create Google Apps Script that is able to look at your files in Drive and produce reports for you. 
2. the script asks you for a link to a jumping off folder in Drive and will work recursively through any sub-folders under the start folder. 
3. it offers options for calculating the numbers of files and their sizes and for checking for links to other Google files in documents. 
4. it writes its analyses out to Google Sheets files within your Google Drive. 

## WHAT NEXT

Google Docs, Sheets and Slides should work normally when moved between Google Drive accounts but will not be usable locally.  We can develop scripts to store local copies of these files in usable formats.

We have looked at links to other files that may need updating after a move. We should explore other things that may break and implement a testing regime for the moved files. 
