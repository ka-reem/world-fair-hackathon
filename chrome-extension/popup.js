// Get current tab information when popup loads
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    document.getElementById('pageUrl').textContent = tab.url;
  } catch (error) {
    document.getElementById('pageUrl').textContent = 'Unable to get page URL';
  }
});

// Take My Quiz - Extract all text from the webpage
document.getElementById('takeQuiz').addEventListener('click', async () => {
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
});

// Change background color of the current page
document.getElementById('changeBackground').addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => {
        const colors = ['#ffebee', '#e8f5e8', '#e3f2fd', '#fff3e0', '#f3e5f5'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        document.body.style.backgroundColor = randomColor;
      }
    });
    
    showStatus('Background color changed!', 'success');
  } catch (error) {
    showStatus('Error changing background', 'error');
  }
});

// Highlight all links on the page
document.getElementById('highlightLinks').addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => {
        const links = document.querySelectorAll('a');
        links.forEach(link => {
          link.style.backgroundColor = '#ffff00';
          link.style.padding = '2px';
          link.style.border = '2px solid #ff0000';
        });
      }
    });
    
    showStatus('Links highlighted!', 'success');
  } catch (error) {
    showStatus('Error highlighting links', 'error');
  }
});

// Show page information
document.getElementById('showPageInfo').addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => {
        return {
          title: document.title,
          links: document.querySelectorAll('a').length,
          images: document.querySelectorAll('img').length,
          paragraphs: document.querySelectorAll('p').length
        };
      }
    });
    
    const pageInfo = results[0].result;
    const infoText = `
      Title: ${pageInfo.title}
      Links: ${pageInfo.links}
      Images: ${pageInfo.images}
      Paragraphs: ${pageInfo.paragraphs}
    `;
    
    alert(infoText);
    showStatus('Page info displayed!', 'success');
  } catch (error) {
    showStatus('Error getting page info', 'error');
  }
});

// Reset page to original state
document.getElementById('resetPage').addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => {
        // Reset background
        document.body.style.backgroundColor = '';
        
        // Reset links
        const links = document.querySelectorAll('a');
        links.forEach(link => {
          link.style.backgroundColor = '';
          link.style.padding = '';
          link.style.border = '';
        });
      }
    });
    
    showStatus('Page reset!', 'success');
  } catch (error) {
    showStatus('Error resetting page', 'error');
  }
});

// View Extracted Text - Display previously captured text
document.getElementById('viewExtractedText').addEventListener('click', async () => {
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
});

// AI Service instance - will be initialized with API key
let aiService = null;

// Initialize AI service with API key
async function initializeAI() {
  try {
    // In a real extension, you'd want to store the API key securely
    // For now, prompt user for API key if not stored
    const result = await chrome.storage.local.get(['llamaApiKey']);
    
    if (!result.llamaApiKey) {
      const apiKey = prompt('Please enter your Llama API key:');
      if (apiKey) {
        await chrome.storage.local.set({ llamaApiKey: apiKey });
        aiService = new AIService(apiKey);
      } else {
        throw new Error('API key required for AI features');
      }
    } else {
      aiService = new AIService(result.llamaApiKey);
    }
  } catch (error) {
    console.error('Failed to initialize AI service:', error);
    showStatus('AI features require API key', 'error');
  }
}

// Get extracted text from storage
async function getExtractedText() {
  const result = await chrome.storage.local.get(['quizData']);
  if (!result.quizData) {
    throw new Error('No extracted text found. Please click "Take My Quiz" first!');
  }
  return result.quizData.textContent;
}

// Show status message
function showStatus(message, type) {
  const statusDiv = document.getElementById('status');
  statusDiv.textContent = message;
  statusDiv.className = type;
  
  setTimeout(() => {
    statusDiv.textContent = '';
    statusDiv.className = '';
  }, 3000);
}

