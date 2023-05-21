# OpenAI Chat API Experiment

This script allows you to experiment with and understand requests and responses to the OpenAI chat completions API. It provides a simple interactive interface where you can ask questions and get responses from the OpenAI model, using your own OpenAI API key. The script maintains conversation context throughout the chat, limited by token size, and includes debugging statements that output the number of tokens used per request, and the number of tokens used across the entire conversation. When the token size limit is reached, the script auto-expires the oldest conversation turn in order to stay below the token limits. This gives the bot a "memory" and allows for the latest context memory to be maintined. The script also allows you to set arbitrary token size limits for experimentation, and includes the full HTTP response payload from the API for inspection, to help you understand how things are working under the hood. This is a work in progress and is intended for experimentation and learning only. Enjoy!!!

## Environment Variables

The following environment variables should be set:

- `API_KEY`: Your OpenAI API key.
- `LANGUAGE_MODEL`: The name of the language model to use.
- `MAX_RESPONSE_TOKENS`: The maximum number of tokens in the response from the model.
- `TEMPERATURE`: The temperature parameter for generating diverse responses.
- `MAX_CONTEXT_TOKENS`: The maximum number of tokens in the conversation context.

## Dependencies

The following dependencies are required:

- `httpx`: A modern, async HTTP client for Python.
- `rich`: A Python library for rich text and beautiful formatting in the terminal.
- `tiktoken`: A Python library for counting tokens in a string.
- `dotenv`: A Python library for loading environment variables from a `.env` file.

## OpenAI API key

You can get your own API key here: [https://platform.openai.com/account](https://platform.openai.com/account).

## Installation

### Python Installation (Mac)

1. Install Homebrew (if not already installed) by following the instructions at [https://brew.sh/](https://brew.sh/).

2. Open Terminal and run the following command to install Python:

    ```shell
    brew install python
    ```

### Python Installation (Windows)

1. Go to the official Python website at [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/).

2. Download the latest version of Python for Windows.

3. Run the downloaded installer and follow the installation instructions.

### Project Setup

1. Clone the repository:

    ```shell
    git clone <repository_url>
    ```

2. Navigate to the project directory:

    ```shell
    cd <project_directory>
    ```

3. Create a virtual environment (optional but recommended):

    ```shell
    python -m venv env
    ```

4. Activate the virtual environment:

    - Mac/Linux:

        ```shell
        source env/bin/activate
        ```

    - Windows:

        ```shell
        .\env\Scripts\activate
        ```

5. Install the required dependencies:

    ```shell
    pip install -r requirements.txt
    ```

## Usage

1. Set the required environment variables by creating a `.env` file in the project directory and adding the following lines:

    ```
    API_KEY=<your_api_key>
    LANGUAGE_MODEL=<language_model_name>
    MAX_RESPONSE_TOKENS=<max_response_tokens>
    TEMPERATURE=<temperature>
    MAX_CONTEXT_TOKENS=<max_context_tokens>
    ```

2. Run the script:

    ```shell
    python script.py
    ```

3. Enter a question when prompted.

4. To exit the script, enter `quit`.

## License

This project is licensed under the [MIT License](LICENSE).
