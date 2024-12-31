import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleAIAgent:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
        self.conversation_history = []

    def get_response(self, user_input):
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=150
            )
            
            # Extract assistant's response
            assistant_response = response.choices[0].message.content
            
            # Add assistant's response to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    # Initialize the agent
    agent = SimpleAIAgent()
    
    print("Hello! I'm your AI assistant. Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
            
        response = agent.get_response(user_input)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    main()