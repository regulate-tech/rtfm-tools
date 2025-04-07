/** analyseDrive.gs - a Google Apps script to help with moving files between Drive accounts */

/**
 * @OnlyCurrentDoc
 * @NotOnlyCurrentDoc
 * Requires the following scopes:
 * - https://www.googleapis.com/auth/drive
 * - https://www.googleapis.com/auth/documents
 * - https://www.googleapis.com/auth/spreadsheets
 */


function doGet() {
  var html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
    <head>
    <base target="_top">
    <style>
    body { 
      font-family: Arial, sans-serif; 
      margin: 20px; 
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
    }
    .input-field { 
      width: 100%; 
      padding: 8px; 
      margin: 10px 0; 
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    .button { 
      background-color: #4CAF50; 
      color: white; 
      padding: 10px 20px; 
      border: none; 
      border-radius: 4px; 
      cursor: pointer; 
    }
    .button:hover { 
      background-color: #45a049; 
    }
    #status {
      margin-top: 20px;
      padding: 10px;
      display: none;
    }
    </style>
    </head>
    <body>
    <h3>Google Drive Folder Analysis</h3>
    <p>Please paste the Google Drive folder URL or folder ID:</p>
    <input type="text" id="folderInput" class="input-field" 
      placeholder="Paste folder URL or ID here...">
    <br>
    <select id="analysisType" class="input-field">
      <option value="storage">Storage Analysis</option>
      <option value="links">Drive Links Analysis</option>
    </select>
    <br>
    <button class="button" onclick="submitFolder()">Analyze Folder</button>
    <div id="status"></div>
    
    <script>
    function submitFolder() {
      var input = document.getElementById('folderInput').value;
      var analysisType = document.getElementById('analysisType').value;
      var statusDiv = document.getElementById('status');
      
      statusDiv.style.display = 'block';
      statusDiv.style.backgroundColor = '#fff3cd';
      statusDiv.innerHTML = 'Analysis in progress... Please wait.';
      
      if (analysisType === 'storage') {
        google.script.run
          .withSuccessHandler(function(message) {
            statusDiv.style.backgroundColor = '#d4edda';
            statusDiv.innerHTML = message;
          })
          .withFailureHandler(function(error) {
            statusDiv.style.backgroundColor = '#f8d7da';
            statusDiv.innerHTML = 'Error: ' + error.message;
          })
          .analyzeFolderFromInput(input);
      } else {
        google.script.run
          .withSuccessHandler(function(message) {
            statusDiv.style.backgroundColor = '#d4edda';
            statusDiv.innerHTML = message;
          })
          .withFailureHandler(function(error) {
            statusDiv.style.backgroundColor = '#f8d7da';
            statusDiv.innerHTML = 'Error: ' + error.message;
          })
          .analyzeDriveLinks(input);
      }
    }
    </script>
    </body>
    </html>
  `)
  .setTitle('Google Drive Folder Analysis')
  .setFaviconUrl('https://www.google.com/images/about/favicon.ico');
  
  return html;
}

function analyzeFolderFromInput(input) {
  try {
    var folderId = extractFolderId(input);
    if (!folderId) {
      throw new Error('Invalid folder URL or ID provided.');
    }
    
    // Create a new spreadsheet with timestamp
    var timestamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd_HH:mm");
    var ss = SpreadsheetApp.create("Drive Storage Analysis " + timestamp);
    var sheet = ss.getActiveSheet();
    
    var parentFolder = DriveApp.getFolderById(folderId);
    
    // Set up headers
    sheet.getRange("A1:E1").setValues([["Folder Path", "Number of Files", "Size (MB)", "Last Modified", "Folder Link"]]);
    sheet.getRange("A1:E1").setFontWeight("bold");
    sheet.setFrozenRows(1);
    
    // Start analyzing
    var rowData = [];
    analyzeFolder(parentFolder, "", rowData);
    
    // Write all data at once
    if (rowData.length > 0) {
      sheet.getRange(2, 1, rowData.length, 5).setValues(rowData);
    }
    
    // Auto-resize columns
    sheet.autoResizeColumns(1, 5);
    
    // Add totals at the bottom
    var lastRow = sheet.getLastRow();
    sheet.getRange(lastRow + 2, 1, 1, 5).setValues([
      ["TOTAL", 
       "=SUM(B2:B" + lastRow + ")", 
       "=SUM(C2:C" + lastRow + ")",
       "",
       ""
      ]
    ]);
    sheet.getRange(lastRow + 2, 1, 1, 5).setFontWeight("bold");
    
    // Format the spreadsheet
    formatSpreadsheet(sheet);
    
    return "Analysis complete! New spreadsheet has been created: <a href='" + ss.getUrl() + "' target='_blank'>Open Spreadsheet</a>";
    
  } catch (e) {
    throw new Error('Could not access the specified folder. Please check the URL/ID and your permissions. Error: ' + e.toString());
  }
}

function extractFolderId(input) {
  if (!input) return null;
  
  // Check if input is a URL
  if (input.includes('folders/')) {
    var matches = input.match(/folders\/([a-zA-Z0-9-_]+)/);
    return matches ? matches[1] : null;
  }
  // If not a URL, assume it's a direct ID
  return input;
}

function analyzeFolder(folder, path, rowData) {
  var folderName = path + "/" + folder.getName();
  var files = folder.getFiles();
  var subfolders = folder.getFolders();
  var totalSize = 0;
  var fileCount = 0;
  
  // Process files in the current folder
  while (files.hasNext()) {
    var file = files.next();
    totalSize += file.getSize();
    fileCount++;
  }
  
  // Add current folder data to rowData array
  rowData.push([
    folderName,
    fileCount,
    (totalSize / (1024 * 1024)).toFixed(2), // Convert bytes to MB
    Utilities.formatDate(folder.getLastUpdated(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm"),
    folder.getUrl()
  ]);
  
  // Process subfolders recursively
  while (subfolders.hasNext()) {
    var subfolder = subfolders.next();
    analyzeFolder(subfolder, folderName, rowData);
  }
}

function formatSpreadsheet(sheet) {
  // Get the data range
  var dataRange = sheet.getDataRange();
  
  // Apply alternating row colors
  var numRows = dataRange.getNumRows();
  for (var i = 2; i <= numRows; i++) {
    if (i % 2 === 0) {
      sheet.getRange(i, 1, 1, 5).setBackground("#f3f3f3");
    }
  }
  
  // Format the size column to 2 decimal places
  sheet.getRange(2, 3, numRows - 1, 1).setNumberFormat("#,##0.00");
  
  // Make folder links clickable
  sheet.getRange(2, 5, numRows - 1, 1).setShowHyperlink(true);
  
  // Add borders
  dataRange.setBorder(true, true, true, true, true, true);
  
  // Center align number columns
  sheet.getRange(1, 2, numRows, 2).setHorizontalAlignment("center");
  
  // Set column widths
  sheet.setColumnWidth(1, 300); // Folder Path
  sheet.setColumnWidth(2, 100); // Number of Files
  sheet.setColumnWidth(3, 100); // Size
  sheet.setColumnWidth(4, 150); // Last Modified
  sheet.setColumnWidth(5, 250); // Folder Link
}

function analyzeDriveLinks(input) {
  try {
    var folderId = extractFolderId(input);
    if (!folderId) {
      throw new Error('Invalid folder URL or ID provided.');
    }
    
    // Create a new spreadsheet with timestamp
    var timestamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd_HH:mm");
    var ss = SpreadsheetApp.create("Drive Links Analysis " + timestamp);
    var sheet = ss.getActiveSheet();
    
    // Set up headers
    sheet.getRange("A1:E1").setValues([["Document Name", "Document Path", "Drive Links Found", "Last Modified", "Document URL"]]);
    sheet.getRange("A1:E1").setFontWeight("bold");
    sheet.setFrozenRows(1);
    
    var parentFolder = DriveApp.getFolderById(folderId);
    var rowData = [];
    analyzeFolderForLinks(parentFolder, "", rowData);
    
    // Write all data at once
    if (rowData.length > 0) {
      sheet.getRange(2, 1, rowData.length, 5).setValues(rowData);
      // Format the spreadsheet
      formatLinkSpreadsheet(sheet);
    } else {
      // Add a message when no documents with links are found
      sheet.getRange(2, 1, 1, 5).setValues([["No Google Docs with Drive links were found in this folder structure.", "", "", "", ""]]);
      sheet.getRange(2, 1, 1, 5).merge();
      sheet.getRange(2, 1).setHorizontalAlignment("center");
      
      // Set basic formatting even for empty results
      sheet.setColumnWidth(1, 200);
      sheet.setColumnWidth(2, 250);
      sheet.setColumnWidth(3, 300);
      sheet.setColumnWidth(4, 150);
      sheet.setColumnWidth(5, 250);
      
      // Add borders to the header and message
      sheet.getRange(1, 1, 2, 5).setBorder(true, true, true, true, true, true);
    }
    
    return "Analysis complete! New spreadsheet has been created: <a href='" + ss.getUrl() + "' target='_blank'>Open Spreadsheet</a>";
    
  } catch (e) {
    throw new Error('Could not analyze the specified folder. Error: ' + e.toString());
  }
}

function formatLinkSpreadsheet(sheet) {
  // Get the data range
  var dataRange = sheet.getDataRange();
  var numRows = dataRange.getNumRows();
  
  // Only apply formatting if we have data rows
  if (numRows > 1) {  // More than just the header row
    // Apply alternating row colors
    for (var i = 2; i <= numRows; i++) {
      if (i % 2 === 0) {
        sheet.getRange(i, 1, 1, 5).setBackground("#f3f3f3");
      }
    }
    
    // Make document links clickable
    sheet.getRange(2, 5, numRows - 1, 1).setShowHyperlink(true);
    
    // Add borders
    dataRange.setBorder(true, true, true, true, true, true);
    
    // Set column widths
    sheet.setColumnWidth(1, 200); // Document Name
    sheet.setColumnWidth(2, 250); // Document Path
    sheet.setColumnWidth(3, 300); // Drive Links Found
    sheet.setColumnWidth(4, 150); // Last Modified
    sheet.setColumnWidth(5, 250); // Document URL
    
    // Set wrap strategy for the links column
    sheet.getRange(2, 3, numRows - 1, 1).setWrapStrategy(SpreadsheetApp.WrapStrategy.WRAP);
  }
}

function analyzeFolderForLinks(folder, path, rowData) {
  var folderPath = path + "/" + folder.getName();
  var files = folder.getFilesByType(MimeType.GOOGLE_DOCS);
  var subfolders = folder.getFolders();
  
  // Process Google Docs in the current folder
  while (files.hasNext()) {
    var file = files.next();
    try {
      var doc = DocumentApp.openById(file.getId());
      var body = doc.getBody();
      var text = body.getText();
      
      // Find Drive, Docs, and Sheets links using regular expressions
      var driveLinks = text.match(/https:\/\/(drive|docs|sheets)\.google\.com\/[^\s\)<>\"\']+/g) || [];
            
      // Only add to results if links are found
      if (driveLinks.length > 0) {
        rowData.push([
          file.getName(),
          folderPath,
          driveLinks.join("\n"),
          Utilities.formatDate(file.getLastUpdated(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm"),
          file.getUrl()
        ]);
      }
    } catch (e) {
      // If we can't open the document, add it to results with an error message
      rowData.push([
        file.getName(),
        folderPath,
        "Error accessing document: " + e.toString(),
        Utilities.formatDate(file.getLastUpdated(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm"),
        file.getUrl()
      ]);
    }
  }
  
  // Process subfolders recursively
  while (subfolders.hasNext()) {
    var subfolder = subfolders.next();
    analyzeFolderForLinks(subfolder, folderPath, rowData);
  }
}
