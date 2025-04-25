import logging
import os

from git import Repo

import src.config as config


def clone_repo(repo_url: str , destination_directory: str) -> None:
    logging.info(f"Cloning {repo_url}")
    Repo.clone_from(repo_url, destination_directory)

def pull_repo(repo_path: str, 
              remote: str = "origin", 
              branch: str = "main") -> None:
    logging.info(f"Pulling {repo_path}")
    try:
        Repo(repo_path).remotes[remote].pull(branch)
    except Exception as e:
        logging.error(f"Failed to pull. Error {e}.")
    
def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=f"{config.LOG_FILE_NAME}"
    )

    repo_url: str = "https://github.com/ncgmyorg/sample.git"
    destination_folder: str = repo_url.split("/")[-1].replace(".git", "")
    local_directory: str = os.path.join(os.environ.get("USERPROFILE"), "Documents", "Python Projects")
    destination_directory: str = os.path.join(local_directory, destination_folder)

    if os.path.exists(destination_directory):
        pull_repo(destination_directory)
    else:
        os.makedirs(destination_directory)
        clone_repo(repo_url, destination_directory)

if __name__ == "__main__":
    main()