# -*- coding:utf-8 -*-
"""
"""
__author__ = "Cliff.wang"
import configparser
import logging
import os

class Settings():

    def __init__(self, path, file):
        self.path = path

        self.logger = self._getLogger()

        config = configparser.ConfigParser()
        config.read(os.path.join(path, file), encoding="utf-8")

        # 单据端数据库连接
        self.dbOrderHost = config.get("orders", "host")
        self.dbOrderUser = config.get("orders", "user")
        self.dbOrderPassword = config.get("orders", "password")
        self.dbOrderDatabase = config.get("orders", "database")

        # 服务端数据库连接
        self.dbServiceHost = config.get("service", "host")
        self.dbServiceUser = config.get("service", "user")
        self.dbServicePassword = config.get("service", "password")
        self.dbServiceDatabase = config.get("service", "database")

        # 业务参数
        self.commentHours = config.getint("business", "commentHours")
        self.workInterval = config.getint("business", "workInterval")

        # 状态
        self.run = True
        self.processing = False

    def _getLogger(self):
        logger = logging.getLogger("[DataInterCatering]")
        handler = logging.FileHandler(os.path.join(self.path, "service.log"))
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        return logger

if __name__ == "__main__":
    i = 1
    i += 1
