import argparse
import base64
import logging
import os
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from github import Github, Organization

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s %(levelname)s "
        "[%(message)s] (%(filename)s "
        "| %(funcName)s | line %(lineno)d)"),
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("app.log"), 
              logging.StreamHandler(sys.stdout)])

import src.config

logger: logging.Logger = logging.getLogger(__name__)


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
                    logger.error("An error occurred during the "
                        f"execution of main.py.\nError message: {e}")
                    if attempt >= max_retries:
                        if retry_raise_exception:
                            raise
                        return None
                    time.sleep(retry_interval_seconds)
        return wrapper
    return decorator

def clone_repo(token: str, 
               repo_url: str, 
               destination_folder_path: str) -> None:
    logger.info(f"Cloning {repo_url}...")

    try:
        credentials = base64.b64encode(
            f"x-access-token:{token}".encode()).decode()
        
        subprocess.run(
            [
                "git",
                "-c",
                f"http.extraheader=Authorization: Basic {credentials}",
                "clone",
                repo_url,
                destination_folder_path
            ],
            check=True
        )

    except Exception as e:
        logger.error(f"Failed to clone.\nError message: {e}")

def pull_repo(token: str,
              folder_path: str,
              remote: str = "origin", 
              branch: str = "main") -> None:
    logger.info(f"Pulling {folder_path}...")

    try:
        credentials = base64.b64encode(
            f"x-access-token:{token}".encode()).decode()
        
        subprocess.run(
            [
                "git",
                "-c",
                f"http.extraheader=Authorization: Basic {credentials}",
                "pull",
                remote,
                branch
            ],
            cwd=folder_path,
            check=True
        )
    except Exception as e:
        logger.error(f"Failed to pull.\nError message: {e}")

def get_org_repo_urls(org: str, token: str) -> list[str] | None:
    logger.info("Getting repository URLs...")

    try:

        github: Github = Github(token)
        github_org: Organization.Organization = github.get_organization(org)
        
        repo_urls: list[str] = [repo.html_url 
                                for repo in github_org.get_repos()]

        return repo_urls

    except Exception as e:
        logger.error("Failed to get organization repository urls."
                     f"\nError message: {e}")
        return None
    
def _bootstrap() -> dict[str, str | None]:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description="clone-github-org-repo")

    parser.add_argument("--dotenv_path",
                        type=str,
                        default="",
                        help="The file path of .env")
    
    parser.add_argument("--github_org",
                        type=str,
                        default="",
                        help="GitHub Organization"
                        )
    
    parser.add_argument("--github_token",
                        type=str,
                        default="",
                        help="GitHub Token")

    args: argparse.Namespace = parser.parse_args()

    config: dict[str, str | None] = src.config.load_config(args.dotenv_path)

    config["github_org"] = args.github_org
    config["github_token"] = args.github_token

    return config
    
def main() -> None:

    config: dict[str, str | None] = _bootstrap()

    logger.info("Running...")

    max_retries: int = int(config.get("MAX_RETRIES") or 0)
    retry_interval_seconds: int = int(config.get("RETRY_INTERVAL_SECONDS") 
                                      or 0)
    retry_raise_exception: bool = config.get("RETRY_RAISE_EXCEPTION", 
                                             "True") in ["True", "true"]

    @retry(max_retries, retry_interval_seconds, retry_raise_exception)
    def run() -> None:
        if config["DESTINATION_FOLDER_NAME"] is None:
            raise ValueError("Destination folder name is empty.")

        userprofile: str | None
        if userprofile:= os.getenv("USERPROFILE"):
            local_directory: str = os.path.join(
                userprofile, 
                "Documents", 
                config["DESTINATION_FOLDER_NAME"])
            
            if config["github_org"] and config["github_token"]:
                repo_urls: list[str] | None = get_org_repo_urls(
                    config["github_org"], 
                    config["github_token"])

                if repo_urls is not None:
                    for repo_url in repo_urls:
                        repo_folder_name: str = repo_url.split("/")[-1]

                        repo_folder_path: Path = (Path(local_directory) 
                                                  / repo_folder_name)

                        if (repo_folder_path.exists() 
                            and any(repo_folder_path.iterdir())):
                            pull_repo(config["github_token"],
                                      str(repo_folder_path))
                        else:
                            os.makedirs(repo_folder_path)
                            repo_folder_path.mkdir(parents=True, 
                                                   exist_ok=True)
                            clone_repo(config["github_token"],
                                       repo_url, 
                                       str(repo_folder_path))
    run()

if __name__ == "__main__":
   main()