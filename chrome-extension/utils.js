// Utility functions and shared functionality
class Utils {
  // Show status message
  static showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = type;
    
    setTimeout(() => {
      statusDiv.textContent = '';
      statusDiv.className = '';
    }, 3000);
  }

  // Initialize current page URL display
  static async initializePageInfo() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      document.getElementById('pageUrl').textContent = tab.url;
    } catch (error) {
      document.getElementById('pageUrl').textContent = 'Unable to get page URL';
    }
  }
}

// Make showStatus available globally for backwards compatibility
window.showStatus = Utils.showStatus;

// Get current tab information when popup loads
document.addEventListener('DOMContentLoaded', async () => {
  await Utils.initializePageInfo();
});
