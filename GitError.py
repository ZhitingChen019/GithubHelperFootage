class GitError(Exception):
    """
    Git 错误类，用于保存 Git 错误信息
    """
    def __init__(self,git_ops,git_args):
        self.git_ops = git_ops
        self.git_args = git_args

    def __str__(self):
        return f"错误时 git 操作: {self.git_ops}, git 参数: {self.git_args}"