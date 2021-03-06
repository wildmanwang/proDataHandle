# -*- coding:utf-8 -*-
"""
数据对接控制类
"""
__author__ = "Cliff.wang"
from datetime import datetime, timedelta
from interMysql import MYSQL
import time
import math

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
        用户信息匹配：根据用户ID和用户名匹配
        OK配送时长匹配：按分/秒计算；舍尾/舍入/进位
        OK超时时长匹配：按分/秒计算；舍尾/舍入/进位
        【模糊匹配】
        OK在评价时间前60分钟内送达，只有一个订单
        OK送达时间和评价时间都在0:00-7:00间，只有一个订单
        OK不同日期，送达与评价绝对值相差60分钟，只有一个订单
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
        【任务策略】
            每日09:00启动任务
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

            # 逐个处理每个门店
            lsSql = r"select erpID, name, initFlag, msgScore from store_info where status > 0 order by level"
            ldCol = ["storeID", "name", "initFlag", "msgScore"]
            curOrder.execute(lsSql)
            rsTmp = curOrder.fetchall()
            rsStore = [dict(zip(ldCol, line)) for line in rsTmp]
            for rcStore in rsStore:
                if rcStore["initFlag"] == 0:
                    # 首次分析评价记录开始时间：今天-7
                    timeCmt = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 60 * 60 * 24 * 7))
                else:
                    # 日常分析评价记录开始时间：今天-3
                    timeCmt = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 60 * 60 * 24 * 3))
                timeCmt = int(time.mktime(time.strptime(timeCmt, "%Y-%m-%d")))

                # 订单记录开始时间：今天-14
                timeOrder = time.strftime("%Y-%m-%d", time.localtime(int(time.time()) - 60 * 60 * 24 * 14))
                timeOrder = int(time.mktime(time.strptime(timeOrder, "%Y-%m-%d")))

                # 检索该门店待处理记录
                lsSql = r"select erpID, order_score, pic_cnt, comment_time, from_time, to_time, ship_duration, over_duration, consumerSName, comment_str from comment_main " \
                        r"where comment_time >= {cmt_time} and storeID = {storeID} and orderID is null order by comment_time".format(
                    cmt_time=timeCmt,
                    storeID=rcStore["storeID"]
                )
                ldCol = ["commentID", "order_score", "pic_cnt", "comment_time", "from_time", "to_time", "ship_duration", "over_duration", "consumerSName", "comment_str"]
                curOrder.execute(lsSql)
                rsTmp = curOrder.fetchall()
                rsCmtMain = [dict(zip(ldCol, line)) for line in rsTmp]

                # 准备好辅助数据
                lsSql = r"select order_main.erpID, order_main.num, order_main.order_time, order_main.estimate_arrival_time, order_main.delivery_time, order_main.consumerID, ifnull(consumer_info.consumerSName, ''), order_main.remark " \
                        r"from order_main left join consumer_info on order_main.consumerID = consumer_info.consumerID " \
                        r"where order_main.order_time >= {order_time} and order_main.storeID = {storeID} and order_main.status = 8 and order_main.matched = 0 order by order_main.order_time".format(
                    order_time=timeOrder,
                    storeID=rcStore["storeID"]
                )
                ldCol = ["orderID", "num", "order_time", "estimate_arrival_time", "delivery_time", "consumerID", "consumerSName", "remark"]
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
                    iFlagSure = 0
                    sInfo = ""

                    # 调试代码
                    if rcCmt["commentID"] == 3745759421:
                        iDebug = 0

                    # 时间范围匹配：评价起止时间范围
                    lOrder, iFlagSure, sInfo = self.stepABillTime(rcCmt, lOrder)
                    if len(lOrder) == 0:
                        continue

                    # 单据商品匹配：数量和名称精确匹配
                    lOrder, iFlagSure, sInfo = self.stepBBillItem(rcCmt, lOrder, rsCmtDetail, rsOrderDetail)
                    if len(lOrder) == 0:
                        continue

                    # 踩赞商品匹配：商品名称模糊匹配
                    lOrder, iFlagSure, sInfo = self.stepCCommentItem(rcCmt, lOrder, rsCmtDetail, rsOrderDetail)
                    if len(lOrder) == 0:
                        continue

                    # 用户信息匹配
                    if len(lOrder) > 1:
                        lOrder, iFlagSure, sInfo = self.stepDConsumerInfo(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 配送时长匹配：按分/秒计算；舍尾/舍入/进位
                    if len(lOrder) > 1:
                        lOrder, iFlagSure, sInfo = self.stepEShipTime(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 超时时长匹配：按分/秒计算；舍尾/舍入/进位
                    if len(lOrder) > 1:
                        lOrder, iFlagSure, sInfo = self.stepFOverTime(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 用户名称匹配
                    if len(lOrder) > 1:
                        lOrder, iFlagSure, sInfo = self.stepGConsumerName(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 评价时机匹配
                    if len(lOrder) > 1:
                        lOrder, iFlagSure, sInfo = self.stepHCommentMoment(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 特殊场景匹配：多种方案
                    if len(lOrder) > 1:
                        lOrder, iFlagSure, sInfo = self.stepXMatchOne(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 权重经验匹配：给不同的情况设置不同的权重
                    if len(lOrder) > 1:
                        lOrder, iFlagSure, sInfo = self.stepYByWeight(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    # 终极排序匹配：按指定规则获取一个结果
                    if len(lOrder) > 1:
                        lOrder, iFlagSure, sInfo = self.stepZFinal(rcCmt, lOrder)
                        if len(lOrder) == 0:
                            continue

                    lsSql = r"delete from business_notice where storeID={storeID} and commentID = {commentID}".format(
                        storeID=rcStore["storeID"],
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
                        if iFlagSure >= 8:
                            # 更新订单匹配标志
                            lsSql = r"update order_main set matched=1 where erpID={orderID}".format(
                                orderID=lOrder[0]["orderID"]
                            )
                            curOrder.execute(lsSql)
                            # 更新顾客信息库
                            if rcCmt["consumerSName"] != "匿名用户":
                                lsSql = r"select count(*) from consumer_info where consumerID={consumerID}".format(
                                    consumerID=lOrder[0]["consumerID"]
                                )
                                curOrder.execute(lsSql)
                                rsTmp = curOrder.fetchall()
                                if rsTmp[0][0] > 0:
                                    lsSql = r"update consumer_info set consumerSName='{consumerSName}' where consumerID={consumerID}".format(
                                        consumerSName=rcCmt["consumerSName"],
                                        consumerID=lOrder[0]["consumerID"]
                                    )
                                else:
                                    lsSql = r"insert into consumer_info ( consumerID, consumerSName ) values ({consumerID}, '{consumerSName}' )".format(
                                        consumerSName=rcCmt["consumerSName"],
                                        consumerID=lOrder[0]["consumerID"]
                                    )
                                curOrder.execute(lsSql)
                        # 把已匹配的订单从备选订单中删除
                        rsOrderMain.remove(lOrder[0])
                        # 一单一提交
                        connOrder.commit()
                        rtnData["dataNumber"] += 1
                    if len(lOrder) == 1 or len(lOrder) > 1 and len(lOrder) < 5 and rcCmt["order_score"] <= rcStore["msgScore"]:
                        # 生成通知消息
                        for recOrder in lOrder:
                            lsSql = r"insert into business_notice ( storeID, commentID, orderID, comment_time, order_score, pic_cnt, commentStr, orderNum, order_time, delivery_time, order_remark, sure_flag, remark ) " \
                                    r"values ( {storeID}, {commentID}, {orderID}, {comment_time}, {order_score}, {pic_cnt}, '{commentStr}', {orderNum}, {order_time}, {delivery_time}, '{order_remark}', {sure_flag}, '{remark}' )".format(
                                storeID=rcStore["storeID"],
                                commentID=rcCmt["commentID"],
                                orderID=recOrder["orderID"],
                                comment_time=rcCmt["comment_time"],
                                order_score=rcCmt["order_score"],
                                pic_cnt=rcCmt["pic_cnt"],
                                commentStr=rcCmt["comment_str"],
                                orderNum=recOrder["num"],
                                order_time=recOrder["order_time"],
                                delivery_time=recOrder["delivery_time"],
                                order_remark=recOrder["remark"],
                                sure_flag=iFlagSure,
                                remark=sInfo
                            )
                            curService.execute(lsSql)
                    elif len(lOrder) == 0 and rcCmt["order_score"] <= rcStore["msgScore"]:
                        lsSql = r"insert into business_notice ( storeID, commentID, orderID, comment_time, order_score, pic_cnt, commentStr, orderNum, order_time, delivery_time, order_remark, sure_flag, remark ) " \
                                r"values ( {storeID}, {commentID}, {orderID}, {comment_time}, {order_score}, {pic_cnt}, '{commentStr}', {orderNum}, {order_time}, {delivery_time}, '{order_remark}', {sure_flag}, '{remark}' )".format(
                            storeID=rcStore["storeID"],
                            commentID=rcCmt["commentID"],
                            orderID=0,
                            comment_time=rcCmt["comment_time"],
                            order_score=rcCmt["order_score"],
                            pic_cnt=rcCmt["pic_cnt"],
                            commentStr=rcCmt["comment_str"],
                            orderNum=0,
                            order_time=0,
                            delivery_time=0,
                            order_remark=None,
                            sure_flag=iFlagSure,
                            remark=sInfo
                        )
                        curService.execute(lsSql)
                    connService.commit()
                if rcStore["initFlag"] == 0:
                    lsSql = r"update store_info set initFlag = 1 where erpID={storeID} and initFlag=0".format(storeID=rcStore["storeID"])
                    curOrder.execute(lsSql)
                    connOrder.commit()
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
        iCnt = len(lOrder)
        # 下单时间范围
        tFrom = rcCmt["from_time"]
        # 2次出现过了48小时评价还没出现明细商品的情况，超时在30分钟内，把时长放开到60分钟
        tFrom -= 60 * 60
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

        return lOrder, 9, "A：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def stepBBillItem(self, rcCmt, lOrder, rsCmtDetail, rsOrderDetail):
        """
        单据商品匹配：数量和名称精确匹配
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :param rsCmtDetail: 评价商品明细
        :param rsOrderDetail: 订单商品明细
        :return: 匹配后的订单列表
        """
        iCnt = len(lOrder)
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
        return lOrder, 9, "B：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def stepCCommentItem(self, rcCmt, lOrder, rsCmtDetail, rsOrderDetail):
        """
        踩赞商品匹配：商品名称模糊匹配
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :param rsCmtDetail: 评价商品明细
        :param rsOrderDetail: 订单商品明细
        :return: 匹配后的订单列表
        """
        iCnt = len(lOrder)
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
        return lOrder, 9, "C：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def stepDConsumerInfo(self, rcCmt, lOrder):
        """
        用户信息匹配
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :return:
        """
        iCnt = len(lOrder)
        if rcCmt["consumerSName"] and rcCmt["consumerSName"] != "匿名用户":
            lOrder = [i for i in lOrder if (len(i["consumerSName"]) == 0 or i["consumerSName"] == rcCmt["consumerSName"])]
        return lOrder, 9, "D：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def stepEShipTime(self, rcCmt, lOrder):
        """
        配送时长匹配：按分/秒计算；舍尾/舍入/进位
        配送分钟-4 < 配送时长四舍五入分钟取整 < 配送分钟
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :return: 匹配后的订单列表
        """
        iCnt = len(lOrder)
        for rcTmp in lOrder[::-1]:
            # 计算配送时长：向上取整：2/59例外
            iShip = math.ceil((rcTmp["delivery_time"] - rcTmp["order_time"])/60)
            # 订单配送时间相对评价配送时间范围：向下5分钟，向上1分钟
            if iShip <= rcCmt["ship_duration"] - 5 or iShip > rcCmt["ship_duration"] + 1:
                lOrder.remove(rcTmp)
        return lOrder, 8, "E：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def stepFOverTime(self, rcCmt, lOrder):
        """
        超时时长匹配：按分/秒计算；舍尾/舍入/进位
        送达时间进位分钟取整-预计送达时间进位分钟取整=超时分钟
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :return: 匹配后的订单列表
        """
        iCnt = len(lOrder)
        if rcCmt["over_duration"] > 0:
            for rcTmp in lOrder[::-1]:
                # 计算超时时长：向上取整：0/13例外
                iShip = math.ceil((rcTmp["delivery_time"] - rcTmp["estimate_arrival_time"]) / 60)
                if rcCmt["over_duration"] != iShip:
                    lOrder.remove(rcTmp)
        else:
            for rcTmp in lOrder[::-1]:
                if rcTmp["estimate_arrival_time"] < rcTmp["delivery_time"]:
                    lOrder.remove(rcTmp)
        return lOrder, 8, "F：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def stepGConsumerName(self, rcCmt, lOrder):
        """
        用户名称匹配
        :param rcCmt: 评价主记录
        :param lOrder: 匹配前订单列表
        :return:
        """
        iCnt = len(lOrder)
        if rcCmt["consumerSName"] and rcCmt["consumerSName"] != "匿名用户":
            lTmp = [i for i in lOrder if (i["consumerSName"] == rcCmt["consumerSName"])]
            if len(lTmp) > 0:
                lOrder = lTmp
        return lOrder, 8, "G：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def stepHCommentMoment(self, rcCmt, lOrder):
        """
        评价时机匹配
        :param rcCmt:
        :param lOrder:
        :return:
        """
        iCnt = len(lOrder)
        sInfo = ""
        # 变量定义
        tCmt = rcCmt["comment_time"]
        lTmp = []

        # 送达时间和评价时间都在当天0:00-7:00间，只有一个订单
        if len(lTmp) == 0:
            lTmp = [i for i in lOrder if (tCmt - i["delivery_time"] <= 7 * 60 * 60 and self._getHour(tCmt) >= 0 and self._getHour(tCmt) <= 7 and self._getHour(i["delivery_time"]) >= 0 and self._getHour(i["delivery_time"]) <= 7)]
            sInfo += "H1:{num1}/{num2};".format(num1=len(lTmp), num2=iCnt)
            if len(lTmp) > 0:
                lOrder = lTmp

        # 在评价时间前60分钟内送达，只有一个订单
        if len(lTmp) == 0:
            lTmp = [i for i in lOrder if (tCmt - i["delivery_time"] <= 60 * 60)]
            sInfo += "H2-1:{num1}/{num2};".format(num1=len(lTmp), num2=iCnt)
            if len(lTmp) > 0:
                lOrder = lTmp
            if len(lTmp) > 1:
                # 送达30秒后评价更常见
                lTmp = [i for i in lTmp if (tCmt - i["delivery_time"] >= 30)]
                sInfo += "H2-2:{num1}/{num2};".format(num1=len(lTmp), num2=iCnt)
                if len(lTmp) > 0:
                    lOrder = lTmp
                if len(lTmp) > 1:
                    # 30分钟内评价更常见
                    lTmp = [i for i in lTmp if (tCmt - i["delivery_time"] <= 30 * 60)]
                    sInfo += "H2-3:{num1}/{num2};".format(num1=len(lTmp), num2=iCnt)
                    if len(lTmp) > 0:
                        lOrder = lTmp

        return lOrder, 6, sInfo

    def stepXMatchOne(self, rcCmt, lOrder):
        """
        特殊场景匹配：多种方案
        :param rcCmt:
        :param lOrder:
        :return:
        """
        iCnt = len(lOrder)
        sInfo = ""
        # 变量定义
        tCmt = rcCmt["comment_time"]
        lTmp = []

        # 当天评价
        if len(lTmp) == 0 and 1==2:
            # 该规则可靠度低，暂屏蔽
            lTmp = [i for i in lOrder if ( self._getDay(i["delivery_time"]) == self._getDay(tCmt))]
            sInfo += "X1:{num1}/{num2};".format(num1=len(lTmp), num2=iCnt)
            if len(lTmp) == 1:
                lOrder = lTmp

        # 不同日期，日期相差不过7天，送达与评价绝对值相差指定时长内，只有一个订单
        if len(lTmp) == 0 and 1==2:
            # 该规则可靠度低，暂屏蔽
            lTmp = [i for i in lOrder if (tCmt - i["delivery_time"] > 7 * 60 * 60 and tCmt - i["delivery_time"] < (7 * 24 + 1) * 60 * 60 and abs(tCmt % (24 * 60 * 60) - i["delivery_time"] % (24 * 60 * 60)) < 90 * 60)]
            sInfo += "X2-1:{num1}/{num2};".format(num1=len(lTmp), num2=iCnt)
            if len(lTmp) == 1:
                lOrder = lTmp
            elif len(lTmp) > 1:
                lTmp = [i for i in lTmp if (abs(tCmt % (24 * 60 * 60) - i["delivery_time"] % (24 * 60 * 60)) < 60 * 60)]
                sInfo += "X2-2:{num1}/{num2};".format(num1=len(lTmp), num2=iCnt)
                if len(lTmp) == 1:
                    lOrder = lTmp
                elif len(lTmp) > 1:
                    lTmp = [i for i in lTmp if (abs(tCmt % (24 * 60 * 60) - i["delivery_time"] % (24 * 60 * 60)) < 30 * 60)]
                    sInfo += "X2-3:{num1}/{num2};".format(num1=len(lTmp), num2=iCnt)
                    if len(lTmp) == 1:
                        lOrder = lTmp

        return lOrder, 4, sInfo

    def stepYByWeight(self, rcCmt, lOrder):
        """
        权重经验匹配：给不同的情况设置不同的权重
        :param rcCmt:
        :param lOrder:
        :return:
        """
        iCnt = len(lOrder)
        return lOrder, 4, "Y：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def stepZFinal(self, rcCmt, lOrder):
        """
        终极排序匹配：按指定规则获取一个结果
        :param rcCmt:
        :param lOrder:
        :return:
        """
        iCnt = len(lOrder)
        return lOrder, 3, "Z：{num1}/{num2}".format(num1=len(lOrder), num2=iCnt)

    def histroyHandle(self):
        """
        历史数据处理：
        1 已完成的数据定期删除
        2 未完成的数据定期删除
        3 删除数据前按月统计完成率
        """
        pass

    def _getDay(self, iTime):
        """
        获取时间戳日
        :param iTime:
        :return:
        """
        return int(time.strftime("%Y%m%d", time.localtime(iTime)))

    def _getHour(self, iTime):
        """
        获取时间戳小时
        :return:
        """
        return int(time.strftime("%H", time.localtime(iTime)))

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
