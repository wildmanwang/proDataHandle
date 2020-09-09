# -*- coding:utf-8 -*-
"""
"""
__author__ = "Cliff.wang"
import pymysql
pymysql.version_info = (1, 4, 13, "final", 0)
pymysql.install_as_MySQLdb()
import decimal      #打包需要

class MYSQL:
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.password = pwd
        self.db = db

    def GetConnect(self):
        if not self.db:
            raise Exception("没有配置数据库信息")
        conn = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.db, charset="utf8")
        if not conn:
            raise Exception("数据库[{server}][{db}]连接失败".format(server=self.host, db=self.db))
        else:
            return conn

    def __GetCursor(self):
        if not self.db:
            raise Exception("没有配置数据库信息")
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.db, charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise Exception("数据库[{server}][{db}]连接失败".format(server=self.host, db=self.db))
        else:
            return cur

    def ExecQuery(self, sql):
        cur = self.__GetCursor()
        cur.execute(sql)
        resList = cur.fetchall()

        self.conn.close()
        return resList

    def ExecNonQuery(self, sql):
        cur = self.__GetCursor()
        cur.execute(sql)

        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    if 1 == 2:
        ms = MSSQL(host="192.168.3.208", user="sa", pwd="0Wangle?", db="InterTest")
        lsSql = r"create table interTmp ( app_billno varchar(50) primary key )"
        ms.ExecNonQuery(lsSql)
