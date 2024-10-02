# github_analysis.py
import os
import re
import requests
from urllib.parse import urlparse
from clone_repo import clone_github_repo
from process_files import read_code_files
from openai_interaction import ask_question_about_code
import shutil
import logging
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

github_analysis_config = config.get('github_analysis', {})
max_repos = github_analysis_config.get('max_repos', None)  # Set to None to process all repositories
max_repo_size_mb = github_analysis_config.get('max_repo_size_mb', None)  # Max size in MB
exclude_forks = github_analysis_config.get('exclude_forks', True)

def extract_github_links(text, hyperlinks):
    """
    Extract GitHub links from both text and hyperlinks.
    """
    github_links = []

    # Extract from text using regex
    pattern = r'(https?://github\.com/[\w\-]+(?:/[\w\-]+)?)'
    github_links_text = re.findall(pattern, text)
    github_links.extend(github_links_text)

    # Extract from hyperlinks
    for link in hyperlinks:
        if 'github.com' in link.lower():
            github_links.append(link)

    # Remove duplicates
    github_links = list(set(github_links))

    return github_links

def analyze_github_repos(github_links, api_params):
    repo_summaries = []
    for link in github_links:
        parsed_url = urlparse(link)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) == 1:
            # User profile link; get user's repositories
            username = path_parts[0]
            repos = get_all_user_repos(username)
            repos = filter_repositories(repos)
            repos_to_process = repos  # Process all filtered repositories
        elif len(path_parts) == 2:
            # Specific repository link
            username, repo_name = path_parts
            repos_to_process = [{'name': repo_name, 'html_url': link}]
        else:
            logger.warning(f"Invalid GitHub URL format: {link}")
            continue

        for repo in repos_to_process:
            repo_url = repo.get('html_url', '')
            repo_name = repo.get('name', '')
            if not repo_url or not repo_name:
                logger.warning(f"Invalid repository data: {repo}")
                continue
            local_path = os.path.join('temp_repos', username, repo_name)
            # Clone the repository
            repo_path = clone_github_repo(repo_url, local_path=local_path)
            if not repo_path:
                logger.error(f"Failed to clone repository: {repo_url}")
                continue
            # Read code files
            codebase_text = read_code_files(repo_path)
            if not codebase_text:
                logger.error(f"No code files found in repository: {repo_url}")
                # Clean up if no code was read
                shutil.rmtree(os.path.join('temp_repos', username), ignore_errors=True)
                continue
            # Ask OpenAI to generate a summary of the repository
            summary = ask_question_about_code(
                codebase_text,
                f"Please provide a summary of the repository '{repo_name}' focusing on technologies used, complexity, and relevance to Document Analysis and Recognition.",
                api_params
            )
            if summary:
                repo_summaries.append({
                    'repo_name': repo_name,
                    'repo_url': repo_url,
                    'summary': summary
                })
            else:
                logger.error(f"Failed to generate summary for repository: {repo_url}")
            # Clean up cloned repository after analysis
            shutil.rmtree(os.path.join('temp_repos', username), ignore_errors=True)
    return repo_summaries

def get_all_user_repos(username):
    repos = []
    page = 1
    per_page = 100  # Maximum allowed by GitHub API

    # Load GitHub access token from environment variables
    github_access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    headers = {}
    if github_access_token:
        headers['Authorization'] = f'token {github_access_token}'
    else:
        logger.warning("No GitHub access token found. API rate limits may be low.")

    while True:
        url = f'https://api.github.com/users/{username}/repos'
        params = {
            'per_page': per_page,
            'page': page,
            'type': 'owner',  # Only repositories owned by the user
            'sort': 'updated',  # Sort by last updated
            'direction': 'desc'
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 404:
                logger.error(f"User {username} not found.")
                break
            response.raise_for_status()
            page_repos = response.json()
            if not page_repos:
                break
            repos.extend(page_repos)
            page += 1
        except requests.RequestException as e:
            logger.error(f"Failed to fetch repositories for {username}: {e}")
            break
    return repos

def filter_repositories(repos):
    filtered_repos = []
    for repo in repos:
        # Exclude forks if specified
        if exclude_forks and repo.get('fork'):
            logger.info(f"Excluded forked repository: {repo.get('html_url')}")
            continue
        # Exclude repositories larger than max_repo_size_mb
        if max_repo_size_mb:
            repo_size_mb = repo.get('size', 0) / 1024  # Size is in MB
            if repo_size_mb > max_repo_size_mb:
                logger.info(f"Excluded large repository (>{max_repo_size_mb} MB): {repo.get('html_url')}")
                continue
        filtered_repos.append(repo)
    return filtered_repos
