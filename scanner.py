import ollama
import os

def find_relevant_file(issue_description):
    # Get a list of all files in your repo (excluding hidden ones)
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    # Use Llama 3.1 to guess which file is related to the issue
    prompt = f"Given these files: {files}, which one relates to: '{issue_description}'? Output ONLY the filename."
    response = ollama.chat(model='llama3.1:8b-instruct-q8_0', messages=[{'role': 'user', 'content': prompt}])
    
    return response['message']['content'].strip()