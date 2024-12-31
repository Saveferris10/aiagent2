import openai
import os
from dotenv import load_dotenv
from datetime import datetime
import json

class EnhancedAIAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
        self.conversation_history = []
        self.commands = {
            '/help': self.show_help,
            '/clear': self.clear_history,
            '/save': self.save_conversation,
            '/history': self.show_history
        }

    def show_help(self):
        return """
Available commands:
/help - Show this help message
/clear - Clear conversation history
/save - Save conversation to file
/history - Show conversation history
        """

    def clear_history(self):
        self.conversation_history = []
        return "Conversation history cleared!"

    def save_conversation(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        return f"Conversation saved to {filename}"

    def show_history(self):
        if not self.conversation_history:
            return "No conversation history yet."
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history])

    def get_response(self, user_input):
        # Check if input is a command
        if user_input.startswith('/'):
            command = self.commands.get(user_input.split()[0])
            if command:
                return command()
            return "Unknown command. Type /help for available commands."

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
            
            assistant_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    print("=" * 50)
    print("Enhanced AI Assistant")
    print("Type /help for available commands or 'quit' to exit")
    print("=" * 50)
    
    agent = EnhancedAIAgent()
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("\nGoodbye! Have a great day!")
            break
            
        response = agent.get_response(user_input)
        print(f"\nAssistant: {response}")
        print("-" * 50)

if __name__ == "__main__":
    main()