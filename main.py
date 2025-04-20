import logging

from git import Repo

import src.config as config


def clone_repo(repo_url: str , destination_directory: str) -> None:
    logging.info(f"Cloning {repo_url}")
    Repo.clone_from(repo_url, destination_directory)
    
def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=f"{config.LOG_FILE_NAME}"
    )

    repo_url: str = "https://github.com/ncgmyorg/sample.git"
    destination_directory: str = r"C:\Users\Nathaniel Gamo\Documents\Python Projects\sample"

    clone_repo(repo_url, destination_directory)

if __name__ == "__main__":
    main()