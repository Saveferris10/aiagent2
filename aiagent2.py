import openai
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import requests
import wikipedia
import sqlite3
from typing import Dict, List

class AdvancedAIAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        openai.api_key = self.api_key
        self.conversation_history = []
        self.setup_database()
        
        self.commands = {
            '/help': self.show_help,
            '/clear': self.clear_history,
            '/save': self.save_conversation,
            '/history': self.show_history,
            '/weather': self.get_weather,
            '/search': self.web_search,
            '/note': self.take_note,
            '/notes': self.show_notes,
            '/remind': self.set_reminder
        }

    def setup_database(self):
        """Initialize SQLite database for notes and reminders"""
        self.conn = sqlite3.connect('agent_data.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes
            (id INTEGER PRIMARY KEY, content TEXT, timestamp TEXT)
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders
            (id INTEGER PRIMARY KEY, content TEXT, due_date TEXT)
        ''')
        self.conn.commit()

    def clear_history(self) -> str:
        """Clear the conversation history"""
        self.conversation_history = []
        return "Conversation history cleared!"

    def save_conversation(self) -> str:
        """Save the conversation to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        return f"Conversation saved to {filename}"

    def show_history(self) -> str:
        """Show the conversation history"""
        if not self.conversation_history:
            return "No conversation history yet."
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history])

    def get_weather(self, city: str = "New York") -> str:
        """Get weather information for a city"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                return f"Weather in {city}: {description}, Temperature: {temp}°C"
            return "Could not fetch weather data"
        except Exception as e:
            return f"Error getting weather: {str(e)}"

    def web_search(self, query: str) -> str:
        """Search Wikipedia for information"""
        try:
            result = wikipedia.summary(query, sentences=2)
            return result
        except Exception as e:
            return f"Error searching: {str(e)}"

    def take_note(self, content: str) -> str:
        """Save a note to database"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO notes (content, timestamp) VALUES (?, ?)",
                          (content, timestamp))
        self.conn.commit()
        return "Note saved successfully!"

    def show_notes(self) -> str:
        """Retrieve all notes"""
        self.cursor.execute("SELECT content, timestamp FROM notes")
        notes = self.cursor.fetchall()
        if not notes:
            return "No notes found."
        
        return "\n".join([f"{timestamp}: {content}" for content, timestamp in notes])

    def set_reminder(self, content: str, due_date: str) -> str:
        """Set a reminder"""
        try:
            self.cursor.execute("INSERT INTO reminders (content, due_date) VALUES (?, ?)",
                              (content, due_date))
            self.conn.commit()
            return "Reminder set successfully!"
        except Exception as e:
            return f"Error setting reminder: {str(e)}"

    def process_command(self, user_input: str) -> str:
        """Process commands with arguments"""
        parts = user_input.split(' ', 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        if command in self.commands:
            if command == '/weather':
                return self.get_weather(args) if args else self.get_weather()
            elif command == '/search':
                return self.web_search(args) if args else "Please provide a search query"
            elif command == '/note':
                return self.take_note(args) if args else "Please provide note content"
            elif command == '/remind':
                try:
                    content, due_date = args.rsplit(' ', 1)
                    return self.set_reminder(content, due_date)
                except ValueError:
                    return "Please provide reminder content and due date"
            else:
                return self.commands[command]()
        
        return "Unknown command. Type /help for available commands."

    def get_ai_response(self, user_input: str) -> str:
        """Get response from AI model"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history + [{"role": "user", "content": user_input}],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting AI response: {str(e)}"

    def show_help(self) -> str:
        return """
Available commands:
/help - Show this help message
/clear - Clear conversation history
/save - Save conversation to file
/history - Show conversation history
/weather [city] - Get weather for a city
/search [query] - Search Wikipedia
/note [content] - Save a note
/notes - Show all notes
/remind [content] [YYYY-MM-DD] - Set a reminder
        """

def main():
    print("=" * 50)
    print("Advanced AI Assistant")
    print("Type /help for available commands or 'quit' to exit")
    print("=" * 50)
    
    agent = AdvancedAIAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("\nGoodbye! Have a great day!")
                break
                
            if user_input.startswith('/'):
                response = agent.process_command(user_input)
            else:
                response = agent.get_ai_response(user_input)
                agent.conversation_history.append({"role": "user", "content": user_input})
                agent.conversation_history.append({"role": "assistant", "content": response})
            
            print(f"\nAssistant: {response}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()