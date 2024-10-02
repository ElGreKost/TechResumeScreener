# clone_repo.py
from git import Repo, GitCommandError
import os
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clone_github_repo(github_url, local_path='cloned_repo'):
    if os.path.exists(local_path):
        try:
            shutil.rmtree(local_path)
            logger.info(f"Removed existing directory {local_path}")
        except Exception as e:
            logger.error(f"Failed to remove existing directory {local_path}: {e}")
            return None
    try:
        Repo.clone_from(github_url, local_path)
        logger.info(f"Cloned repository {github_url} to {local_path}")
        return local_path
    except GitCommandError as e:
        logger.error(f"Git command error while cloning {github_url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error cloning repository {github_url}: {e}")
        return None
