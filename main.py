import argparse
import logging
import os
import time
from typing import Any, Callable

from git import Repo
from github import Github, Organization, Repository

import src.config as config


def retry(function: Callable[[argparse.Namespace], None]) -> Callable[..., 
                                                                      None]:
    def wrapper(*args: Any, **kwargs: Any) -> None:
        retry_count: int = 0
        while True:
            try:
                function(*args, **kwargs)
                break
            except Exception as e:
                logging.error("An error occurred during the "
                      f"execution of main.py.\nError message: {e}")
                if retry_count >= config.MAX_RETRIES:
                    break
                retry_count += 1
                time.sleep(config.RETRY_INTERVAL_SECONDS)
    return wrapper

def clone_repo(repo_url: str , destination_directory: str) -> None:
    logging.info(f"Cloning {repo_url}...")

    try:
        Repo.clone_from(repo_url, destination_directory)
    except Exception as e:
        logging.error(f"Failed to clone.\nError message: {e}")

def pull_repo(repo_path: str, 
              remote: str = "origin", 
              branch: str = "main") -> None:
    logging.info(f"Pulling {repo_path}...")

    try:
        Repo(repo_path).remotes[remote].pull(branch)
    except Exception as e:
        logging.error(f"Failed to pull.\nError message: {e}")

def get_org_repo_urls(org: str, token: str) -> list[str] | None:
    logging.info("Getting repository URLs...")

    try:
        github: Github = Github(token)
        github_org: Organization.Organization = github.get_organization(org)
        
        repo: Repository.Repository
        repo_urls: list[str] = [repo.html_url for repo in 
                                github_org.get_repos()]

        return repo_urls
    except Exception as e:
        logging.error(f"Failed to get repository URLs.\nError message: {e}")
        return None
    
def main(args: argparse.Namespace) -> None:
    try:
        logging.info("Executing main.py...")

        if args.github_org is None or args.github_token is None:
            raise ValueError("GitHub Organization Name "
                             "or GitHub Token is empty.")
        
        if config.DESTINATION_FOLDER_NAME is None:
            raise ValueError("Destination folder name is empty.")

        userprofile: str | None
        if userprofile:= os.getenv("USERPROFILE"):
            local_directory: str = os.path.join(userprofile, 
                                                "Documents", 
                                                config.DESTINATION_FOLDER_NAME)
            
            repo_urls: list[str] | None = get_org_repo_urls(
                args.github_org, args.github_token)

            if repo_urls is not None:
                repo_url: str
                for repo_url in repo_urls:
                    destination_folder: str = repo_url.split("/")[-1]
                    
                    destination_directory: str = os.path.join(
                        local_directory, destination_folder)

                    if os.path.exists(destination_directory):
                        pull_repo(destination_directory)
                    else:
                        os.makedirs(destination_directory)
                        clone_repo(repo_url, destination_directory)
        
    except Exception as e:
        logging.error(f"An error occurred during the "
                      f"execution of main.py.\nError message: {e}")

if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="download-github-repositories")
    
    parser.add_argument("--dotenv_path",
                        type=str,
                        help="The file path of .env.")
    
    parser.add_argument("github_org",
                        type=str,
                        default=None,
                        nargs="?",
                        help="GitHub Organization"
                        )
    
    parser.add_argument("github_token",
                        type=str,
                        default=None,
                        nargs="?",
                        help="GitHub Token")
    
    args: argparse.Namespace = parser.parse_args()

    if args.dotenv_path:
        config.call_load_dotenv(args.dotenv_path)
    else:
        config.call_load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=f"{config.LOG_FILE_PATH}"
    )

    main(args)