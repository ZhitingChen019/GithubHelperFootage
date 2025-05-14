import logging
import os


def mkdir_if_missing(path):
    logging.warning('目录 %s 缺失，尝试进行创建',path)
    if not os.path.exists(path):
        os.makedirs(path)