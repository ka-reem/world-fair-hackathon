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
