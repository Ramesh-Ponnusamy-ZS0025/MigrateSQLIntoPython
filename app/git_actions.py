import os
from git import Repo
from .models import GitRepository
from app import db
import shutil

def push_to_git(database_id,files_to_commit):
    try:
        commit_message='Commit from Agile Architects'
        local_repo_path= 'C:\\workspace'

        git_repo_details = db.session.query(GitRepository).filter(GitRepository.database_id == database_id).first()

        local_repo_path_ = os.path.join(local_repo_path, git_repo_details.repo_name)
        username =git_repo_details.username
        token = git_repo_details.token
        repo_path = git_repo_details.repo_path #'https://github.com/M-Revathy/test'
        repo_ = repo_path.split(':')[1].replace('//', '')
        # Clone the repository if it doesn't exist
        if not os.path.exists(local_repo_path_):
            repo_url = f'https://{username}:{token}@{repo_}'
            repo = Repo.clone_from(repo_url, local_repo_path_)
        else:
            repo = Repo(local_repo_path_)

        remote_repo = f'https://{username}:{token}@{repo_}'
        print(remote_repo)

        git = repo.git
        branches = repo.git.branch('-a')
        print("Branches available:", branches)

        # Checkout to the target branch
        repo.git.checkout(git_repo_details.branch_name)
        moved_files = []
        for file in files_to_commit:
            filename = os.path.basename(file)
            shutil.copy(file, local_repo_path_)
            destination_path = os.path.join(local_repo_path_, filename)
            moved_files.append(destination_path)
            # print('moved_files',moved_files)


        # Add files to the staging area
        repo.index.add(moved_files)

        # Commit the changes
        repo.index.commit(commit_message)

        # Push the changes
        repo.remote(name='origin').push(git_repo_details.branch_name)
        print("Files committed and pushed successfully!")
        return 'Success'
    except Exception as e:
        raise e
        print('Failed while push to git ',e)
        return 'Failed'

