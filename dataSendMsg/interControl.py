# -*- coding:utf-8 -*-
"""
数据对接控制类
"""
__author__ = "Cliff.wang"
from datetime import datetime, timedelta
from interMysql import MYSQL
import time
from interMsg import MsgJYKX

class InterControl():

    def __init__(self, sett):
        """
        接口控制类
        """
        self.sett = sett
        self.dbOrder = MYSQL(self.sett.dbOrderHost, self.sett.dbOrderUser, self.sett.dbOrderPassword, self.sett.dbOrderDatabase)
        self.dbService = MYSQL(self.sett.dbServiceHost, self.sett.dbServiceUser, self.sett.dbServicePassword, self.sett.dbServiceDatabase)
        self.sysParas = {}
        self.getSysParas()
        self.msgSrv = MsgJYKX()
        self.msgSrv.sysParas = self.sysParas

    def getSysParas(self):
        """
        获取系统参数
        """
        rtnData = {
            "result": False,  # 逻辑控制 True/False
            "info": "",  # 信息
            "dataString": "",  # 字符串
            "dataNumber": 0,  # 数字
            "entities": {}
        }
        ibConn = False
        try:
            conn = self.dbOrder.GetConnect()
            ibConn = True
            cur = conn.cursor()

            # 服务商标志
            lsSql = r"select paraValue from sys_paras where paraCode='{paraCode}'".format(paraCode="serviceFlag")
            cur.execute(lsSql)
            rsTmp = cur.fetchall()
            if len(rsTmp) > 0:
                self.sysParas["serviceFlag"] = rsTmp[0][0]
            else:
                self.sysParas["serviceFlag"] = ""

            # 错误日志接收者
            lsSql = r"select paraValue from sys_paras where paraCode='{paraCode}'".format(paraCode="errLogRecipient")
            cur.execute(lsSql)
            rsTmp = cur.fetchall()
            if len(rsTmp) > 0:
                lsTmp = rsTmp[0][0]
            else:
                lsTmp = ""
            self.sysParas["errLogRecipient"] = [int(i) for i in lsTmp.split(";")]
        finally:
            if ibConn:
                conn.close()
        return rtnData

    def dataHandle(self, storeID):
        """
        【任务策略】
            每日09:30启动任务
        :return:
        """
        rtnData = {
            "result": False,  # 逻辑控制 True/False
            "info": "",  # 信息
            "dataString": "",  # 字符串
            "dataNumber": 0,  # 数字
            "entities": {}
        }

        ibConnOrder = False
        ibConnService = False
        try:
            # 获取订单连接
            connOrder = self.dbOrder.GetConnect()
            ibConnOrder = True
            curOrder = connOrder.cursor()

            # 获取服务连接
            connService = self.dbService.GetConnect()
            ibConnService = True
            curService = connService.cursor()

            # 评价记录开始时间：今天-1
            sDate = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 60 * 60 * 24 * 1))
            timeCmt = int(time.mktime(time.strptime(sDate, "%Y-%m-%d")))

            # 逐个处理每个门店
            if storeID > 0:
                lsSql = r"select erpID, name, recipient, IFNULL(lastSend, ''), msgScore from store_info where erpID={storeID} and recipient>0".format(storeID=storeID)
            else:
                lsSql = r"select erpID, name, recipient, IFNULL(lastSend, ''), msgScore from store_info where status=1 and recipient>0 order by level"
            ldCol = ["storeID", "name", "recipient", "lastSend", "msgScore"]
            curOrder.execute(lsSql)
            rsTmp = curOrder.fetchall()
            rsStore = [dict(zip(ldCol, line)) for line in rsTmp]
            for rcStore in rsStore:
                if rcStore["msgScore"] <= 2:
                    msgFlag = "差评"
                elif rcStore["msgScore"] <= 3:
                    msgFlag = "中差评"
                else:
                    msgFlag = "评价"
                # 统计全部需通知评价数量
                lsSql = r"select count(erpID), sum(if(order_score <= {msgScore}, 1, 0)) from comment_main where storeID = {storeID} and comment_time >= {cmt_time}".format(
                    msgScore=rcStore["msgScore"],
                    cmt_time=timeCmt,
                    storeID=rcStore["storeID"]
                )
                curOrder.execute(lsSql)
                rsTmp = curOrder.fetchall()
                iCntAll = rsTmp[0][0]
                iCntBad = rsTmp[0][1]
                # 检索该门店待处理记录
                lsSql = r"select commentID, comment_time, order_score, pic_cnt, commentStr, orderNum, orderID, order_time, delivery_time, order_remark, sure_flag from business_notice " \
                        r"where comment_time >= {cmt_time} and storeID = {storeID} and order_score <= {msgScore} and status = 0 order by comment_time desc, commentID desc".format(
                    msgScore=rcStore["msgScore"],
                    cmt_time=timeCmt,
                    storeID=rcStore["storeID"]
                )
                ldCol = ["commentID", "comment_time", "order_score", "pic_cnt", "commentStr", "orderNum", "orderID", "order_time", "delivery_time", "order_remark", "sure_flag"]
                curService.execute(lsSql)
                rsTmp = curService.fetchall()
                rsMsg = [dict(zip(ldCol, line)) for line in rsTmp]
                msgPack = {}
                msgPack["commentID"] = 0
                msgs = []
                for msg in rsMsg:
                    if msg["commentID"] != msgPack["commentID"]:
                        if msgPack["commentID"] > 0:
                            msgs.append(msgPack)
                        msgPack = {
                            "commentID": msg["commentID"],
                            "comment_time": msg["comment_time"],
                            "order_score": msg["order_score"],
                            "pic_cnt": msg["pic_cnt"],
                            "commentStr": msg["commentStr"],
                            "orderList": [],
                            "sure_flag": msg["sure_flag"]
                        }
                    msgPack["orderList"].append({
                        "orderNum": msg["orderNum"],
                        "orderID": msg["orderID"],
                        "order_time": msg["order_time"],
                        "callbackTime": msg["delivery_time"] + 24 * 60 * 60,
                        "order_remark": msg["order_remark"]
                    })
                if msgPack["commentID"] > 0:
                    msgs.append(msgPack)
                # 发送消息
                if len(rsMsg) > 0 or len(rsMsg) == 0 and iCntAll > 0 and sDate > rcStore["lastSend"]:
                    for reci in rcStore["recipient"].split(";"):
                        rtnData = self.msgSrv.sendMsgCmt(reci, rcStore["name"], msgs, iCntBad, msgFlag)
                        if not rtnData["result"]:
                            raise Exception(rtnData["info"])
                        for msgItem in msgs:
                            # 更新标志
                            lsSql = r"update business_notice set status = 1 where commentID = {commentID}".format(
                                commentID=msgItem["commentID"]
                            )
                            curService.execute(lsSql)
                        connService.commit()
                        print("send:")
                        print(msgs)
                    if sDate > rcStore["lastSend"]:
                        lsSql = r"update store_info set lastSend='{lastSend}' where erpID={storeID}".format(
                            lastSend=sDate,
                            storeID=rcStore["storeID"]
                        )
                        curOrder.execute(lsSql)
                        connOrder.commit()
            rtnData["result"] = True
        except Exception as e:
            rtnData["result"] = False
            if ibConnOrder:
                connOrder.rollback()
            if ibConnService:
                connService.rollback()
            rtnData["info"] = str(e)
        finally:
            if ibConnOrder:
                connOrder.close()
            if ibConnService:
                connService.close()

        return rtnData

    def errLogSend(self):
        """
        错误日志报警
        """
        rtnData = {
            "result": False,  # 逻辑控制 True/False
            "info": "",  # 信息
            "dataString": "",  # 字符串
            "dataNumber": 0,  # 数字
            "entities": {}
        }
        ibConn = False
        try:
            conn = self.dbOrder.GetConnect()
            ibConn = True
            cur = conn.cursor()

            # 日志记录开始时间：今天
            sDate = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
            timeCmt = int(time.mktime(time.strptime(sDate, "%Y-%m-%d")))
            lsSql = r"select oper_time, storeID, busi_type, step, begin_date, end_date, remark from oper_log where oper_time >= {oper_time} and step = -1 and status = 0".format(
                oper_time=timeCmt
            )
            ldCol = ["oper_time", "storeID", "busi_type", "step", "begin_date", "end_date", "remark"]
            cur.execute(lsSql)
            rsTmp = cur.fetchall()
            rsLog = [dict(zip(ldCol, line)) for line in rsTmp]
            if len(rsLog) > 0:
                rtnData = self.msgSrv.sendMsgLog(rsLog)
                if not rtnData["result"]:
                    raise Exception(rtnData["info"])
                lsSql = r"update oper_log set status=1 where oper_time >= {oper_time} and step = -1 and status = 0".format(
                    oper_time=timeCmt
                )
                cur.execute(lsSql)
                conn.commit()
            else:
                rtnData["result"] = True
        except Exception as e:
            rtnData["result"] = False
            if ibConn:
                conn.rollback()
        finally:
            if ibConn:
                conn.close()

        return rtnData

if __name__ == "__main__":
    import os, sys
    from interConfig import Settings
    sPath = os.path.dirname(sys.executable)
    sPath = os.path.dirname(sPath)
    sPath = os.path.dirname(sPath)
    sett = Settings(sPath, "config")
    inter = InterControl(sett)
    rtn = inter.dataHandle(9598509)
    print(rtn)
    rtn = inter.errLogSend()
    print(rtn)
