// Content script that runs on all pages
console.log('Simple Chrome Extension content script loaded!');

// Add a subtle indicator that the extension is active
const indicator = document.createElement('div');
indicator.id = 'simple-extension-indicator';
indicator.textContent = '🚀 Extension Active';
indicator.style.cssText = `
  position: fixed;
  top: 10px;
  right: 10px;
  background: #4CAF50;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 10000;
  font-family: Arial, sans-serif;
  opacity: 0.8;
  transition: opacity 0.3s;
`;

// Add hover effect
indicator.addEventListener('mouseenter', () => {
  indicator.style.opacity = '1';
});

indicator.addEventListener('mouseleave', () => {
  indicator.style.opacity = '0.8';
});

// Add the indicator to the page
document.body.appendChild(indicator);

// Remove the indicator after 3 seconds
setTimeout(() => {
  if (indicator && indicator.parentNode) {
    indicator.style.opacity = '0';
    setTimeout(() => {
      if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
      }
    }, 300);
  }
}, 3000);
