import datetime
import json
import logging
import os
import shutil
import subprocess
import utils
from GitError import GitError
from PullRequestInfo import PullRequestInfo


class GitClient:
    """
    Git 操作客户端类，用于实际执行 Git 操作
    """

    def __init__(self, username, local_repo_path):
        self.username = username
        self.local_repo_path = local_repo_path
        self.upstream_remote_repo = None
        self.remote_my_repo = None
        self.local_commit_file_path_list = None
        self.remote_directory_path_list = None
        self.remote_commit_file_name_list = None

    def set_upstream_remote_repo(self, upstream_remote_repo_name):
        """
        设置主要远程仓库，用于与最新分支同步
        :param upstream_remote_repo_name: 主要远程仓库名
        :return: 
        """
        self.upstream_remote_repo = upstream_remote_repo_name

    def set_my_repo(self, my_repo_name):
        """
        设置自己的远程仓库
        :param my_repo_name: 自己的远程仓库名
        :return:
        """
        self.remote_my_repo = my_repo_name

    def set_commit_files(self, local_commit_file_path_list,
                         remote_directory_path_list, remote_commit_file_name_list):
        """
        设置需要进行自动化提交的文件
        :param local_commit_file_path_list: 提交文件的本地地址
        :param remote_directory_path_list: 对应文件在目标仓库的目录的相对地址
        :param remote_commit_file_name_list: 远程文件名
        """
        self.local_commit_file_path_list = local_commit_file_path_list
        self.remote_directory_path_list = remote_directory_path_list
        self.remote_commit_file_name_list = remote_commit_file_name_list

    def do_sync_local_with_remote(self):
        """
        将本地 main 分支与远程仓库同步
        """
        remote_name = self.upstream_remote_repo
        try:
            subprocess.run(['git', 'checkout', 'main'], cwd=self.local_repo_path, check=True)
            logging.info("执行从 主仓库 远程拉取 git fetch")
            subprocess.run(['git', 'fetch', remote_name], cwd=self.local_repo_path, check=True)
            logging.info("执行从 主仓库 与本地的合并操作")
            subprocess.run(['git', 'pull', remote_name, 'main'], cwd=self.local_repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logging.error("尝试与远程仓库同步时发生错误！返回码：%d 错误信息：%s", e.returncode, e.stderr)
            raise GitError("pull", remote_name + " main") from e
        logging.info("Git 同步完成")

    def do_sync_my_repo_with_remote(self):
        """
        保证自己的仓库也是最新状态
        """
        logging.info("开始将自己的仓库与主仓库同步")
        try:
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=self.local_repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logging.error("尝试将自己的仓库与远程仓库同步时发生错误！返回码：%d 错误信息：%s", e.returncode, e.stderr)
            raise GitError("push", self.remote_my_repo + " main") from e
        logging.info("自己的仓库同步完成")

    def generate_new_branch_name(self, file_type="doc"):
        """
        根据用户输入或文件名自动生成一个有意义的分支名，若有多个文件更新取第一个文件名
        :param file_type:更改的文件类型，默认为 doc
        :return:生成的分支名称
        """
        current_date = datetime.date.today()
        formatted_date = current_date.strftime("%Y%m%d")

        file_name = self.remote_commit_file_name_list[0]

        new_branch_name = file_type + "/update-" + file_name + "-" + formatted_date

        return new_branch_name

    def add_local_commit(self):
        """
        遍历文件列表，先将文件复制到本地仓库目录，然后尝试 git add
        :return:
        """
        global path_of_file_to_add
        for idx in range(len(self.local_commit_file_path_list)):
            # 提交所需的本地文件地址，相对仓库地址，提交文件名
            local_commit_file_path = self.local_commit_file_path_list[idx]
            remote_directory_path = self.remote_directory_path_list[idx]
            remote_commit_file_name = self.remote_commit_file_name_list[idx]

            try:
                local_repo_file_path = str(os.path.join(self.local_repo_path, remote_directory_path))
                utils.mkdir_if_missing(local_repo_file_path)

                path_of_file_to_add = str(os.path.join(local_repo_file_path, remote_commit_file_name))
                shutil.copy(local_commit_file_path, path_of_file_to_add)
            except FileNotFoundError as e:
                logging.error("文件未找到错误: %s", e.strerror)

            self.do_add(path_of_file_to_add)

    def do_add(self, file_path):
        """
        实际执行 git add 的函数
        :param file_path: 待提交的文件绝对地址
        """
        if not os.path.exists(file_path):
            logging.error("待提交的文件不存在: %s", file_path)
            return
        try:
            subprocess.run(['git', 'add', file_path], cwd=self.local_repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logging.error("尝试执行 git add 时发生错误！返回码：%d 错误信息：%s", e.returncode, e.stderr)
            raise GitError("add", "file_path")
        logging.info("git add 成功")

    def do_commit(self, commit_message):
        """
        实际执行 git commit 的函数
        :param commit_message: 提交的信息
        """
        logging.info("进行 git commit")
        try:
            subprocess.run(['git', 'commit', '-m', commit_message], cwd=self.local_repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logging.error("尝试执行 git commit 时发生错误！返回码：%d 错误信息：%s", e.returncode, e.stderr)
            raise GitError("commit", "-m " + commit_message)
        logging.info("git commit 成功")

    def do_push_to_my_repo(self, branch_name):
        """
       实际执行 git push 的语句，防止污染主要仓库，总是推送到我的仓库
       :param branch_name: 分支名
       """
        logging.info("进行 git push 到%s,分支名 :%s", self.remote_my_repo, branch_name)
        try:
            subprocess.run(['git', 'push', '-u', self.remote_my_repo, branch_name], cwd=self.local_repo_path,
                           check=True)
        except subprocess.CalledProcessError as e:
            logging.error("尝试执行 git push 时发生错误！返回码：%d 错误信息：%s", e.returncode, e.stderr)
            raise GitError("push", "-u " + self.remote_my_repo + " " + branch_name)
        logging.info("git push 成功")

    def do_create_pull_request(self, pull_request_info: PullRequestInfo):
        """
        实际执行 pr create 的语句
        :param pull_request_info: PullRequestInfo 结构体
        :return:
        """
        logging.info("执行 pr create")
        try:
            res = subprocess.run(['gh', 'pr', 'create', '--repo', pull_request_info.repo,
                                  '--base', pull_request_info.base,
                                  '--head', pull_request_info.head,
                                  '--title', pull_request_info.title,
                                  '--body', pull_request_info.body], cwd=self.local_repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logging.error("尝试执行 git push 时发生错误！返回码：%d 错误信息：%s", e.returncode, e.stderr)
            raise GitError("pr create", json.dumps(pull_request_info.__dict__))
        logging.info("pr create 成功")
        logging.info("pr url 是%s ", res.stdout.strip())
        print("新的 pr url: %s", res.stdout.strip())

    def do_create_branch(self, branch_name):
        """
        为 main 创建指定名称的分支
        :param branch_name: 分支名
        """
        logging.info("执行分支创建git checkout：%s", branch_name)
        try:
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.local_repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logging.error("尝试执行 git checkout 时发生错误！返回码：%d 错误信息：%s", e.returncode, e.stderr)
            raise GitError("git checkout", "-b " + branch_name)
        logging.info("分支 %s 创建成功", branch_name)
