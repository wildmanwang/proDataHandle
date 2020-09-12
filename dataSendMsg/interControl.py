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
        self.msgSrv = MsgJYKX()

    def dataHandle(self, storeID):
        """
        :return:
        """
        rtnData = {
            "result": False,  # 逻辑控制 True/False
            "dataString": "",  # 字符串
            "dataNumber": 0,  # 数字
            "info": "",  # 信息
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

            # 评价记录开始时间：今天-3
            sDate = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 60 * 60 * 24 * 1))
            timeCmt = int(time.mktime(time.strptime(sDate, "%Y-%m-%d")))

            # 逐个处理每个门店
            if storeID > 0:
                lsSql = r"select erpID, name, recipient, IFNULL(lastSend, '') from store_info where erpID={storeID} and recipient>0".format(storeID=storeID)
            else:
                lsSql = r"select erpID, name, recipient, IFNULL(lastSend, '') from store_info where status=1 and recipient>0 order by level desc"
            ldCol = ["storeID", "name", "recipient", "lastSend"]
            curOrder.execute(lsSql)
            rsTmp = curOrder.fetchall()
            rsStore = [dict(zip(ldCol, line)) for line in rsTmp]
            for rcStore in rsStore:
                msgs = []
                # 统计全部差评数量
                lsSql = r"select count(erpID), sum(if(order_score < 3, 1, 0)) from comment_main where storeID = {storeID} and comment_time >= {cmt_time}".format(
                    cmt_time=timeCmt,
                    storeID=rcStore["storeID"]
                )
                curOrder.execute(lsSql)
                rsTmp = curOrder.fetchall()
                iCntAll = rsTmp[0][0]
                iCntBad = rsTmp[0][1]
                # 检索该门店待处理记录
                lsSql = r"select commentID, comment_time, order_score, commentStr, order_time, orderNum, orderID, delivery_time, sure_flag from business_notice " \
                        r"where comment_time >= {cmt_time} and storeID = {storeID} and order_score < 3 and status = 0".format(
                    cmt_time=timeCmt,
                    storeID=rcStore["storeID"]
                )
                ldCol = ["commentID", "comment_time", "order_score", "commentStr", "order_time", "orderNum", "orderID", "delivery_time", "sure_flag"]
                curService.execute(lsSql)
                rsTmp = curService.fetchall()
                rsMsg = [dict(zip(ldCol, line)) for line in rsTmp]
                for msg in rsMsg:
                    # 添加消息内容
                    msgs.append({
                        "cmtTime": msg["comment_time"],
                        "orderScore": msg["order_score"],
                        "cmtStr": msg["commentStr"],
                        "orderTime": msg["order_time"],
                        "orderNum": msg["orderNum"],
                        "orderID": msg["orderID"],
                        "callbackTime": msg["delivery_time"] + 24 * 60 * 60,
                        "sureFlag": msg["sure_flag"]
                    })
                    # 更新标志
                    lsSql = r"update business_notice set status = 1 where commentID = {commentID}".format(
                        commentID=msg["commentID"]
                    )
                    curService.execute(lsSql)
                # 发送消息
                if len(rsMsg) > 0 or len(rsMsg) == 0 and iCntAll > 0 and sDate > rcStore["lastSend"]:
                    for reci in rcStore["recipient"].split(";"):
                        self.msgSrv.send_msg(reci, rcStore["name"], msgs, iCntBad)
                        print("send:")
                        print(msgs)
                    if sDate > rcStore["lastSend"]:
                        lsSql = r"update store_info set lastSend='{lastSend}' where erpID={storeID}".format(
                            lastSend=sDate,
                            storeID=rcStore["storeID"]
                        )
                    curOrder.execute(lsSql)
                connOrder.commit()
                connService.commit()
            rtnData["result"] = True
        except Exception as e:
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

    def sendMsg(self, person, msg):
        """
        发消息
        :param person:
        :param msg:
        :return:
        """
        pass

if __name__ == "__main__":
    import os, sys
    from interConfig import Settings
    sPath = os.path.dirname(sys.executable)
    sPath = os.path.dirname(sPath)
    sPath = os.path.dirname(sPath)
    sett = Settings(sPath, "config")
    inter = InterControl(sett)
    rtn = inter.dataHandle(0)
    print(rtn)
