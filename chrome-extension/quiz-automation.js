// Quiz automation functionality
class QuizAutomation {
  constructor() {
    this.setupEventListeners();
  }

  setupEventListeners() {
    document.getElementById('autoAnswerQuiz').addEventListener('click', this.autoAnswerQuiz.bind(this));
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
            }, 500);
            
          }, 500);
          
          return { success: true };
        }
      });
      
      showStatus('Quiz auto-answer process started! Check browser console for details.', 'success');
    } catch (error) {
      console.error('Error in auto-answer process:', error);
      showStatus('Error in auto-answer process', 'error');
    }
  }
}

// Initialize quiz automation when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new QuizAutomation();
});
