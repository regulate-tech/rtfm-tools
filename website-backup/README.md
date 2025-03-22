# Readme for GitHub Pages Backup Tool

A descriptive guide to the website backup script. For technical requirements please see the SETUP.md file.

## WHO

You are running one or more websites on GitHub Pages. You are maintaining a repository for each website.

## WHAT

You want to have two copies of each website off GitHub - a local copy on your computer and one on an online cloud storage service.

## WHY

You are thinking about resilience and making sure you can get up and running again if anything happens to the GitHub service. The local copy will allow you to run tests on the backups and the cloud storage backup is an option to serve the sites publicly.

## WHERE

You will run the script locally on your device. It will work on common personal computers - Windows/Mac/Chromebook/Linux - if these have been properly configured.

## WHEN

You can set the script up to run periodically, for example once a day, so that you always have recent copies of your websites. There are different ways to do this depending on your operating system and scheduling tools available.

## HOW

1. you create a list of the GitHub repositories and associated domains in a CSV file.
2. the script checks that it has access to GitHub and AWS and exits with a message if it does not.
3. it reads the CSV file and runs routines for each of the repository-domain pairs.
4. it uses GitHub commands to pull a local copy of the repository.
5. it uses another GitHub command to pull something called an ‘artifact’ which is the full set of GitHub Pages content.
6. it extracts files from the artifact so now it has both the repository and a runnable version of the website locally.
7. it creates a new AWS S3 storage bucket if one does not exist already for that domain.
8. it uploads both the GitHub repository and the runnable version of the website to the S3 storage bucket.
9. it iterates through the list in the CSV file until it has made copies of all the websites and then completes its run.

## WHAT NEXT

You will want to run tests against the local copies of the websites to make sure everything is as you expect it. We can develop some scripts for this.

If you want to serve the websites from the backup copies on S3 you will need to reconfigure DNS so that it points to these. We can prepare documentation and scripts for this reflecting common ways to administer DNS configurations.

You can run a failover exercise where you switch to the S3 copies and then switch back to GitHub and see how long this takes and how it affects the availability of your websites. We can prepare a model playbook for doing this.
