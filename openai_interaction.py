# openai_interaction.py
import os
import base64
import json
import logging
import requests
import yaml
from dotenv import load_dotenv

from prompts import EXTRACT_INFORMATION_PROMPT, ASK_QUESTION_ABOUT_CODE_PROMPT, EVALUATE_CANDIDATE_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
github_access_token = os.getenv("GITHUB_ACCESS_TOKEN")

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

models = config['models']

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_information_from_cv(image_path, api_params):
    base64_image = encode_image(image_path)

    # Prepare the messages for the chat model
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": EXTRACT_INFORMATION_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
            ],
        }
    ]

    # Prepare the payload for the API call
    payload = {
        "model": models['vision_model'],
        "messages": messages,
        "max_tokens": api_params['max_tokens'],
        "temperature": api_params.get('temperature', 0),
        "n": api_params.get('n', 1),
    }

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        response_json = response.json()
        response_text = response_json["choices"][0]["message"]["content"].strip()

        try:
            data = json.loads(response_text)
            extracted_info = data.get('extracted_info', {})
            cv_summary = data.get('cv_summary', '')
            return extracted_info, cv_summary
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}")
            return {}, response_text  # Return the raw text as summary if JSON parsing fails
    else:
        logger.error(f"API request failed with status code {response.status_code}: {response.text}")
        return {}, ""

def ask_question_about_code(codebase_text, question, api_params):
    if not codebase_text.strip():
        logger.error("Empty codebase_text provided. Skipping OpenAI API call.")
        return ""

    try:
        # Limit the codebase text to a manageable size
        max_codebase_length = 8000  # Adjust based on token limits
        codebase_excerpt = codebase_text[:max_codebase_length]

        prompt = ASK_QUESTION_ABOUT_CODE_PROMPT(codebase_excerpt, question)

        payload = {
            "model": models['language_model'],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": api_params.get('max_tokens', 500),
            "temperature": api_params.get('temperature', 0),
            "n": api_params.get('n', 1),
        }

        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            response_json = response.json()
            answer = response_json["choices"][0]["message"]["content"].strip()
            return answer
        else:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return ""
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return ""


def evaluate_candidate(cv_summary, github_summary, api_params):
    prompt = EVALUATE_CANDIDATE_PROMPT(cv_summary, github_summary)

    payload = {
        "model": models['language_model'],
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": api_params['max_tokens'],
        "temperature": api_params.get('temperature', 0),
        "n": api_params.get('n', 1),
    }

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        response_json = response.json()
        evaluation = response_json["choices"][0]["message"]["content"].strip()
        return evaluation
    else:
        logger.error(f"API request failed with status code {response.status_code}: {response.text}")
        return "Evaluation could not be generated."
