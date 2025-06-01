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
    // Check if API key is already stored
    const result = await chrome.storage.local.get(['llamaApiKey']);
    
    if (!result.llamaApiKey) {
      // Prompt user for API key if not stored
      const apiKey = prompt('Please enter your Llama API key (it will be stored securely):');
      if (apiKey && apiKey.trim()) {
        await chrome.storage.local.set({ llamaApiKey: apiKey.trim() });
        aiService = new AIService(apiKey.trim());
        console.log('AI service initialized successfully with new API key');
      } else {
        throw new Error('API key is required for AI features');
      }
    } else {
      // Use stored API key
      aiService = new AIService(result.llamaApiKey);
      console.log('AI service initialized successfully with stored API key');
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
    
    console.log('Generated quiz questions:', quizQuestions);
    
    // Create an interactive quiz display
    const quizWindow = window.open('', 'QuizQuestions', 'width=900,height=700,scrollbars=yes');
    
    let quizHTML = '';
    if (Array.isArray(quizQuestions)) {
      quizHTML = quizQuestions.map((q, index) => {
        const optionsHTML = q.options ? q.options.map((option, optIndex) => 
          `<div class="option" data-question="${index}" data-option="${optIndex}">
            ${String.fromCharCode(65 + optIndex)}. ${option}
          </div>`
        ).join('') : '<div>No options available</div>';
        
        return `
          <div class="question-container" id="question-${index}">
            <div class="question">
              <h3>Question ${index + 1}: ${q.question || 'No question text'}</h3>
              <div class="options">
                ${optionsHTML}
              </div>
              <div class="answer-section" id="answer-${index}" style="display: none;">
                <div class="correct-answer">
                  ✅ Correct Answer: ${q.options && q.correct !== undefined ? 
                    String.fromCharCode(65 + q.correct) + '. ' + q.options[q.correct] : 
                    'Answer not available'}
                </div>
                ${q.explanation ? `<div class="explanation">💡 ${q.explanation}</div>` : ''}
              </div>
              <button class="show-answer-btn" onclick="toggleAnswer(${index})">Show Answer</button>
            </div>
          </div>
        `;
      }).join('');
    } else {
      quizHTML = `<div class="error">Error generating quiz. Raw response: <pre>${JSON.stringify(quizQuestions, null, 2)}</pre></div>`;
    }
    
    quizWindow.document.write(`
      <html>
        <head>
          <title>AI Generated Quiz</title>
          <style>
            body { 
              font-family: Arial, sans-serif; 
              padding: 20px; 
              max-width: 900px; 
              margin: 0 auto;
              background-color: #f5f5f5;
            }
            
            h1 { 
              text-align: center; 
              color: #333; 
              margin-bottom: 30px;
            }
            
            .question-container { 
              background: white;
              margin: 20px 0; 
              padding: 20px; 
              border-radius: 10px; 
              box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .question h3 {
              color: #2c3e50;
              margin-bottom: 15px;
              font-size: 18px;
            }
            
            .option { 
              margin: 8px 0; 
              padding: 12px; 
              cursor: pointer; 
              border: 2px solid #ddd;
              border-radius: 5px;
              transition: all 0.3s ease;
              background-color: #fafafa;
            }
            
            .option:hover { 
              background-color: #e3f2fd; 
              border-color: #2196F3;
            }
            
            .option.selected {
              background-color: #bbdefb;
              border-color: #1976D2;
            }
            
            .option.correct {
              background-color: #c8e6c9;
              border-color: #4CAF50;
            }
            
            .option.incorrect {
              background-color: #ffcdd2;
              border-color: #f44336;
            }
            
            .show-answer-btn {
              background-color: #2196F3;
              color: white;
              border: none;
              padding: 10px 20px;
              border-radius: 5px;
              cursor: pointer;
              margin-top: 15px;
              font-size: 14px;
            }
            
            .show-answer-btn:hover {
              background-color: #1976D2;
            }
            
            .answer-section {
              margin-top: 15px;
              padding: 15px;
              background-color: #f8f9fa;
              border-left: 4px solid #4CAF50;
              border-radius: 0 5px 5px 0;
            }
            
            .correct-answer {
              font-weight: bold;
              color: #2e7d32;
              margin-bottom: 10px;
            }
            
            .explanation {
              color: #555;
              font-style: italic;
              line-height: 1.5;
            }
            
            .error {
              background-color: #ffebee;
              border: 1px solid #f44336;
              padding: 20px;
              border-radius: 5px;
              color: #c62828;
            }
            
            .score-section {
              text-align: center;
              margin: 30px 0;
              padding: 20px;
              background: white;
              border-radius: 10px;
              box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
          </style>
        </head>
        <body>
          <h1>🧠 AI Generated Quiz</h1>
          
          <div class="score-section">
            <h3>Instructions</h3>
            <p>Click on an answer choice, then click "Show Answer" to see if you got it right!</p>
          </div>
          
          ${quizHTML}
          
          <script>
            let selectedAnswers = {};
            
            // Handle option selection
            document.querySelectorAll('.option').forEach(option => {
              option.addEventListener('click', function() {
                const questionId = this.dataset.question;
                const optionId = this.dataset.option;
                
                // Remove previous selection for this question
                document.querySelectorAll(\`[data-question="\${questionId}"]\`).forEach(opt => {
                  opt.classList.remove('selected');
                });
                
                // Mark this option as selected
                this.classList.add('selected');
                selectedAnswers[questionId] = parseInt(optionId);
              });
            });
            
            // Show answer function
            function toggleAnswer(questionIndex) {
              const answerSection = document.getElementById('answer-' + questionIndex);
              const button = document.querySelector(\`#question-\${questionIndex} .show-answer-btn\`);
              
              if (answerSection.style.display === 'none') {
                answerSection.style.display = 'block';
                button.textContent = 'Hide Answer';
                
                // Highlight correct/incorrect options
                const correctAnswer = ${JSON.stringify(quizQuestions.map(q => q.correct))};
                const questionOptions = document.querySelectorAll(\`[data-question="\${questionIndex}"]\`);
                
                questionOptions.forEach((option, index) => {
                  if (index === correctAnswer[questionIndex]) {
                    option.classList.add('correct');
                  } else if (selectedAnswers[questionIndex] === index) {
                    option.classList.add('incorrect');
                  }
                });
                
              } else {
                answerSection.style.display = 'none';
                button.textContent = 'Show Answer';
                
                // Remove highlighting
                const questionOptions = document.querySelectorAll(\`[data-question="\${questionIndex}"]\`);
                questionOptions.forEach(option => {
                  option.classList.remove('correct', 'incorrect');
                });
              }
            }
          </script>
        </body>
      </html>
    `);
    quizWindow.document.close();
    
    showStatus('Interactive quiz generated!', 'success');
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

// Manage API Key
document.getElementById('manageApiKey').addEventListener('click', async () => {
  try {
    const result = await chrome.storage.local.get(['llamaApiKey']);
    
    const actions = ['View', 'Change', 'Clear'];
    const action = prompt(`API Key Management:\n1. View current key (masked)\n2. Change API key\n3. Clear API key\n\nEnter 1, 2, or 3:`);
    
    switch(action) {
      case '1': // View
        if (result.llamaApiKey) {
          const maskedKey = result.llamaApiKey.substring(0, 10) + '***' + result.llamaApiKey.substring(result.llamaApiKey.length - 5);
          alert(`Current API Key: ${maskedKey}`);
        } else {
          alert('No API key stored');
        }
        break;
        
      case '2': // Change
        const newKey = prompt('Enter new Llama API key:');
        if (newKey && newKey.trim()) {
          await chrome.storage.local.set({ llamaApiKey: newKey.trim() });
          aiService = null; // Reset service to use new key
          showStatus('API key updated successfully', 'success');
        }
        break;
        
      case '3': // Clear
        if (confirm('Are you sure you want to clear the stored API key?')) {
          await chrome.storage.local.remove(['llamaApiKey']);
          aiService = null;
          showStatus('API key cleared', 'success');
        }
        break;
        
      default:
        showStatus('Invalid option selected', 'error');
    }
  } catch (error) {
    console.error('Error managing API key:', error);
    showStatus('Error managing API key', 'error');
  }
});
