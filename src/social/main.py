#!/usr/bin/env python
import sys
import warnings
from flask import Flask, request, jsonify
from crew import Social
import re

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = Flask(__name__)

def extract_prompts(output: str) -> list:
    """Extract clean prompts from the output"""
    print("\n=== Starting prompt extraction ===")
    print(f"Raw output type: {type(output)}")
    print(f"Raw output preview: {str(output)[:200]}...")
    
    prompts = []
    
    # Use regex to find prompts between --- PROMPT X: and ---
    import re
    pattern = r'--- PROMPT \d+:\s*(.*?)\s*---'
    matches = re.finditer(pattern, output, re.DOTALL)
    
    for match in matches:
        prompt = match.group(1).strip()
        prompts.append(prompt)
        print(f"\nFound prompt: {prompt[:100]}...")
    
    print(f"\nExtracted {len(prompts)} prompts")
    for i, prompt in enumerate(prompts, 1):
        print(f"Prompt {i} preview: {prompt[:100]}...")
    return prompts

@app.route('/generate-ideas', methods=['POST'])
def generate_ideas():
    try:
        # Get topic from request or use default
        data = request.get_json() or {}
        topic = data.get('topic', 'faith and personal growth')  # Default topic if none provided
        
        social = Social()
        output = social.run(topic=topic)  # Pass topic to run method
        
        return jsonify({
            'success': True,
            'output': output,
            'markdown_file': social.markdown_filepath
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs'
    }
    Social().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Social().crew().train(n_iterations=int(sys.argv[2]), filename=sys.argv[3], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Social().crew().replay(task_id=sys.argv[2])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Social().crew().test(n_iterations=int(sys.argv[2]), openai_model_name=sys.argv[3], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'train':
            train()
        elif command == 'replay':
            replay()
        elif command == 'test':
            test()
    else:
        # Run Flask app in development mode
        app.run(debug=True, host='0.0.0.0', port=5051)
