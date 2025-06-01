# Simple Chrome Extension

A basic Chrome extension that demonstrates popup functionality and content script injection.

## Features

- **Change Page Background**: Randomly changes the background color of the current page
- **Highlight Links**: Highlights all links on the page with yellow background and red border
- **Show Page Info**: Displays information about the current page (title, number of links, images, paragraphs)
- **Reset Page**: Resets all modifications back to original state
- **Active Indicator**: Shows a small indicator when the extension loads on a page

## File Structure

```
chrome-extension/
├── manifest.json       # Extension configuration
├── popup.html         # Extension popup interface
├── popup.js          # Popup functionality
├── content.js        # Content script that runs on web pages
├── icons/            # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
└── README.md         # This file
```

## How to Install and Test

### 1. Enable Developer Mode
1. Open Chrome browser
2. Go to `chrome://extensions/`
3. Toggle "Developer mode" in the top-right corner

### 2. Load the Extension
1. Click "Load unpacked" button
2. Navigate to and select the `chrome-extension` folder
3. The extension should now appear in your extensions list

### 3. Test the Extension
1. Navigate to any website (e.g., https://google.com)
2. Click the extension icon in the Chrome toolbar (puzzle piece icon, then find "Simple Extension")
3. Try the different buttons in the popup:
   - **Change Page Background**: Changes the page background color
   - **Highlight Links**: Makes all links stand out
   - **Show Page Info**: Shows page statistics
   - **Reset Page**: Undoes all changes

### 4. Check Content Script
- When you visit any webpage, you should briefly see a "🚀 Extension Active" indicator in the top-right corner
- This demonstrates that the content script is working

## Development Tips

- **Reload Extension**: After making changes, go to `chrome://extensions/` and click the reload icon for your extension
- **Debug Popup**: Right-click the extension icon and select "Inspect popup" to open DevTools
- **Debug Content Script**: Use the regular page DevTools to debug content script issues
- **View Console**: Check the browser console for any error messages

## Permissions Explained

- `activeTab`: Allows the extension to access the current active tab
- `storage`: Allows the extension to store data (not currently used but included for future features)
- `scripting`: Allows the extension to inject scripts into web pages

## Next Steps

You can extend this extension by:
- Adding more interactive features
- Storing user preferences
- Adding background scripts
- Creating options pages
- Adding keyboard shortcuts
