class PullRequestInfo:
    """
    PR 信息实体类
    """
    def __init__(self, repo, base, head, title, body):
        self._repo = repo
        self._base = base
        self._head = head
        self._title = title
        self._body = body
    def __str__(self):
        return (
            f"--repo {self._repo}\n"
            f"--base {self._base}\n"
            f"--head {self._head}\n"
            f"--title {self._title}\n"
            f"--body {self._body}\n"
        )

    # 使用 @property 装饰器生成 getter 方法
    @property
    def repo(self):
        return self._repo

    @property
    def base(self):
        return self._base

    @property
    def head(self):
        return self._head

    @property
    def title(self):
        return self._title

    @property
    def body(self):
        return self._body

