# main.py
import os
import sys
import time
import logging
import yaml

from GitClient import GitClient
from GitError import GitError
from GitErrorHandler import GitErrorHandler
from PullRequestInfo import PullRequestInfo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
GITHUB_USERNAME = ""
LOCAL_REPO_PATH = ""
git_error_handler = None
sys.stdout.reconfigure(line_buffering=True)


def write_config(config_file_path):
    data = {
        "github_username": "",
        "local_repo_path": ""
    }
    logging.warning("配置文件缺失，请重新输入配置信息。")
    github_username = input("请输入 github 用户名：\n").strip()
    local_repo_path = input("请输入本地仓库地址：\n").strip()
    data["github_username"] = github_username
    data["local_repo_path"] = local_repo_path

    with open(config_file_path, "w+", encoding="utf8") as config_file:
        yaml.dump(data, config_file, default_flow_style=False)
        logging.info("配置文件保存成功")

    return github_username, local_repo_path


def load_config(config_file_path="config.yaml"):
    global GITHUB_USERNAME
    global LOCAL_REPO_PATH
    global git_error_handler
    # 读取配置文件
    logging.info("载入配置文件");
    if not os.path.exists(config_file_path):
        logging.warning("配置文件不存在，重新创建配置文件")
        github_username, local_repo_path = write_config(config_file_path)
    else:
        with open(config_file_path, "r", encoding="utf8") as config_file:
            data = yaml.load(config_file, Loader=yaml.FullLoader)

        github_username = data["github_username"]
        local_repo_path = data["local_repo_path"]

        if github_username is None or local_repo_path is None:
            github_username, local_repo_path = write_config(config_file_path)

    GITHUB_USERNAME = github_username
    LOCAL_REPO_PATH = local_repo_path
    git_error_handler = GitErrorHandler(LOCAL_REPO_PATH)
    logging.info("获取配置成功")


def try_commit():
    success = True

    local_commit_file_path_list = []
    remote_directory_path_list = []
    remote_file_name_list = []

    first_input = True

    while True:
        if first_input:
            first_input = False
        else:
            continue_input = input("是否继续输入？(y/n): \n").strip().lower()

            # 检查用户是否想停止
            if continue_input == 'n':
                break

        # 收集文件信息
        local_commit_file_path = input("请输入待提交文件地址: \n")
        remote_directory_path = input("请输入文件在 apache/cloudberry-site 仓库结构中的目标相对路径: \n")
        remote_file_name = input("请输入在远程目录中使用的名字: \n")

        local_commit_file_path_list.append(local_commit_file_path)
        remote_directory_path_list.append(remote_directory_path)
        remote_file_name_list.append(remote_file_name)

    # 执行 git 操作
    # 设置所需参数
    git_client = GitClient(GITHUB_USERNAME, LOCAL_REPO_PATH)
    git_client.set_my_repo('origin')
    git_client.set_upstream_remote_repo('upstream')
    git_client.set_commit_files(local_commit_file_path_list, remote_directory_path_list, remote_file_name_list)

    try:
        # 与远程仓库同步
        git_client.do_sync_local_with_remote()
        git_client.do_sync_my_repo_with_remote()
        # 生成新分支名
        branch_name = git_client.generate_new_branch_name()
        git_client.do_create_branch(branch_name)
        logging.info("生成新分支名：%s", branch_name)
        # 尝试进行提交

        git_client.add_local_commit()
        # 进行提交和推送
        commit_message = input("输入当前 commit 的描述，遵循 \"docs: Add X documentation for Y feature\" 的格式: \n")
        git_client.do_commit(commit_message)
        git_client.do_push_to_my_repo(branch_name)
        # 创建 pr 并尝试合并
        pr_title = input("输入当前 pr 的标题: \n").strip()
        pr_body = input("输入当前 pr 的描述: \n").strip()
        pull_request_info = PullRequestInfo(
            "apache/cloudberry-site",
            'main',
            GITHUB_USERNAME + ":" + branch_name,
            pr_title,
            pr_body

        )

        git_client.do_create_pull_request(pull_request_info)
    except FileNotFoundError as e:
        logging.error("发生文件未找到错误:%s", e)
        return False
    except GitError as e:
        logging.error("发生 Git 错误:%s", e)
        git_error_handler.handle_error(e)
        return False
    except Exception as e:
        logging.error("发生未知错误:%s", e)
        return False

    return success


def main():
    # 读取配置文件
    load_config("config.yaml")

    # 交互确定待提交本地文件和远程文件
    logging.info("进行 git 提交流程")
    success = try_commit()
    if not success:
        logging.error("尝试提交失败")
    else:
        logging.info("提交成功")


if __name__ == "__main__":
    main()
