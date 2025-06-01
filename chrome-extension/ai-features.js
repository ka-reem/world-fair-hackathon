// AI-powered features
class AIFeatures {
  constructor() {
    this.aiService = null;
    this.setupEventListeners();
  }

  setupEventListeners() {
    document.getElementById('generateQuiz').addEventListener('click', this.generateQuiz.bind(this));
    document.getElementById('summarizeText').addEventListener('click', this.summarizeText.bind(this));
    document.getElementById('extractKeyPoints').addEventListener('click', this.extractKeyPoints.bind(this));
    document.getElementById('openChatbot').addEventListener('click', this.openChatbot.bind(this));
    document.getElementById('manageApiKey').addEventListener('click', this.manageApiKey.bind(this));
  }

  // Initialize AI service with API key
  async initializeAI() {
    try {
      // Check if API key is already stored
      const result = await chrome.storage.local.get(['llamaApiKey']);
      
      if (!result.llamaApiKey) {
        // Prompt user for API key if not stored
        const apiKey = prompt('Please enter your Llama API key (it will be stored securely):');
        if (apiKey && apiKey.trim()) {
          await chrome.storage.local.set({ llamaApiKey: apiKey.trim() });
          this.aiService = new AIService(apiKey.trim());
          console.log('AI service initialized successfully with new API key');
        } else {
          throw new Error('API key is required for AI features');
        }
      } else {
        // Use stored API key
        this.aiService = new AIService(result.llamaApiKey);
        console.log('AI service initialized successfully with stored API key');
      }
    } catch (error) {
      console.error('Failed to initialize AI service:', error);
      showStatus('AI features require API key', 'error');
    }
  }

  // Generate Quiz Questions using AI
  async generateQuiz() {
    try {
      if (!this.aiService) await this.initializeAI();
      if (!this.aiService) return;
      
      showStatus('Generating quiz questions...', 'success');
      
      const extractedText = await TextExtraction.getExtractedText();
      const quizQuestions = await this.aiService.generateQuiz(extractedText);
      
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
  }

  // Summarize Content using AI
  async summarizeText() {
    try {
      if (!this.aiService) await this.initializeAI();
      if (!this.aiService) return;
      
      showStatus('Generating summary...', 'success');
      
      const extractedText = await TextExtraction.getExtractedText();
      const summary = await this.aiService.summarize(extractedText);
      
      // Display summary in alert for now (could be improved with a nice popup)
      alert(`📝 Content Summary:\n\n${summary}`);
      
      showStatus('Summary generated!', 'success');
    } catch (error) {
      console.error('Error generating summary:', error);
      showStatus(error.message, 'error');
    }
  }

  // Extract Key Points using AI
  async extractKeyPoints() {
    try {
      if (!this.aiService) await this.initializeAI();
      if (!this.aiService) return;
      
      showStatus('Extracting key points...', 'success');
      
      const extractedText = await TextExtraction.getExtractedText();
      const keyPoints = await this.aiService.extractKeyPoints(extractedText);
      
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
  }

  // Open Chatbot using AI
  async openChatbot() {
    try {
      if (!this.aiService) await this.initializeAI();
      if (!this.aiService) return;
      
      const extractedText = await TextExtraction.getExtractedText();
      
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
  }

  // Manage API Key
  async manageApiKey() {
    try {
      const result = await chrome.storage.local.get(['llamaApiKey']);
      
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
            this.aiService = null; // Reset service to use new key
            showStatus('API key updated successfully', 'success');
          }
          break;
          
        case '3': // Clear
          if (confirm('Are you sure you want to clear the stored API key?')) {
            await chrome.storage.local.remove(['llamaApiKey']);
            this.aiService = null;
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
  }
}

// Initialize AI features when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new AIFeatures();
});
