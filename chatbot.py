import os
import sys
import json
import time
from dotenv import load_dotenv
import httpx
from rich import print
from rich.markdown import Markdown
import tiktoken
import re

# Load .env file
load_dotenv()

# Try to access your API key and raise an error if it doesn't exist
try:
    OPENAI_API_KEY = os.getenv('API_KEY')
    if OPENAI_API_KEY is None:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables")
except Exception as e:
    print(e)
    sys.exit(1)

OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

# Fetch environment variables once at the start
LANGUAGE_MODEL = os.getenv('LANGUAGE_MODEL')
MAX_RESPONSE_TOKENS = int(os.getenv('MAX_RESPONSE_TOKENS'))
TEMPERATURE = float(os.getenv('TEMPERATURE'))
MAX_CONTEXT_TOKENS = int(os.getenv('MAX_CONTEXT_TOKENS'))

# Define the initial prompt
try:
    initial_prompt = {
        'stream': True,
        'model': LANGUAGE_MODEL,
        'max_tokens': MAX_RESPONSE_TOKENS,
        'temperature': TEMPERATURE,
        'messages': [
            {'role': 'system', 'content': "You are a helpful assistant. You should always append one of the following strings to each and every response: 'Sentiment: Positive', 'Sentiment: Negative', or 'Sentiment: Neutral', based on your analysis of the sentiment of the text the entered by the user. If you don't detect a particular sentiment, append ' Sentiment: Neutral'."},
        ]
    }
except Exception as e:
    print(f"Error setting up initial_prompt: {e}")
    sys.exit(1)

# Define the headers for the API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {OPENAI_API_KEY}'
}

# Function to calculate number of tokens in a string
def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Helper function to extract sentiment from assistant message
def extract_sentiment(assistant_message):
    # Use regular expressions to find sentiment in the assistant message
    match = re.search(r'Sentiment:\s*(\w+)', assistant_message)
    if match:
        sentiment = match.group(1)
    else:
        sentiment = 'Neutral'  # Default to neutral if no sentiment found
    
    # print(f"Assistant message: {assistant_message}")
    # print(f"Matched sentiment: {sentiment}")
    return sentiment


# Main function to generate text from OpenAI
async def get_text(prompt):

    user_tokens = num_tokens_from_string(prompt, LANGUAGE_MODEL)

    initial_prompt['messages'].append({'role': 'user', 'content': prompt})

    total_tokens = 0

    for message in initial_prompt['messages']:
        total_tokens += num_tokens_from_string(message['content'], LANGUAGE_MODEL)

    print(f"Total tokens including this request: {total_tokens}")

    # The following while loop handles API requests and responses
    while True:
        try:
            async with httpx.AsyncClient() as client:
                # Some print statements for debugging and understanding the flow
                print(f"\nSending this initial_prompt to API: {initial_prompt}")
                print(f"Current temperature: {initial_prompt['temperature']}")

                # Main request to the OpenAI API
                async with client.stream('POST', OPENAI_API_URL, headers=headers, json=initial_prompt, timeout=10.0) as response:
                    # Handle successful response
                    if response.status_code == 200:
                        assistant_text = ""
                        async for line in response.aiter_lines():
                            if line.startswith("data: "): 
                                message = line[6:]
        
                                if message == "[DONE]":
                                    # print("Streamed response: [DONE]")
                                    break
                                else:
                                    # print(f"Streamed response: {message}")
                                    try:
                                        data = json.loads(message)['choices'][0]
                                    except json.JSONDecodeError as e:
                                        # print(f"JSONDecodeError: {e}, Message: {message}")
                                        continue

                                    
                                    # Check if the delta dictionary is empty
                                    if not data.get('delta'):
                                        # print("Received an empty delta dictionary. Skipping this chunk.")
                                        continue
                                    
                                    # Process each chunk of the response
                                    chunk_data = data['delta']

                                    # Monitor finish_reason
                                    finish_reason = data.get('finish_reason')
                                    if finish_reason and finish_reason != 'stop':
                                        print(f"Warning: finish_reason is {finish_reason}")

                                    # Append each chunk to the assistant_text
                                    if 'content' in chunk_data:
                                        chunk = chunk_data['content']
                                        assistant_text += chunk

                                        sys.stdout.write(chunk)
                                        sys.stdout.flush()

                        # Extract sentiment from the assistant's response
                        sentiment = extract_sentiment(assistant_text)

                        # Adjust the temperature based on sentiment
                        if sentiment.lower() == "negative":
                            initial_prompt['temperature'] = min(1.0, initial_prompt['temperature'] + 0.1)
                            print(f"\nAdjusted temperature to {initial_prompt['temperature']} due to negative sentiment")

                        # Update the messages and token count
                        initial_prompt['messages'].append({'role': 'assistant', 'content': assistant_text})
                        total_tokens += num_tokens_from_string(assistant_text, LANGUAGE_MODEL)  # Update total_tokens after appending assistant_text

                        print(f"\nTotal tokens including this response: {total_tokens}")

                        # Handle cases where token count exceeds maximum
                        while total_tokens >= MAX_CONTEXT_TOKENS:
                            # Get the oldest message that is not from the system
                            for i, message in enumerate(initial_prompt['messages']):
                                if message['role'] != 'system':
                                    removed_message = initial_prompt['messages'].pop(i)
                                    total_tokens -= num_tokens_from_string(removed_message['content'], LANGUAGE_MODEL)  # Update total_tokens after removing message
                                    break
                            else:
                                print("All remaining messages are system messages. Cannot remove any more messages.")
                                break

                        return assistant_text

                    elif response.status_code == 400:
                        # Handle case where API request was malformed
                        await response.read()
                        error_data = await response.json()
                        print(f"OpenAI API returned an API Error: {error_data}")
                        break
                    elif response.status_code == 429:
                        # Handle case where rate limit was exceeded
                        await response.read()
                        error_data = await response.json()
                        retry_after = int(response.headers.get('Retry-After', 1))
                        print(f"OpenAI API request exceeded rate limit: {error_data}")
                        time.sleep(retry_after)
                    else:
                        # Handle any other unexpected error
                        await response.read()
                        error_data = await response.json()
                        print(f"OpenAI API returned an unexpected error: {error_data}")
                        break
        except Exception as e:
            # Handle any other exceptions that may occur
            print(f"Error occurred while processing API request: {e}, Line: {sys.exc_info()[-1].tb_lineno}")

            break

# Main loop to handle user input and assistant responses
async def main():
    while True:
        # Get user input
        user_input = input("\n\nUser: ")

        # Exit the loop if the user types "quit"
        if user_input.lower().strip() == "quit":
            break

        # Get the assistant's response
        assistant_response = await get_text(user_input)

        # Print the assistant's response
        # print(f"\nAssistant: {assistant_response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

