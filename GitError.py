class GitError(Exception):
    """
    Git 错误类，用于保存 Git 错误信息
    包括使用的 git 客户端，git 指令，git 操作等
    """
    def __init__(self,client,git_ops,git_args):
        self.client = client
        self.git_ops = git_ops
        self.git_args = git_args

    def __str__(self):
        return f"发生错误的 git 命令: {self.client} {self.git_ops} {self.git_args}"