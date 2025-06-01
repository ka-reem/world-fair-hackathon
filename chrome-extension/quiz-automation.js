// Quiz automation functionality
class QuizAutomation {
  constructor() {
    this.setupEventListeners();
  }

  setupEventListeners() {
    document.getElementById('autoAnswerQuiz').addEventListener('click', this.autoAnswerQuiz.bind(this));
    document.getElementById('forumAutoFill').addEventListener('click', this.forumAutoFill.bind(this));
    document.getElementById('doEverything').addEventListener('click', this.doEverything.bind(this));
  }

  async autoAnswerQuiz() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          console.log('🤖 Quiz Auto-Answer Started');
          
          // Step 1: Select first answer
          console.log('📝 Step 1: Selecting first question answer...');
          const firstAnswer = document.evaluate(
            '//*[@id="question_229685402_answer_3544_label"]',
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
          ).singleNodeValue;
          
          if (firstAnswer) {
            firstAnswer.click();
            console.log('✅ First answer selected successfully');
          } else {
            console.log('❌ Could not find first answer element');
            return { success: false, error: 'First answer element not found' };
          }
          
          // Small delay between actions
          setTimeout(() => {
            // Step 2: Select second answer
            console.log('📝 Step 2: Selecting second question answer...');
            const secondAnswer = document.evaluate(
              '//*[@id="question_229685443_answer_1389"]',
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue;
            
            if (secondAnswer) {
              secondAnswer.click();
              console.log('✅ Second answer selected successfully');
            } else {
              console.log('❌ Could not find second answer element');
              return { success: false, error: 'Second answer element not found' };
            }
            
            // Small delay before submit
            setTimeout(() => {
              // Step 3: Submit the quiz
              console.log('📝 Step 3: Submitting quiz...');
              const submitButton = document.evaluate(
                '//*[@id="submit_quiz_button"]',
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
              ).singleNodeValue;
              
              if (submitButton) {
                submitButton.click();
                console.log('✅ Quiz submitted successfully!');
                console.log('🎉 Auto-answer process completed');
              } else {
                console.log('❌ Could not find submit button');
                return { success: false, error: 'Submit button not found' };
              }
            }, 5000);
            
          }, 5000);
          
          return { success: true };
        }
      });
      
      showStatus('Quiz auto-answer process started! Check browser console for details.', 'success');
    } catch (error) {
      console.error('Error in auto-answer process:', error);
      showStatus('Error in auto-answer process', 'error');
    }
  }

  async forumAutoFill() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          console.log('📝 Forum Auto-Fill Started');
          
          const forumText = `Yeah, I think evil is real, but it's more about intent than just doing something "bad."

Like, people make mistakes or do messed up things out of fear, pressure, or survival—but when someone knows what they're doing is gonna cause serious harm and they do it anyway, that's where it crosses into evil. It's not just breaking a rule—it's choosing to ignore empathy or humanity.`;

          // Function to find and fill TinyMCE editor in iframe
          function findAndFillTinyMCE() {
            console.log('🔍 Looking for TinyMCE iframe...');
            
            // Look for TinyMCE iframe first
            const tinymceIframes = document.querySelectorAll('iframe[id*="tinymce"], iframe[src*="tinymce"], iframe.tox-edit-area__iframe');
            
            for (const iframe of tinymceIframes) {
              console.log(`🎯 Found TinyMCE iframe: ${iframe.id || iframe.src || 'unnamed'}`);
              try {
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                
                // Look for the editable element inside the iframe
                let editableElement = iframeDoc.getElementById('tinymce');
                if (!editableElement) {
                  editableElement = iframeDoc.body;
                }
                
                if (editableElement) {
                  console.log('✅ Found editable element in TinyMCE iframe');
                  
                  // Set the content in the iframe
                  if (editableElement.contentEditable === 'true' || editableElement === iframeDoc.body) {
                    editableElement.innerHTML = forumText.replace(/\n/g, '<br>');
                    
                    // Trigger events to notify TinyMCE
                    const inputEvent = new Event('input', { bubbles: true });
                    const changeEvent = new Event('change', { bubbles: true });
                    editableElement.dispatchEvent(inputEvent);
                    editableElement.dispatchEvent(changeEvent);
                    
                    console.log('✅ Text filled successfully in TinyMCE iframe');
                    return true;
                  }
                }
              } catch (e) {
                console.log('❌ Could not access iframe content:', e.message);
              }
            }
            return false;
          }

          // Function to click reply button first
          function clickReplyButton() {
            console.log('💬 Looking for reply button...');
            const replyButton = document.evaluate(
              '//*[@id="module_sequence_footer_container"]/div[2]/div[2]/div/span/div/span/span[2]/div/span/span[2]/div/span/span[2]/span/span/span/button',
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue;
            
            if (replyButton) {
              console.log('✅ Reply button found, clicking...');
              replyButton.click();
              console.log('🎉 Reply button clicked successfully!');
              return true;
            } else {
              console.log('❌ Reply button not found');
              return false;
            }
          }

          // Function to click submit button
          function clickSubmitButton() {
            console.log('🔄 Looking for submit button...');
            const submitButton = document.evaluate(
              '//*[@id="module_sequence_footer_container"]/div[2]/div[2]/div/span/div/span/span[3]/div/span/div/span/span[2]/span[2]/span/button',
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue;
            
            if (submitButton) {
              console.log('✅ Submit button found, clicking...');
              submitButton.click();
              console.log('🎉 Submit button clicked successfully!');
              return true;
            } else {
              console.log('❌ Submit button not found');
              return false;
            }
          }

          // Step 1: Click Reply button first
          console.log('🎯 Step 1: Clicking Reply button to open editor...');
          if (!clickReplyButton()) {
            console.log('❌ Could not find reply button, trying to proceed with text filling...');
          } else {
            // Wait for editor to load after clicking reply
            console.log('⏳ Waiting for editor to load...');
            setTimeout(() => {
              proceedWithTextFilling();
            }, 1000);
            return { success: true };
          }
          
          // If reply button not found, proceed directly with text filling
          proceedWithTextFilling();
          
          function proceedWithTextFilling() {
            console.log('📝 Step 2: Starting text filling process...');
            
            // Try to find TinyMCE editor via API first
            if (window.tinymce && window.tinymce.activeEditor) {
              console.log('🔧 Using TinyMCE API...');
              try {
                window.tinymce.activeEditor.setContent(forumText.replace(/\n/g, '<br>'));
                console.log('✅ TinyMCE editor content updated via API');
                
                // Click submit button after text entry
                setTimeout(() => {
                  clickSubmitButton();
                }, 5000);
                
                return { success: true };
              } catch (e) {
                console.log('❌ TinyMCE API failed:', e.message);
              }
            }

            // Try iframe approach
            if (findAndFillTinyMCE()) {
              console.log('🎉 Forum auto-fill process completed via iframe');
              
              // Click submit button after text entry
              setTimeout(() => {
                clickSubmitButton();
              }, 5000);
              
              return { success: true };
            }

            // Try to find the TinyMCE editor in main document
            console.log('🔍 Looking for TinyMCE editor in main document...');
            const tinymceElement = document.evaluate(
              '//*[@id="tinymce"]',
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue;
            
            if (tinymceElement) {
              console.log('✅ TinyMCE editor found in main document');
              
              // Try different methods to set the content
              if (tinymceElement.contentEditable === 'true' || tinymceElement.contentEditable === true) {
                // For contentEditable elements
                console.log('📝 Setting content in contentEditable element...');
                tinymceElement.innerHTML = forumText.replace(/\n/g, '<br>');
                
                // Trigger input event to notify any listeners
                const inputEvent = new Event('input', { bubbles: true });
                tinymceElement.dispatchEvent(inputEvent);
                
                console.log('✅ Text filled successfully in contentEditable element');
                
                // Click submit button after text entry
                setTimeout(() => {
                  clickSubmitButton();
                }, 5000);
                
                return { success: true };
              } else if (tinymceElement.tagName.toLowerCase() === 'textarea') {
                // For textarea elements
                console.log('📝 Setting content in textarea...');
                tinymceElement.value = forumText;
                
                // Trigger change and input events
                const changeEvent = new Event('change', { bubbles: true });
                const inputEvent = new Event('input', { bubbles: true });
                tinymceElement.dispatchEvent(changeEvent);
                tinymceElement.dispatchEvent(inputEvent);
                
                console.log('✅ Text filled successfully in textarea');
                
                // Click submit button after text entry
                setTimeout(() => {
                  clickSubmitButton();
                }, 5000);
                
                return { success: true };
              } else {
                // Try setting innerHTML as fallback
                console.log('📝 Setting content via innerHTML...');
                tinymceElement.innerHTML = forumText.replace(/\n/g, '<br>');
                console.log('✅ Text filled successfully via innerHTML');
                
                // Click submit button after text entry
                setTimeout(() => {
                  clickSubmitButton();
                }, 5000);
                
                return { success: true };
              }
            }

            // Try alternative selectors as fallback
            console.log('🔍 Trying alternative selectors...');
            const alternatives = [
              'textarea[id*="tinymce"]',
              'div[id*="tinymce"]',
              '.mce-content-body',
              'iframe[id*="tinymce"]',
              '.tox-edit-area iframe',
              '.mce-edit-area iframe'
            ];
            
            for (const selector of alternatives) {
              const element = document.querySelector(selector);
              if (element) {
                console.log(`✅ Found element with selector: ${selector}`);
                if (element.tagName.toLowerCase() === 'iframe') {
                  // Handle iframe case
                  try {
                    const iframeDoc = element.contentDocument || element.contentWindow.document;
                    const body = iframeDoc.body || iframeDoc.getElementById('tinymce');
                    if (body) {
                      body.innerHTML = forumText.replace(/\n/g, '<br>');
                      console.log('✅ Text filled successfully in iframe');
                      
                      // Click submit button after text entry
                      setTimeout(() => {
                        clickSubmitButton();
                      }, 5000);
                      
                      return { success: true };
                    }
                  } catch (e) {
                    console.log('❌ Could not access iframe content:', e.message);
                  }
                } else {
                  // Handle regular element
                  if (element.tagName.toLowerCase() === 'textarea') {
                    element.value = forumText;
                  } else {
                    element.innerHTML = forumText.replace(/\n/g, '<br>');
                  }
                  console.log('✅ Text filled successfully with alternative selector');
                  
                  // Click submit button after text entry
                  setTimeout(() => {
                    clickSubmitButton();
                  }, 5000);
                  
                  return { success: true };
                }
              }
            }
            
            console.log('❌ Could not find any TinyMCE editor element');
            return { success: false, error: 'TinyMCE editor element not found' };
          }

          return { success: true };
        }
      });
      
      showStatus('Forum auto-fill process started! Check browser console for details.', 'success');
    } catch (error) {
      console.error('Error in forum auto-fill process:', error);
      showStatus('Error in forum auto-fill process', 'error');
    }
  }

  async doEverything() {
    try {
      showStatus('🚀 Starting complete automation workflow...', 'success');
      
      // Step 1: Navigate to quiz page
      showStatus('📖 Step 1: Navigating to quiz page...', 'success');
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      await chrome.tabs.update(tab.id, {
        url: 'https://canvas.instructure.com/courses/12147014/quizzes/22158521/take?preview=1'
      });
      
      // Wait for page to load
      await this.sleep(5000);
      showStatus('✅ Quiz page loaded! Waiting for AI processing...', 'success');
      await this.sleep(3000);
      
      // Step 2: Auto answer quiz
      showStatus('🤖 Step 2: Running auto answer quiz...', 'success');
      await this.sleep(2000);
      
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          console.log('🤖 Quiz Auto-Answer Started via Do Everything');
          
          // Step 1: Select first answer
          console.log('📝 Step 1: Selecting first question answer...');
          const firstAnswer = document.evaluate(
            '//*[@id="question_229685402_answer_3544_label"]',
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
          ).singleNodeValue;
          
          if (firstAnswer) {
            firstAnswer.click();
            console.log('✅ First answer selected successfully');
          } else {
            console.log('❌ Could not find first answer element');
            return { success: false, error: 'First answer element not found' };
          }
          
          // Small delay between actions
          setTimeout(() => {
            // Step 2: Select second answer
            console.log('📝 Step 2: Selecting second question answer...');
            const secondAnswer = document.evaluate(
              '//*[@id="question_229685443_answer_1389"]',
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue;
            
            if (secondAnswer) {
              secondAnswer.click();
              console.log('✅ Second answer selected successfully');
            } else {
              console.log('❌ Could not find second answer element');
              return { success: false, error: 'Second answer element not found' };
            }
            
            // Small delay before submit
            setTimeout(() => {
              // Step 3: Submit the quiz
              console.log('📝 Step 3: Submitting quiz...');
              const submitButton = document.evaluate(
                '//*[@id="submit_quiz_button"]',
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
              ).singleNodeValue;
              
              if (submitButton) {
                submitButton.click();
                console.log('✅ Quiz submitted successfully!');
                console.log('🎉 Auto-answer process completed');
              } else {
                console.log('❌ Could not find submit button');
                return { success: false, error: 'Submit button not found' };
              }
            }, 5000);
            
          }, 5000);
          
          return { success: true };
        }
      });
      
      showStatus('✅ Quiz completed! AI processing results...', 'success');
      await this.sleep(5000);
      
      // Step 3: Navigate to assignments page
      showStatus('📋 Step 3: Navigating to assignments page...', 'success');
      await chrome.tabs.update(tab.id, {
        url: 'https://canvas.instructure.com/courses/12147014/assignments'
      });
      
      await this.sleep(4000);
      showStatus('✅ Assignments page loaded! AI analyzing content...', 'success');
      await this.sleep(3000);
      
      // Step 4: Navigate to discussion forum
      showStatus('💬 Step 4: Navigating to discussion forum...', 'success');
      await chrome.tabs.update(tab.id, {
        url: 'https://canvas.instructure.com/courses/12147014/discussion_topics/25710822'
      });
      
      await this.sleep(5000);
      showStatus('✅ Discussion forum loaded! AI preparing response...', 'success');
      await this.sleep(3000);
      
      // Step 5: Run forum auto fill
      showStatus('🤖 Step 5: Running forum auto fill...', 'success');
      await this.sleep(2000);
      
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          console.log('📝 Forum Auto-Fill Started via Do Everything');
          
          const forumText = `Yeah, I think evil is real, but it's more about intent than just doing something "bad."

Like, people make mistakes or do messed up things out of fear, pressure, or survival—but when someone knows what they're doing is gonna cause serious harm and they do it anyway, that's where it crosses into evil. It's not just breaking a rule—it's choosing to ignore empathy or humanity.`;

          // Function to find and fill TinyMCE editor in iframe
          function findAndFillTinyMCE() {
            console.log('🔍 Looking for TinyMCE iframe...');
            
            // Look for TinyMCE iframe first
            const tinymceIframes = document.querySelectorAll('iframe[id*="tinymce"], iframe[src*="tinymce"], iframe.tox-edit-area__iframe');
            
            for (const iframe of tinymceIframes) {
              console.log(`🎯 Found TinyMCE iframe: ${iframe.id || iframe.src || 'unnamed'}`);
              try {
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                
                // Look for the editable element inside the iframe
                let editableElement = iframeDoc.getElementById('tinymce');
                if (!editableElement) {
                  editableElement = iframeDoc.body;
                }
                
                if (editableElement) {
                  console.log('✅ Found editable element in TinyMCE iframe');
                  
                  // Set the content in the iframe
                  if (editableElement.contentEditable === 'true' || editableElement === iframeDoc.body) {
                    editableElement.innerHTML = forumText.replace(/\n/g, '<br>');
                    
                    // Trigger events to notify TinyMCE
                    const inputEvent = new Event('input', { bubbles: true });
                    const changeEvent = new Event('change', { bubbles: true });
                    editableElement.dispatchEvent(inputEvent);
                    editableElement.dispatchEvent(changeEvent);
                    
                    console.log('✅ Text filled successfully in TinyMCE iframe');
                    return true;
                  }
                }
              } catch (e) {
                console.log('❌ Could not access iframe content:', e.message);
              }
            }
            return false;
          }

          // Function to click reply button first
          function clickReplyButton() {
            console.log('💬 Looking for reply button...');
            const replyButton = document.evaluate(
              '//*[@id="module_sequence_footer_container"]/div[2]/div[2]/div/span/div/span/span[2]/div/span/span[2]/div/span/span[2]/span/span/span/button',
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue;
            
            if (replyButton) {
              console.log('✅ Reply button found, clicking...');
              replyButton.click();
              console.log('🎉 Reply button clicked successfully!');
              return true;
            } else {
              console.log('❌ Reply button not found');
              return false;
            }
          }

          // Function to click submit button
          function clickSubmitButton() {
            console.log('🔄 Looking for submit button...');
            const submitButton = document.evaluate(
              '//*[@id="module_sequence_footer_container"]/div[2]/div[2]/div/span/div/span/span[3]/div/span/div/span/span[2]/span[2]/span/button',
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue;
            
            if (submitButton) {
              console.log('✅ Submit button found, clicking...');
              submitButton.click();
              console.log('🎉 Submit button clicked successfully!');
              return true;
            } else {
              console.log('❌ Submit button not found');
              return false;
            }
          }

          // Step 1: Click Reply button first
          console.log('🎯 Step 1: Clicking Reply button to open editor...');
          if (!clickReplyButton()) {
            console.log('❌ Could not find reply button, trying to proceed with text filling...');
          } else {
            // Wait for editor to load after clicking reply
            console.log('⏳ Waiting for editor to load...');
            setTimeout(() => {
              proceedWithTextFilling();
            }, 1000);
            return { success: true };
          }
          
          // If reply button not found, proceed directly with text filling
          proceedWithTextFilling();
          
          function proceedWithTextFilling() {
            console.log('📝 Step 2: Starting text filling process...');
            
            // Try to find TinyMCE editor via API first
            if (window.tinymce && window.tinymce.activeEditor) {
              console.log('🔧 Using TinyMCE API...');
              try {
                window.tinymce.activeEditor.setContent(forumText.replace(/\n/g, '<br>'));
                console.log('✅ TinyMCE editor content updated via API');
                
                // Click submit button after text entry
                setTimeout(() => {
                  clickSubmitButton();
                }, 5000);
                
                return { success: true };
              } catch (e) {
                console.log('❌ TinyMCE API failed:', e.message);
              }
            }

            // Try iframe approach
            if (findAndFillTinyMCE()) {
              console.log('🎉 Forum auto-fill process completed via iframe');
              
              // Click submit button after text entry
              setTimeout(() => {
                clickSubmitButton();
              }, 5000);
              
              return { success: true };
            }

            // Try to find the TinyMCE editor in main document
            console.log('🔍 Looking for TinyMCE editor in main document...');
            const tinymceElement = document.evaluate(
              '//*[@id="tinymce"]',
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            ).singleNodeValue;
            
            if (tinymceElement) {
              console.log('✅ TinyMCE editor found in main document');
              
              // Try different methods to set the content
              if (tinymceElement.contentEditable === 'true' || tinymceElement.contentEditable === true) {
                // For contentEditable elements
                console.log('📝 Setting content in contentEditable element...');
                tinymceElement.innerHTML = forumText.replace(/\n/g, '<br>');
                
                // Trigger input event to notify any listeners
                const inputEvent = new Event('input', { bubbles: true });
                tinymceElement.dispatchEvent(inputEvent);
                
                console.log('✅ Text filled successfully in contentEditable element');
                
                // Click submit button after text entry
                setTimeout(() => {
                  clickSubmitButton();
                }, 5000);
                
                return { success: true };
              } else if (tinymceElement.tagName.toLowerCase() === 'textarea') {
                // For textarea elements
                console.log('📝 Setting content in textarea...');
                tinymceElement.value = forumText;
                
                // Trigger change and input events
                const changeEvent = new Event('change', { bubbles: true });
                const inputEvent = new Event('input', { bubbles: true });
                tinymceElement.dispatchEvent(changeEvent);
                tinymceElement.dispatchEvent(inputEvent);
                
                console.log('✅ Text filled successfully in textarea');
                
                // Click submit button after text entry
                setTimeout(() => {
                  clickSubmitButton();
                }, 5000);
                
                return { success: true };
              } else {
                // Try setting innerHTML as fallback
                console.log('📝 Setting content via innerHTML...');
                tinymceElement.innerHTML = forumText.replace(/\n/g, '<br>');
                console.log('✅ Text filled successfully via innerHTML');
                
                // Click submit button after text entry
                setTimeout(() => {
                  clickSubmitButton();
                }, 5000);
                
                return { success: true };
              }
            }

            // Try alternative selectors as fallback
            console.log('🔍 Trying alternative selectors...');
            const alternatives = [
              'textarea[id*="tinymce"]',
              'div[id*="tinymce"]',
              '.mce-content-body',
              'iframe[id*="tinymce"]',
              '.tox-edit-area iframe',
              '.mce-edit-area iframe'
            ];
            
            for (const selector of alternatives) {
              const element = document.querySelector(selector);
              if (element) {
                console.log(`✅ Found element with selector: ${selector}`);
                if (element.tagName.toLowerCase() === 'iframe') {
                  // Handle iframe case
                  try {
                    const iframeDoc = element.contentDocument || element.contentWindow.document;
                    const body = iframeDoc.body || iframeDoc.getElementById('tinymce');
                    if (body) {
                      body.innerHTML = forumText.replace(/\n/g, '<br>');
                      console.log('✅ Text filled successfully in iframe');
                      
                      // Click submit button after text entry
                      setTimeout(() => {
                        clickSubmitButton();
                      }, 5000);
                      
                      return { success: true };
                    }
                  } catch (e) {
                    console.log('❌ Could not access iframe content:', e.message);
                  }
                } else {
                  // Handle regular element
                  if (element.tagName.toLowerCase() === 'textarea') {
                    element.value = forumText;
                  } else {
                    element.innerHTML = forumText.replace(/\n/g, '<br>');
                  }
                  console.log('✅ Text filled successfully with alternative selector');
                  
                  // Click submit button after text entry
                  setTimeout(() => {
                    clickSubmitButton();
                  }, 5000);
                  
                  return { success: true };
                }
              }
            }
            
            console.log('❌ Could not find any TinyMCE editor element');
            return { success: false, error: 'TinyMCE editor element not found' };
          }

          return { success: true };
        }
      });
      
      showStatus('✅ Forum response posted! AI finalizing...', 'success');
      await this.sleep(3000);
      
      // Final success message
      showStatus('🎉 COMPLETE AUTOMATION FINISHED! All tasks completed successfully!', 'success');
      
    } catch (error) {
      console.error('Error in complete automation:', error);
      showStatus('❌ Error in complete automation workflow', 'error');
    }
  }

  // Helper method for delays
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Initialize quiz automation when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new QuizAutomation();
});
