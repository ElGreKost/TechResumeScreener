# app.py
import gradio as gr
import logging
import yaml

from backend import process_resume

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def process_resume_ui(cv_file_path, temperature, max_tokens):
    if not cv_file_path:
        return "Please upload a CV PDF file."

    # Prepare API parameters
    api_params = {
        'temperature': temperature,
        'max_tokens': max_tokens,
        'n': config['api_params'].get('n', 1),
    }

    # Notify the user about processing time
    processing_message = "Processing the resume and analyzing all GitHub repositories. This may take several minutes depending on the number of repositories and their sizes."

    # Process the resume
    report = process_resume(cv_file_path, api_params)
    return f"{processing_message}\n\n{report}"

iface = gr.Interface(
    fn=process_resume_ui,
    inputs=[
        gr.File(type='filepath', label="Upload CV PDF"),
        gr.Slider(minimum=0.0, maximum=1.0, step=0.1, value=config['api_params']['temperature'], label="Temperature"),
        gr.Slider(minimum=100, maximum=2000, step=100, value=config['api_params']['max_tokens'], label="Max Tokens")
    ],
    outputs="markdown",
    title="Resume Screener",
    description="Upload a candidate's CV in PDF format to generate a summary, analyze GitHub repositories, and evaluate the candidate.",
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch(debug=True, share=True)
