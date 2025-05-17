import logging
import os

from git import Repo
from github import Github, Organization, Repository

import src.config as config


def clone_repo(repo_url: str , destination_directory: str) -> None:
    logging.info(f"Cloning {repo_url}...")

    try:
        Repo.clone_from(repo_url, destination_directory)
    except Exception as e:
        logging.error(f"Failed to clone. Error {e}.")

def pull_repo(repo_path: str, 
              remote: str = "origin", 
              branch: str = "main") -> None:
    logging.info(f"Pulling {repo_path}...")

    try:
        Repo(repo_path).remotes[remote].pull(branch)
    except Exception as e:
        logging.error(f"Failed to pull. Error {e}.")

def get_org_repo_urls(org_name: str, token: str) -> list[str] | None:
    logging.info("Getting repository URLs...")

    try:
        g: Github = Github(token)
        org: Organization.Organization = g.get_organization(org_name)
        
        repo: Repository.Repository
        repo_urls: list[str] = [repo.html_url for repo in org.get_repos()]

        return repo_urls
    except Exception as e:
        logging.error(f"Failed to get repository URLs. Error {e}.")
        return None
    
def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=f"{config.LOG_FILE_NAME}"
    )

    userprofile: str | None = os.environ.get("USERPROFILE")

    if userprofile:
        local_directory: str = os.path.join(userprofile, 
                                            "Documents", 
                                            "UiPath Projects")

        if config.GITHUB_ORG_NAME is not None and config.GITHUB_TOKEN is not None:
            repo_urls: list[str] | None = get_org_repo_urls(config.GITHUB_ORG_NAME, 
                                                            config.GITHUB_TOKEN)

        if repo_urls is not None:
            repo_url: str
            for repo_url in repo_urls:
                destination_folder: str = repo_url.split("/")[-1]

                destination_directory: str = os.path.join(local_directory, 
                                                        destination_folder)

                if os.path.exists(destination_directory):
                    pull_repo(destination_directory)
                else:
                    os.makedirs(destination_directory)
                    clone_repo(repo_url, destination_directory)

if __name__ == "__main__":
    main()