// Generate Quiz Questions using AI
document.getElementById('generateQuiz').addEventListener('click', async () => {
  try {
    if (!aiService) await initializeAI();
    if (!aiService) return;
    
    showStatus('Generating quiz questions...', 'success');
    
    const extractedText = await getExtractedText();
    const quizQuestions = await aiService.generateQuiz(extractedText);
    
    // Display quiz in a new window
    const quizWindow = window.open('', 'QuizQuestions', 'width=800,height=600,scrollbars=yes');
    quizWindow.document.write(`
      <html>
        <head>
          <title>AI Generated Quiz</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; }
            .question { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .option { margin: 5px 0; padding: 5px; cursor: pointer; }
            .option:hover { background-color: #f0f0f0; }
          </style>
        </head>
        <body>
          <h1>🧠 AI Generated Quiz Questions</h1>
          <div id="quiz-content">
            ${typeof quizQuestions === 'string' ? 
              `<pre>${quizQuestions}</pre>` : 
              JSON.stringify(quizQuestions, null, 2)}
          </div>
        </body>
      </html>
    `);
    quizWindow.document.close();
    
    showStatus('Quiz questions generated!', 'success');
  } catch (error) {
    console.error('Error generating quiz:', error);
    showStatus(error.message, 'error');
  }
});

// Summarize Content using AI
document.getElementById('summarizeText').addEventListener('click', async () => {
  try {
    if (!aiService) await initializeAI();
    if (!aiService) return;
    
    showStatus('Generating summary...', 'success');
    
    const extractedText = await getExtractedText();
    const summary = await aiService.summarize(extractedText);
    
    // Display summary in alert for now (could be improved with a nice popup)
    alert(`📝 Content Summary:\n\n${summary}`);
    
    showStatus('Summary generated!', 'success');
  } catch (error) {
    console.error('Error generating summary:', error);
    showStatus(error.message, 'error');
  }
});

// Extract Key Points using AI
document.getElementById('extractKeyPoints').addEventListener('click', async () => {
  try {
    if (!aiService) await initializeAI();
    if (!aiService) return;
    
    showStatus('Extracting key points...', 'success');
    
    const extractedText = await getExtractedText();
    const keyPoints = await aiService.extractKeyPoints(extractedText);
    
    // Display key points in a new window
    const keyPointsWindow = window.open('', 'KeyPoints', 'width=600,height=500,scrollbars=yes');
    keyPointsWindow.document.write(`
      <html>
        <head>
          <title>Key Points</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
            h1 { color: #333; }
          </style>
        </head>
        <body>
          <h1>🔑 Key Points</h1>
          <div style="white-space: pre-wrap;">${keyPoints}</div>
        </body>
      </html>
    `);
    keyPointsWindow.document.close();
    
    showStatus('Key points extracted!', 'success');
  } catch (error) {
    console.error('Error extracting key points:', error);
    showStatus(error.message, 'error');
  }
});

// Open Chatbot using AI
document.getElementById('openChatbot').addEventListener('click', async () => {
  try {
    if (!aiService) await initializeAI();
    if (!aiService) return;
    
    const extractedText = await getExtractedText();
    
    // Open chatbot in a new window
    const chatWindow = window.open('', 'Chatbot', 'width=700,height=600,scrollbars=yes');
    chatWindow.document.write(`
      <html>
        <head>
          <title>Content Chatbot</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; margin: 0; }
            #chat-container { height: 500px; border: 1px solid #ddd; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
            #chat-input { width: 70%; padding: 10px; }
            #send-btn { width: 25%; padding: 10px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #e3f2fd; text-align: right; }
            .ai { background: #f0f0f0; }
          </style>
        </head>
        <body>
          <h1>💬 Chat About This Content</h1>
          <div id="chat-container">
            <div class="message ai">Hi! I can answer questions about the content from the webpage. What would you like to know?</div>
          </div>
          <input type="text" id="chat-input" placeholder="Ask a question about the content..." />
          <button id="send-btn">Send</button>
          
          <script>
            const extractedText = \`${extractedText.replace(/`/g, '\\`')}\`;
            // This would need to be implemented with proper message passing to the extension
            document.getElementById('send-btn').addEventListener('click', () => {
              alert('Chatbot functionality would be implemented here with proper message passing to the extension');
            });
          </script>
        </body>
      </html>
    `);
    chatWindow.document.close();
    
    showStatus('Chatbot opened!', 'success');
  } catch (error) {
    console.error('Error opening chatbot:', error);
    showStatus(error.message, 'error');
  }
});
