# Readme for Google Data Pull Tool

A descriptive guide to the scripts for pulling data from your Google account and processing this locally. For technical requirements please see the SETUP.md file.

## WHO

You use a Google account (personal or Workspace) for managing your contacts and calendar.

## WHAT

You want to pull the data from your Google account to feed into other processes running locally or on other non-Google servers.

## WHY

You are thinking about resilience so would anyway like to have a machine-readable copy of this important data. You want to develop other tools to help you manage your work and time using the data from your Google account. 

## WHERE

You will run the script locally on your device. It will work on common personal computers - Windows/Mac/Chromebook/Linux - if these have been properly configured.

## WHEN

You can run the script manually when you have a use for your contacts and calendar data. You might set the script up to run periodically by calling it from other work management tools.

## HOW

1. you set up your Google account to allow access to the relevant APIs and provide access keys for this.
2. the script checks that it has access to your Google account and calls routine to log you in if necessary.
3. it reads the calendar and/or contacts data by calling the API.
4. it writes the pulled data to JSON files on your local machine.

## WHAT NEXT

You will want to run tests against the local JSON files to make sure everything is as you expect it. We can develop some scripts for this.

You can add more options to the workflow to specify the ranges of data to be downloaded and processes for incremental updates.

You can develop tools that use the downloaded data to help your work management. You can see an example script to use audio recording to add notes to your contacts - contact-audio-notes.py.
