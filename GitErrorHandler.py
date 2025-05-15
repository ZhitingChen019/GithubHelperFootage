import logging
import subprocess

from GitError import GitError


class GitErrorHandler:
    """
    Git 错误处理类，用于根据错误的操作和参数执行相应函数
    """

    def __init__(self, work_dir):
        self.work_dir = work_dir

    def handle_error(self, error: GitError) -> None:
        if error.git_ops == "_commit":
            logging.warning("检测 commit 失败，准备回滚")
            rollback_success = self.try_rollback()
            if rollback_success:
                logging.warning("回滚成功")


    def try_rollback(self) -> bool:
        try:
            subprocess.run(["git", "reset", "--soft", "HEAD~1"], cwd=self.work_dir, check=True)
        except subprocess.CalledProcessError as e:
            logging.error("回滚失败，请手动回滚,错误信息:%s", e)
            return False
        return True
