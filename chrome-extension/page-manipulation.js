// Core page manipulation functions
class PageManipulation {
  constructor() {
    this.setupEventListeners();
  }

  setupEventListeners() {
    document.getElementById('changeBackground').addEventListener('click', this.changeBackground.bind(this));
    document.getElementById('highlightLinks').addEventListener('click', this.highlightLinks.bind(this));
    document.getElementById('showPageInfo').addEventListener('click', this.showPageInfo.bind(this));
    document.getElementById('resetPage').addEventListener('click', this.resetPage.bind(this));
  }

  // Change background color of the current page
  async changeBackground() {
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
  }

  // Highlight all links on the page
  async highlightLinks() {
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
  }

  // Show page information
  async showPageInfo() {
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
  }

  // Reset page to original state
  async resetPage() {
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
  }
}

// Initialize page manipulation when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PageManipulation();
});
