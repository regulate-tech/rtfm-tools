# Setup Instructions for analyseDrive.gs script

1. Open a web browser window in the Google Drive account you want to analyse.
2. Create a new Google Apps Script by clicking the New button then 'More' at the bottom of the menu which gives you at list that includes 'Google Apps Script'
3. Paste the code from analyseDrive.gs into the script in your browser and save it.
4. Deploy your script by clicking on "Deploy" (blue button in the top right).
5. Select "New deployment" - Click "Select type" (the gear icon) - Choose "Web app"
6. Fill in the following - Description: "Drive Folder Analysis" (or whatever you prefer), Execute as: "Me", Who has access: "Only Myself"
7. Click "Deploy" and you'll be asked to authorize the app - click through the authorization screens which may agreeing to deploy an unsafe app.
8. After deployment: You'll get a URL that looks something like https://script.google.com/macros/s/.../exec
9. Copy this URL and open it in a new browser tab - the web interface will appear in the new tab, not in the script editor.
10. Open a Google Drive folder in another tab and copy the URL into the input box on your running script.
11. Choose one of the two types of analysis from the drop down and click the button to run this.
12. You should get a link to a Google Sheet at the end of the run and can click this for your results.

NB some Google Apps scripts can be run from the script file but this one has to be Deployed. And the permissions stuff can get weird if you are logged into multiple Google accounts. The safest option is to create the script and run the authorizations etc from a session that is only logged into the single Google account you want to analyse.