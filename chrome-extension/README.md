# Chrome Extension - Modular Quiz & Content Tools

A powerful Chrome extension with AI-powered features for content analysis, quiz generation, and automated quiz answering.

## 🆕 New Features

### 🤖 Auto Answer Quiz
- **Button**: "🤖 Auto Answer Quiz" (orange button)
- **Functionality**: Automatically fills out specific quiz forms with predefined answers
- **Process**:
  1. Selects answer for question_229685402_answer_3544_label
  2. Selects answer for question_229685443_answer_1389  
  3. Clicks the submit button (submit_quiz_button)
  4. Logs each step in the browser console with detailed status messages

## 📁 Project Structure (Refactored)

The codebase has been split into modular files for better organization:

### Core Files
- **`popup.html`** - Main UI layout with all buttons
- **`popup.js`** - Main entry point and coordinator
- **`manifest.json`** - Extension configuration

### Modular JavaScript Files
- **`utils.js`** - Shared utilities and status functions
- **`text-extraction.js`** - Text extraction and viewing functionality
- **`page-manipulation.js`** - Page styling and manipulation tools
- **`ai-features.js`** - AI-powered content analysis features
- **`quiz-automation.js`** - NEW: Automated quiz answering functionality
- **`ai-service.js`** - AI service integration (Llama API)
- **`content.js`** - Content script for page interactions

## 🎯 Features Overview

### Text & Content Tools
- **Take My Quiz**: Extract all text content from current webpage
- **View Extracted Text**: Display previously extracted content in formatted window

### AI-Powered Features (Requires API Key)
- **🧠 Generate Quiz Questions**: Create interactive quizzes from page content
- **📝 Summarize Content**: Generate concise summaries of extracted text
- **🔑 Extract Key Points**: Identify and list main points from content
- **💬 Chat About Content**: Open chatbot for content-related questions
- **⚙️ Manage API Key**: Securely store and manage Llama API credentials

### Page Manipulation Tools
- **Change Page Background**: Apply random background colors
- **Highlight All Links**: Visually highlight all links on the page
- **Show Page Info**: Display page statistics (title, links, images, paragraphs)
- **Reset Page**: Restore page to original state

### Quiz Automation (NEW)
- **🤖 Auto Answer Quiz**: Automatically answer specific quiz questions and submit

## 🔧 Installation

1. Download or clone this extension folder
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the extension folder
5. The extension icon will appear in your browser toolbar

## 🚀 Usage

### Basic Features
1. Click the extension icon to open the popup
2. Use any button to interact with the current webpage
3. Status messages will appear at the bottom of the popup

### AI Features Setup
1. Click "⚙️ Manage API Key" 
2. Enter your Llama API key when prompted
3. The key will be stored securely in Chrome storage
4. Now you can use all AI-powered features

### Auto Quiz Feature
1. Navigate to a quiz page with the target questions
2. Click "🤖 Auto Answer Quiz"
3. Check the browser console (F12) for detailed logs
4. The extension will automatically:
   - Select the first answer option
   - Select the second answer option  
   - Submit the quiz
   - Log each action with status messages

## 📝 Console Logging

The Auto Answer Quiz feature provides detailed console logging:
- 🤖 Process start notification
- 📝 Step-by-step action descriptions  
- ✅ Success confirmations for each action
- ❌ Error messages if elements aren't found
- 🎉 Completion notification

Example console output:
```
🤖 Quiz Auto-Answer Started
📝 Step 1: Selecting first question answer...
✅ First answer selected successfully
📝 Step 2: Selecting second question answer...
✅ Second answer selected successfully  
📝 Step 3: Submitting quiz...
✅ Quiz submitted successfully!
🎉 Auto-answer process completed
```

## 🔒 Privacy & Security

- API keys are stored securely in Chrome's local storage
- No data is sent to external servers except for AI features (when explicitly used)
- All page interactions are performed locally
- Text extraction only processes content from the active tab

## 🛠️ Development

### File Structure Benefits
- **Modularity**: Each feature is in its own file
- **Maintainability**: Easy to find and modify specific functionality
- **Scalability**: Simple to add new features without cluttering
- **Debugging**: Easier to isolate and fix issues

### Adding New Features
1. Create a new JavaScript file for your feature
2. Add the file to `popup.html` script loading section
3. Add corresponding buttons to the HTML
4. Follow the existing class-based pattern for organization

## 🆕 Recent Updates

- ✅ Split monolithic popup.js into 6 modular files
- ✅ Added automated quiz answering functionality
- ✅ Enhanced console logging for better debugging
- ✅ Improved code organization and maintainability
- ✅ Added comprehensive documentation

## 🐛 Troubleshooting

**Auto Answer Quiz not working?**
- Check browser console for error messages
- Ensure you're on the correct quiz page
- Verify the quiz elements exist with the expected IDs

**AI features not working?**
- Verify your API key is correctly entered
- Check your internet connection
- Ensure the Llama API service is accessible

**Extension not loading?**
- Check for JavaScript errors in browser console
- Verify all files are present in the extension folder
- Try reloading the extension in chrome://extensions/
