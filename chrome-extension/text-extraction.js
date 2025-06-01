// Text extraction functionality
class TextExtraction {
  constructor() {
    this.setupEventListeners();
  }

  setupEventListeners() {
    document.getElementById('takeQuiz').addEventListener('click', this.extractText.bind(this));
    document.getElementById('viewExtractedText').addEventListener('click', this.viewExtractedText.bind(this));
  }

  // Take My Quiz - Extract all text from the webpage
  async extractText() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          // Get all text content from the page
          const allText = document.body.innerText || document.body.textContent;
          
          // Clean up the text (remove extra whitespace, empty lines)
          const cleanText = allText
            .split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .join('\n');
          
          return {
            title: document.title,
            url: window.location.href,
            textContent: cleanText,
            wordCount: cleanText.split(/\s+/).length
          };
        }
      });
      
      const pageData = results[0].result;
      
      // Store the extracted data for later use
      await chrome.storage.local.set({
        quizData: pageData,
        timestamp: Date.now()
      });
      
      console.log('Extracted page data:', pageData);
      showStatus(`Text extracted! ${pageData.wordCount} words found.`, 'success');
      
      // Optional: Show a preview of the extracted text
      const preview = pageData.textContent.substring(0, 200) + '...';
      console.log('Text preview:', preview);
      
    } catch (error) {
      console.error('Error extracting text:', error);
      showStatus('Error extracting page text', 'error');
    }
  }

  // View Extracted Text - Display previously captured text
  async viewExtractedText() {
    try {
      const result = await chrome.storage.local.get(['quizData']);
      
      if (result.quizData) {
        const data = result.quizData;
        
        // Create a simple popup window to show the text
        const textWindow = window.open('', 'ExtractedText', 'width=600,height=400,scrollbars=yes');
        textWindow.document.write(`
          <html>
            <head>
              <title>Extracted Text</title>
              <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .header { border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }
                .content { white-space: pre-wrap; line-height: 1.6; }
                .stats { background: #f0f0f0; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
              </style>
            </head>
            <body>
              <div class="header">
                <h2>Extracted Text</h2>
                <div class="stats">
                  <strong>Title:</strong> ${data.title}<br>
                  <strong>URL:</strong> ${data.url}<br>
                  <strong>Word Count:</strong> ${data.wordCount} words
                </div>
              </div>
              <div class="content">${data.textContent}</div>
            </body>
          </html>
        `);
        textWindow.document.close();
        
        showStatus('Extracted text displayed in new window', 'success');
      } else {
        showStatus('No extracted text found. Click "Take My Quiz" first!', 'error');
      }
    } catch (error) {
      console.error('Error retrieving extracted text:', error);
      showStatus('Error retrieving extracted text', 'error');
    }
  }

  // Get extracted text from storage (utility function for other modules)
  static async getExtractedText() {
    const result = await chrome.storage.local.get(['quizData']);
    if (!result.quizData) {
      throw new Error('No extracted text found. Please click "Take My Quiz" first!');
    }
    return result.quizData.textContent;
  }
}

// Initialize text extraction when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new TextExtraction();
});
