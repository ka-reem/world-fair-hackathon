// AI Service for Chrome Extension
class AIService {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = "https://api.llama.com/compat/v1/";
  }

  async callAPI(messages) {
    try {
      const response = await fetch(`${this.baseUrl}chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "Llama-4-Maverick-17B-128E-Instruct-FP8",
          messages: messages,
          max_tokens: 1000,
          temperature: 0.7
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      return data.choices[0].message.content;
    } catch (error) {
      console.error('AI API Error:', error);
      throw error;
    }
  }

  // Generate quiz questions from text
  async generateQuiz(text, numQuestions = 5) {
    const messages = [
      {
        role: "system",
        content: "You are a helpful quiz generator. Create multiple choice questions based on the provided text. You MUST respond with valid JSON only - no other text. Format your response as a JSON array of objects with 'question', 'options' (array of 4 choices), 'correct' (index of correct answer, 0-3), and 'explanation' (why this is the correct answer)."
      },
      {
        role: "user",
        content: `Based on this text, create ${numQuestions} multiple choice questions. Respond with ONLY valid JSON:\n\n${text.substring(0, 3000)}` // Limit text length
      }
    ];

    const response = await this.callAPI(messages);
    
    try {
      // Clean the response to ensure it's valid JSON
      let cleanResponse = response.trim();
      
      // Remove any markdown code blocks if present
      if (cleanResponse.startsWith('```json')) {
        cleanResponse = cleanResponse.replace(/```json\s*/, '').replace(/```\s*$/, '');
      } else if (cleanResponse.startsWith('```')) {
        cleanResponse = cleanResponse.replace(/```\s*/, '').replace(/```\s*$/, '');
      }
      
      const parsed = JSON.parse(cleanResponse);
      
      // Validate the structure
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed;
      } else {
        throw new Error('Invalid quiz format received');
      }
    } catch (e) {
      console.warn('AI response was not valid JSON:', response);
      // Return a fallback quiz format
      return [{
        question: "Quiz Generation Error",
        options: [
          "The AI response was not in the expected format",
          "Please try again",
          "Check the console for details",
          "Raw response: " + response.substring(0, 100) + "..."
        ],
        correct: 0,
        explanation: "There was an error parsing the AI response. Raw response: " + response
      }];
    }
  }

  // Chatbot functionality
  async chat(userMessage, context = "") {
    const messages = [
      {
        role: "system",
        content: `You are a helpful assistant that can answer questions about web content. ${context ? `Here's some context from the webpage: ${context.substring(0, 2000)}` : ''}`
      },
      {
        role: "user",
        content: userMessage
      }
    ];

    return await this.callAPI(messages);
  }

  // Summarize the extracted text
  async summarize(text) {
    const messages = [
      {
        role: "system",
        content: "You are a helpful assistant that creates concise summaries of text content."
      },
      {
        role: "user",
        content: `Please provide a concise summary of this text:\n\n${text.substring(0, 4000)}`
      }
    ];

    return await this.callAPI(messages);
  }

  // Extract key points from text
  async extractKeyPoints(text) {
    const messages = [
      {
        role: "system",
        content: "You are a helpful assistant that extracts key points from text. Return them as a bulleted list."
      },
      {
        role: "user",
        content: `Extract the key points from this text:\n\n${text.substring(0, 4000)}`
      }
    ];

    return await this.callAPI(messages);
  }
}
