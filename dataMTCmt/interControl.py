# -*- coding:utf-8 -*-
"""
数据对接控制类
"""
__author__ = "Cliff.wang"
from datetime import datetime, timedelta
from interMysql import MYSQL
import time

class InterControl():

    def __init__(self, sett):
        """
        接口控制类
        """
        self.sett = sett
        self.dbOrder = MYSQL(self.sett.dbOrderHost, self.sett.dbOrderUser, self.sett.dbOrderPassword, self.sett.dbOrderDatabase)
        self.dbService = MYSQL(self.sett.dbServiceHost, self.sett.dbServiceUser, self.sett.dbServicePassword, self.sett.dbServiceDatabase)

    def dataHandle(self):
        """
        把评论映射到订单
        【精确匹配】
        OK时间范围匹配：评价起止时间范围
        OK单据商品匹配：数量和名称精确匹配
        OK踩赞商品匹配：商品名称模糊匹配
        UN配送超时评价：只有配送分差评，配送超时
        UN配送时长匹配：按分/秒计算；舍尾/舍入/进位
        UN超时时长匹配：按分/秒计算；舍尾/舍入/进位
        【优先级规则】
        当日吃完后评价：当日送达10、40、60、120分钟内评价                               +0、10、6、3
        当日口味分差评：只有口味分差评，送达10、40、60、120分钟内评价                     +0、5、3、1
        当日配送分差评：只有配送分差评、送达40分钟内评价、且配送超时5、10、20、30、60分钟    +1、2、3、4、5
        当日全满分评价：送达后5分钟内全满分评价                                        -10
        当日低峰期评价：当日评论和送达都在0:00-7:00间                                  +5
        隔日下单后评价：不同日期时段下单相差-5、10、20、30、40分钟内评价                   +10、10、6、3、1
        隔日吃完后评价：不同日期时段送达相差10、40、60、120分钟内评价                     +5、10、6、4
        时间相关性原则：送达1、3、5、7天后评价                                         -（天数-1）
        【终极选择】
        （评论时间 - 送达时间）:按[（原值-原值舍入到整数）的绝对值]取最小
        【问题】
        * 配送时间怎么计算？暂定=（送达时间秒-下单时间秒）/60四舍五入                      把握：80%
        * 超时时间怎么计算？暂定=（送达时间秒-预计送达时间秒）/60四舍五入                   把握：30%
        * 有商品明细的评价，是否可以有两个相同的商品？不可以                               把握：80%，待实际测试
        * 有踩赞明细的评价，实际商品数是否可以大于踩赞商品数？可以                          把握：90%，待实际测试
        :return:
        """
        # MYSQL
        # 时间戳转时间：select from_unixtime(1596720546)，返回2020-08-06 21:29:06
        # 时间转时间戳：select unix_timestamp('2020-08-06 21:29:06')，返回1596720546
        # PYTHON
        # 获取时间戳（秒）：int(time.time())

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
            # 获取数据库连接
            connOrder = self.dbOrder.GetConnect()
            ibConnOrder = True
            curOrder = connOrder.cursor()
            connService = self.dbService.GetConnect()
            ibConnService = True
            curService = connService.cursor()

            # 评价记录开始时间：今天-1
            timeCmt = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 60 * 60 * 24 * 1))
            timeCmt = int(time.mktime(time.strptime(timeCmt, "%Y-%m-%d")))
            timeCmt = 0

            # 订单记录开始时间：今天-3
            timeOrder = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 60 * 60 * 24 * 2))
            timeOrder = int(time.mktime(time.strptime(timeOrder, "%Y-%m-%d")))
            timeOrder = 0

            # 逐个处理每个门店
            lsSql = r"select erpID, name from store_info where status = 1 order by level desc"
            ldCol = ["storeID", "name"]
            curOrder.execute(lsSql)
            rsTmp = curOrder.fetchall()
            rsStore = [dict(zip(ldCol, line)) for line in rsTmp]
            for rcStore in rsStore:
                # 检索该门店待处理记录
                lsSql = r"select erpID, comment_str, order_score, comment_time, from_time, to_time, ship_duration, over_duration from comment_main " \
                        r"where comment_time >= {cmt_time} and storeID = {storeID} and orderID is null".format(
                    cmt_time=timeCmt,
                    storeID=rcStore["storeID"]
                )
                ldCol = ["commentID", "comment_str", "order_score", "comment_time", "from_time", "to_time", "ship_duration", "over_duration"]
                curOrder.execute(lsSql)
                rsTmp = curOrder.fetchall()
                rsCmtMain = [dict(zip(ldCol, line)) for line in rsTmp]

                # 准备好辅助数据
                lsSql = r"select erpID, storeID, order_time, estimate_arrival_time, delivery_time from order_main " \
                        r"where order_time >= {order_time} and storeID = {storeID} and status = 8".format(
                    order_time=timeOrder,
                    storeID=rcStore["storeID"]
                )
                ldCol = ["orderID", "storeID", "order_time", "estimate_arrival_time", "delivery_time"]
                curOrder.execute(lsSql)
                rsTmp = curOrder.fetchall()
                rsOrderMain = [dict(zip(ldCol, line)) for line in rsTmp]

                lsSql = r"select orderID, itemID, itemName, unit from order_detail " \
                        r"where order_time >= {order_time} and storeID = {storeID}".format(
                    order_time=timeOrder,
                    storeID=rcStore["storeID"]
                )
                ldCol = ["orderID", "itemID", "itemName", "unit"]
                curOrder.execute(lsSql)
                rsTmp = curOrder.fetchall()
                rsOrderDetail = [dict(zip(ldCol, line)) for line in rsTmp]

                lsSql = r"select commentID, itemSource, itemID, itemName from comment_detail " \
                        r"where comment_time >= {cmt_time} and storeID = {storeID}".format(
                    cmt_time=timeCmt,
                    storeID=rcStore["storeID"]
                )
                ldCol = ["commentID", "itemSource", "itemID", "itemName"]
                curOrder.execute(lsSql)
                rsTmp = curOrder.fetchall()
                rsCmtDetail = [dict(zip(ldCol, line)) for line in rsTmp]

                for rcCmt in rsCmtMain:
                    lOrder = [i for i in rsOrderMain]

                    # 时间范围匹配：评价起止时间范围
                    lOrder = self.stepABillTime(rcCmt, lOrder)
                    if len(lOrder) == 0:
                        continue

                    # 单据商品匹配：数量和名称精确匹配
                    lOrder = self.stepABillItem(rcCmt, lOrder, rsCmtDetail, rsOrderDetail)
                    if len(lOrder) == 0:
                        continue

                    # 踩赞商品匹配：商品名称模糊匹配
                    lOrder = self.stepACommentItem(rcCmt, lOrder, rsCmtDetail, rsOrderDetail)
                    if len(lOrder) == 0:
                        continue

                    # 配送超时评价：只有配送分差评，配送超时
                    if len(lOrder) > 1:
                        lOrder = self.stepBOverComment(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 配送时长匹配：按分/秒计算；舍尾/舍入/进位
                    if len(lOrder) > 1:
                        lOrder = self.stepBShipTime(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 超时时长匹配：按分/秒计算；舍尾/舍入/进位
                    if len(lOrder) > 1:
                        lOrder = self.stepBOverTime(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 权重经验匹配：给不同的情况设置不同的权重
                    if len(lOrder) > 1:
                        lOrder = self.stepCByWeight(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 终极排序匹配：按指定规则获取一个结果
                    if len(lOrder) > 1:
                        lOrder = self.stepOFinal(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    lsSql = r"delete from handle_data where commentID = {commentID}".format(
                        commentID=rcCmt["commentID"]
                    )
                    curService.execute(lsSql)
                    if len(lOrder) == 1:
                        # 找到订单，更新订单关系
                        lsSql = r"update comment_main set orderID={orderID} where erpID={commentID}".format(
                            orderID=lOrder[0]["orderID"],
                            commentID=rcCmt["commentID"]
                        )
                        curOrder.execute(lsSql)
                        # 生成通知消息
                        lsSql = r"insert into business_notice ( storeID, commentID, commentDate, order_score, commentStr, orderID, status ) " \
                                r"values ( {storeID}, {commentID}, '{commentDate}', {order_score}, '{comment_str}', {orderID}, 0 )".format(
                            storeID=rcStore["storeID"],
                            commentID=rcCmt["commentID"],
                            commentDate=rcCmt["comment_time"],
                            order_score=rcCmt["order_score"],
                            comment_str=rcCmt["comment_str"],
                            orderID=lOrder[0]["orderID"]
                        )
                        curService.execute(lsSql)
                        # 一单一提交
                        connOrder.commit()
                        rtnData["dataNumber"] += 1
                    elif len(lOrder) > 1 and len(lOrder) <= 3:
                        # 确定了范围，待下次重新分析，写入临时表
                        for recOrder in lOrder:
                            lsSql = r"insert into handle_data ( commentID, orderID ) values ( {commentID}, {orderID} )".format(
                                commentID=rcCmt["commentID"],
                                orderID=recOrder["orderID"]
                            )
                            curService.execute(lsSql)
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

    def stepABillTime(self, rcCmt, lOrder):
        """
        时间范围匹配：评价起止时间范围
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :return: 匹配后的订单列表
        """
        # 下单时间范围
        tFrom = rcCmt["from_time"]
        tTo = rcCmt["to_time"]
        for rcTmp in lOrder[::-1]:
            t1 = rcTmp["order_time"]
            if not (t1 > tFrom and t1 < tTo):
                lOrder.remove(rcTmp)

        # 送达时间<评价时间
        tCmt = rcCmt["comment_time"]
        for rcTmp in lOrder[::-1]:
            t1 = rcTmp["delivery_time"]
            if not (t1 < tCmt):
                lOrder.remove(rcTmp)

        return lOrder

    def stepABillItem(self, rcCmt, lOrder, rsCmtDetail, rsOrderDetail):
        """
        单据商品匹配：数量和名称精确匹配
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :param rsCmtDetail: 评价商品明细
        :param rsOrderDetail: 订单商品明细
        :return: 匹配后的订单列表
        """
        lItemCmt = [i for i in rsCmtDetail if (i["commentID"] == rcCmt["commentID"] and i["itemSource"] == 1)]
        if len(lItemCmt) > 0:
            for rcTmp in lOrder[::-1]:
                lItemOrder = [i for i in rsOrderDetail if (i["orderID"] == rcTmp["orderID"])]
                bFind = False
                if len(lItemCmt) == len(lItemOrder):
                    for i in lItemCmt:
                        bFind = False
                        for j in lItemOrder:
                            if i["itemName"] == j["itemName"]:
                                bFind = True
                                break
                        if not bFind:
                            break
                if not bFind:
                    lOrder.remove(rcTmp)
        return lOrder

    def stepACommentItem(self, rcCmt, lOrder, rsCmtDetail, rsOrderDetail):
        """
        踩赞商品匹配：商品名称模糊匹配
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :param rsCmtDetail: 评价商品明细
        :param rsOrderDetail: 订单商品明细
        :return: 匹配后的订单列表
        """
        lItemCmt = [i for i in rsCmtDetail if (i["commentID"] == rcCmt["commentID"] and i["itemSource"] > 1)]
        if len(lItemCmt) > 0:
            for rcTmp in lOrder[::-1]:
                lItemOrder = [i for i in rsOrderDetail if (i["orderID"] == rcTmp["orderID"])]
                bFind = False
                for i in lItemCmt:
                    bFind = False
                    for j in lItemOrder:
                        if j["itemName"].startswith(i["itemName"]):
                            bFind = True
                            break
                    if not bFind:
                        break
                if not bFind:
                    lOrder.remove(rcTmp)
        return lOrder

    def stepBOverComment(self, rcCmt, lOrder):
        """
        配送超时评价：只有配送分差评，配送超时
        :param rcCmt:
        :param lOrder:
        :return:
        """
        return lOrder

    def stepBShipTime(self, rcCmt, lOrder):
        """
        配送时长匹配：按分/秒计算；舍尾/舍入/进位
        配送分钟-4 < 配送时长四舍五入分钟取整 < 配送分钟
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :return: 匹配后的订单列表
        """
        for rcTmp in lOrder[::-1]:
            if rcCmt["ship_duration"] != int((rcTmp["delivery_time"] - rcTmp["order_time"])/60):
                lOrder.remove(rcTmp)
        return lOrder

    def stepBOverTime(self, rcCmt, lOrder):
        """
        超时时长匹配：按分/秒计算；舍尾/舍入/进位
        送达时间进位分钟取整-预计送达时间进位分钟取整=超时分钟
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :return: 匹配后的订单列表
        """
        if rcCmt["over_duration"] > 0:
            for rcTmp in lOrder[::-1]:
                if rcCmt["over_duration"] != int((rcTmp["delivery_time"] - rcTmp["estimate_arrival_time"])/60):
                    lOrder.remove(rcTmp)
        else:
            for rcTmp in lOrder[::-1]:
                if rcTmp["estimate_arrival_time"] < rcTmp["delivery_time"]:
                    lOrder.remove(rcTmp)
        return lOrder

    def stepCByWeight(self, rcCmt, lOrder):
        """
        权重经验匹配：给不同的情况设置不同的权重
        :param rcCmt:
        :param lOrder:
        :return:
        """
        return lOrder

    def stepOFinal(self, rcCmt, lOrder):
        """
        终极排序匹配：按指定规则获取一个结果
        :param rcCmt:
        :param lOrder:
        :return:
        """
        return lOrder

    def histroyHandle(self):
        """
        历史数据处理：
        1 已完成的数据定期删除
        2 未完成的数据定期删除
        3 删除数据前按月统计完成率
        """
        pass

if __name__ == "__main__":
    import os
    from interConfig import Settings

    myPath = os.path.abspath(os.path.dirname(__file__))
    mySett = Settings(myPath, "config")

    myInter = InterControl(mySett)
    rtn = myInter.dataHandle()
    if not rtn["result"]:
        print(rtn["info"])
    else:
        print("成功完成评论消息匹配订单的任务.")
    print("为{num}条评论消息找到原始订单.".format(num=rtn["dataNumber"]))
