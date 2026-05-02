import argparse
import logging
import os
import time
from typing import Any, Callable

from git import Repo
from github import Github, Organization, Repository

import src.config


def retry(max_retries: int = 3, 
          retry_interval_seconds: int = 0, 
          retry_raise_exception: bool = True) -> (Callable[..., 
                                                           Callable[..., 
                                                                    Any]]):
    def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    logging.error("An error occurred during the "
                        f"execution of main.py.\nError message: {e}")
                    if attempt >= max_retries:
                        if retry_raise_exception:
                            raise
                        return None
                    time.sleep(retry_interval_seconds)
        return wrapper
    return decorator

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
    
def _bootstrap() -> dict[str, str | None]:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description="clone-github-org-repo")

    parser.add_argument("--dotenv_path",
                        type=str,
                        default="",
                        help="The file path of .env.")
    
    parser.add_argument("github_org",
                        type=str,
                        # default=None,
                        # nargs="?",
                        help="GitHub Organization"
                        )
    
    parser.add_argument("github_token",
                        type=str,
                        # default=None,
                        # nargs="?",
                        help="GitHub Token")

    args: argparse.Namespace = parser.parse_args()

    config: dict[str, str | None] = src.config.load_config(args.dotenv_path)

    log_file_path: str = "app.log"
    if "LOG_FILE_PATH" in config:
        if config["LOG_FILE_PATH"]:
            log_file_path = config["LOG_FILE_PATH"]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=log_file_path
    )

    config["github_org"] = args.github_org
    config["github_token"] = args.github_token

    return config
    
def main() -> None:

    config: dict[str, str | None] = _bootstrap()

    logging.info("Running...")

    max_retries: int = 0
    if "MAX_RETRIES" in config:
        if config["MAX_RETRIES"]:
            max_retries = int(config["MAX_RETRIES"])

    retry_interval_seconds: int = 0
    if "RETRY_INTERVAL_SECONDS" in config:
        if config["RETRY_INTERVAL_SECONDS"]:
            retry_interval_seconds = int(config["RETRY_INTERVAL_SECONDS"])

    retry_raise_exception: bool = True
    if "RETRY_RAISE_EXCEPTION" in config:
        if config["RETRY_RAISE_EXCEPTION"]:
            retry_raise_exception = (config["RETRY_RAISE_EXCEPTION"].lower() 
                                     == "true")

    @retry(max_retries, retry_interval_seconds, retry_raise_exception)
    def run() -> None:
        logging.info("Executing main.py...")
        
        if config["DESTINATION_FOLDER_NAME"] is None:
            raise ValueError("Destination folder name is empty.")

        userprofile: str | None
        if userprofile:= os.getenv("USERPROFILE"):
            local_directory: str
            
            local_directory= os.path.join(userprofile, 
                                          "Documents", 
                                          config["DESTINATION_FOLDER_NAME"])
            
            if config["github_org"] and config["github_token"]:
                repo_urls: list[str] | None = get_org_repo_urls(
                    config["github_org"], config["github_token"])

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
    run()

if __name__ == "__main__":
   main()