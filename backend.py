# backend.py
import logging
from cv_processing import process_cv
from github_analysis import extract_github_links, analyze_github_repos
from openai_interaction import evaluate_candidate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_resume(cv_file_path, api_params):
    # Read file bytes
    try:
        with open(cv_file_path, 'rb') as f:
            file_bytes = f.read()
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        return "Failed to read the uploaded file."

    # Process the CV
    extracted_info, cv_summary, hyperlinks = process_cv(file_bytes, api_params)

    # Extract GitHub links from the extracted information and hyperlinks
    cv_text = cv_summary
    github_links = extract_github_links(cv_text, hyperlinks)

    # Analyze GitHub repositories if any
    github_summaries = []
    if github_links:
        repo_summaries = analyze_github_repos(github_links, api_params)
        # Generate a combined GitHub summary
        for repo in repo_summaries:
            if repo.get('summary'):
                github_summaries.append(repo['summary'])
    else:
        repo_summaries = []

    combined_github_summary = " ".join(github_summaries)

    # Evaluate the candidate
    evaluation = evaluate_candidate(cv_summary, combined_github_summary, api_params)

    # Compile the final report
    report = f"## **Candidate Summary:**\n{cv_summary}\n\n"

    if repo_summaries:
        report += "## **GitHub Repository Analysis:**\n"
        for repo in repo_summaries:
            report += f"- **Repository Name:** [{repo['repo_name']}]({repo['repo_url']})\n"
            report += f"  **Summary:**\n{repo['summary']}\n\n"
    else:
        report += "## **GitHub Repository Analysis:**\nNo GitHub repositories found or analyzed.\n\n"

    report += f"## **Candidate Evaluation:**\n{evaluation}\n"

    return report
