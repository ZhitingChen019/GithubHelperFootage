import logging
import os
import subprocess

from GitError import GitError


def mkdir_if_missing(path):
    logging.warning('目录 %s 缺失，尝试进行创建', path)
    if not os.path.exists(path):
        os.makedirs(path)


def check_local_branch(local_repo,branch_name):
    """检查本地是否存在指定分支"""
    try:
        result = subprocess.run(
            ["git", "branch", "--list", branch_name],
            cwd=local_repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.CalledProcessError as e:
        logging.error('分支检查失败，退出程序')
        raise GitError("git", "branch", "--list " + branch_name)
    return branch_name in result.stdout
