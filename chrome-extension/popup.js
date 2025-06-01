// Get current tab information when popup loads
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    document.getElementById('pageUrl').textContent = tab.url;
  } catch (error) {
    document.getElementById('pageUrl').textContent = 'Unable to get page URL';
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
