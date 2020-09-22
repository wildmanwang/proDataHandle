#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-09-10 18:22:18
# Project: mts_orders

from pyspider.libs.base_handler import *
import json
import datetime, time
import random
import pymysql

class Handler(BaseHandler):
    """
    1 订单数据 order
    2 备餐数据 prepare
    3 配送数据 delivery
    4 结算数据 settle
    """
    crawl_config = {
    }

    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "0Wangle?",
            "dbname": "mt_orderinfo"
        }

    def source_replace(self, source, key, value):
        li_pos = source.find(key + "=")
        if li_pos > 0:
            li_len = source[li_pos:].find(";")
            if li_len > 0:
                return source[:li_pos] + key + "=" + value + source[li_pos + li_len:]
            else:
                return source[:li_pos] + key + "=" + value
        else:
            return source

    def source_parse(self, strList):
        varDict = {}
        for strSource in strList:
            for line in strSource.split('; '):
                key, value = line.split('=', 1)
                varDict[key] = value
        return varDict

    def data_handle(self, sJudge, bType, sHandle):
        """
        数据库操作：
        sJudge——判断SQL语句，是否存在这样的记录
        bType——True记录存在则处理，不存在不处理；False记录存在则不处理，不存在则处理
        sHandle——处理SQL语句
        """
        try:
            cur = self.db.cursor()
            cur.execute("set names utf8mb4")
            cur.execute("SET CHARACTER SET utf8mb4")
            cur.execute("SET character_set_connection=utf8mb4")
            if len(sJudge) > 0:
                cur.execute(sJudge)
                rsData = cur.fetchall()
                if (len(rsData) > 0 and bType) or (len(rsData) == 0 and not bType):
                    cur.execute(sHandle)
                    self.db.commit()
            else:
                cur.execute(sHandle)
                self.db.commit()
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))
            self.db.rollback()
    
    def data_select(self, sSelect, sCols):
        """
        获取数据集
        """
        try:
            cur = self.db.cursor()
            cur.execute("set names utf8mb4")
            cur.execute("SET CHARACTER SET utf8mb4")
            cur.execute("SET character_set_connection=utf8mb4")
            cur.execute(sSelect)
            rsTmp = cur.fetchall()
            rsData = [dict(zip(sCols, line)) for line in rsTmp]
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))
        return rsData
    
    def operlog(self, storeID, busi_type, step, begin_date, end_date, remark):
        """
        参数：
        storeID     门店ID
        busi_type   所属业务类型：1 订单 2 评价
        step        阶段：1 任务启动 2 数据抓取 -1 异常产生 0 任务结束
        begin_date  业务开始日期
        end_date    业务截止日期
        remark      备注
        """
        try:
            cur = self.db.cursor()
            lsSql = r"insert into oper_log ( oper_time, storeID, busi_type, step, begin_date, end_date, remark ) " \
                    r"values ( {oper_time}, {storeID}, {busi_type}, {step}, {begin_date}, {end_date}, '{remark}' ) ".format(
                oper_time=int(time.time()),
                storeID=storeID,
                busi_type=busi_type,
                step=step,
                begin_date="{val}".format(val=("'" + begin_date + "'" if begin_date else 'NULL')),
                end_date="{val}".format(val=("'" + end_date + "'" if end_date else 'NULL')),
                remark=remark
            )
            cur.execute(lsSql)
            self.db.commit()
        except Exception as e:
            print(str(e))
            self.db.rollback()

    @every(minutes=24 * 60 * 1000)
    def on_start(self):
        self.bConnected = False
        try:
            self.db = pymysql.connect(
                host=self.db_config["host"], 
                user=self.db_config["user"], 
                password=self.db_config["password"], 
                database=self.db_config["dbname"], 
                charset="utf8mb4", 
                use_unicode=True
            )
            self.bConnected = True
            self.operlog(0, 1, 1, None, None, "")
            lsSql = r"select erpID, initFlag, cookie_order from store_info where status = 1 and cookie_order is not null order by level asc, createTime asc"
            ldCol = ["storeID", "initFlag", "cookie_order"]
            rsStore = self.data_select(lsSql, ldCol)
            for rcStore in rsStore:
                storeVar = {}
                if rcStore["initFlag"] == 1:
                    iFromDays = 1
                else:
                    iFromDays = 6
                storeVar["sDate10StartOrder"] = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=iFromDays),"%Y-%m-%d")
                storeVar["sDate10EndOrder"] = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")
                storeVar["sDate8EndOrder"] = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y%m%d")
                
                strParse = []
                storeVar["cookie_order"] = rcStore["cookie_order"]
                storeVar["cookie_order"] = self.source_replace(storeVar["cookie_order"], "setPrivacyTime", "1_" + datetime.datetime.strftime(datetime.date.today(), "%Y%m%d"))
                strParse.append(storeVar["cookie_order"])
                storeVar["varDict"] = self.source_parse(strParse)
                
                storeVar["headers_order"] = {
                    "Connection": "keep-alive",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": "http://e.waimai.meituan.com/v2/order/new/history?region_id={region_id}&region_version={region_version}".format(
                            region_id=storeVar["varDict"]["region_id"],
                            region_version=storeVar["varDict"]["region_version"]
                        ),
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cookie": storeVar["cookie_order"]
                }
                
                storeVar["headers_settle"] = storeVar["headers_order"].copy()
                storeVar["headers_settle"]["Content-Type"] = "application/x-www-form-urlencoded"
                storeVar["headers_settle"]["Origin"] = "http://e.waimai.meituan.com"

                # 获取订单
                sUrl_order = r"http://e.waimai.meituan.com/v2/order/common/history/all/r/list?" \
                    r"lastLabel=&nextLabel=&userId=-1&tag=all&startDate={dateStart}&endDate={dateEnd}" \
                    r"&region_id={region_id}&region_version={region_version}" \
                    "".format(
                        dateStart=storeVar["sDate10StartOrder"],
                        dateEnd=storeVar["sDate10EndOrder"],
                        region_id=storeVar["varDict"]["region_id"],
                        region_version=storeVar["varDict"]["region_version"]
                    )
                sItag = str(rcStore["storeID"]) + storeVar["sDate8EndOrder"] + "9999"
                self.crawl(sUrl_order + "#" + sItag, headers=storeVar["headers_order"], itag=sItag, age=2*60, retries=2, callback=self.index_page, save=storeVar)
                self.operlog(rcStore["storeID"], 1, 2, storeVar["sDate10StartOrder"], storeVar["sDate10EndOrder"], "")
                time.sleep(random.randint(5,15))
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))

    @config(age=2 * 60)
    def index_page(self, response):
        try:
            if type(response.content).__name__ == "bytes":
                response.content = (response.content).decode('utf-8')
            if response.json["code"] == 0:
                if not response.json["data"]:
                    self.operlog(response.save["varDict"]["wmPoiId"], 1, -1, None, None, "获取订单信息失败：无json数据")
                    return {"info": "获取订单信息失败：无json数据"}
                self.detail_page_order(response)
                iLen = len(response.json["data"]["wmOrderList"])
                if iLen >= 10:
                    iNum = response.json["data"]["wmOrderList"][9]["num"]
                    if iNum == 11:
                        iNum = 12
                    sDateSpc8 = time.strftime("%Y%m%d", time.localtime(response.json["data"]["wmOrderList"][iLen - 1]["order_time"]))
                    if iNum > 1:
                        sUrl = r"http://e.waimai.meituan.com/v2/order/common/history/all/r/list?lastLabel=&nextLabel=" \
                            r"%7B%22day%22%3A{date8}%2C%22day_seq%22%3A{num}%2C%22page%22%3A0%2C%22setDay_seq%22%3Atrue%2C%22setPage%22%3Afalse%2C%22setDay%22%3Atrue%7D" \
                            r"&userId=-1&tag=all&startDate={dateStart}&endDate={dateEnd}&region_id={region_id}&region_version={region_version}" \
                            "".format(
                                date8=sDateSpc8,
                                num=iNum,
                                dateStart=response.save["sDate10StartOrder"],
                                dateEnd=response.save["sDate10EndOrder"],
                                region_id=response.save["varDict"]["region_id"],
                                region_version=response.save["varDict"]["region_version"]
                            )
                        sItag = str(response.save["varDict"]["wmPoiId"]) + sDateSpc8 + str(iNum)
                        time.sleep(random.randint(5,15))
                        self.crawl(sUrl + "#" + sItag, headers=response.save["headers_order"], itag=sItag, age=2*60, retries=1, callback=self.index_page, save=response.save)
            else:
                # code=1001     登录过期，需要重新登录
                self.operlog(response.save["varDict"]["wmPoiId"], 1, -1, None, None, "错误[{code}]：{msg}".format(code=response.json["code"], msg=response.json["msg"]))
                return {"info": "[{storeID}]错误[{code}]：{msg}".format(storeID=response.save["varDict"]["wmPoiId"], code=response.json["code"], msg=response.json["msg"])}
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))

    @config(priority=2)
    def detail_page_order(self, response):
        """
        解析订单数据
        """
        try:
            sUrl_prepare = ""
            sUrl_delivery = ""
            sUrl_settle = r"http://e.waimai.meituan.com/v2/order/receive/r/chargeInfo?region_id={region_id}&region_version={region_version}".format(
                region_id=response.save["varDict"]["region_id"],
                region_version=response.save["varDict"]["region_version"]
            )
            listSettle = []
            for each in response.json["data"]["wmOrderList"]:
                cID = int(each["wm_order_id_view_str"])
                iStatus = each["status"]
                sSqlJ = r"select 1 from order_main where erpID = {orderID} and status < {status}".format(orderID=cID, status=iStatus)
                sSqlH = r"delete from order_main where erpID = {orderID}".format(orderID=cID)
                self.data_handle(sSqlJ, True, sSqlH)
                sSqlJ = r"select 1 from order_main where erpID = {orderID}".format(orderID=cID)
                sSqlH = r"insert into order_main ( erpID, storeID, num, status, order_time, estimate_arrival_time, consumerID, remark ) " \
                    r"values ( {orderID}, {storeID}, {num}, {status}, {order_time}, {estimate_arrival_time}, {consumerID}, '{remark}' )" \
                    "".format(
                        orderID=cID,
                        storeID=each["wm_poi_id"],
                        num=each["num"],
                        status=iStatus,
                        order_time=each["order_time"],
                        estimate_arrival_time=int(time.mktime(time.strptime(each["estimate_arrival_time_fmt"], "%Y-%m-%d %H:%M:%S"))),
                        consumerID=each["user_id"],
                        remark=each["remark"]
                    )
                self.data_handle(sSqlJ, False, sSqlH)
                # 订单明细
                lItem = []
                for bag in each["cartDetailVos"]:
                    lItem.extend(bag["details"])
                self.detail_page_order_detail(cID, each["wm_poi_id"], each["order_time"], lItem)
                # 备餐
                if len(sUrl_prepare) == 0:
                    sUrl_prepare = r"http://e.waimai.meituan.com/v2/order/receive/processed/r/orderAsyncInfos/v3?orderInfos="
                    sUrl_prepare += r"%5B"
                else:
                    sUrl_prepare += r"%2C"
                sUrl_prepare += r"%7B%22wmOrderViewId%22%3A%22"
                sUrl_prepare += each["wm_order_id_view_str"]
                sUrl_prepare += r"%22%2C%22wmPoiId%22%3A{storeID}%2C%22cityId%22%3A{cityID}%7D".format(storeID=response.save["varDict"]["wmPoiId"], cityID=response.save["varDict"]["cityId"])
                # 配送
                if len(sUrl_delivery) == 0:
                    sUrl_delivery = r"http://e.waimai.meituan.com/v2/order/receive/processed/r/distribute/list/v2?orderInfos="
                    sUrl_delivery += r"%5B"
                else:
                    sUrl_delivery += r"%2C"
                sUrl_delivery += r"%7B%22wmOrderViewId%22%3A%22"
                sUrl_delivery += each["wm_order_id_view_str"]
                sUrl_delivery += r"%22%2C%22wmPoiId%22%3A{storeID}%2C%22logisticsStatus%22%3A40%2C%22logisticsCode%22%3A%222002%22%7D".format(storeID=response.save["varDict"]["wmPoiId"])
                # 结算
                listSettle.append({"wmOrderViewId": each["wm_order_id_view_str"], "wmPoiId": int(response.save["varDict"]["wmPoiId"])})
            sUrl_prepare += r"%5D&region_id={region_id}&region_version={region_version}".format(
                region_id=response.save["varDict"]["region_id"],
                region_version=response.save["varDict"]["region_version"]
            )
            self.crawl(sUrl_prepare, headers=response.save["headers_order"], age=0, retries=1, callback=self.detail_page_prepare)
            sUrl_delivery += r"%5D&region_id={region_id}&region_version={region_version}".format(
                region_id=response.save["varDict"]["region_id"],
                region_version=response.save["varDict"]["region_version"]
            )
            self.crawl(sUrl_delivery, headers=response.save["headers_order"], age=0, retries=1, callback=self.detail_page_delivery)
            # 注释以下3行代码，暂不需要抓取结算数据
            # sData = json.dumps(listSettle, ensure_ascii = False).replace(' ', '')
            # sItag = str(response.save["varDict"]["wmPoiId"]) + datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f") + str(cID)
            # self.crawl(sUrl_settle + "#" + sItag, method="POST", data={"chargeInfo": sData}, headers=response.save["headers_settle"], itag=sItag, age=0, retries=1, callback=self.detail_page_settle)
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))

    def detail_page_order_detail(self, orderID, storeID, order_time, itemList):
        """
        解析订单明细
        """
        try:
            for each in itemList:
                itemID=each["wm_food_id"]
                itemName=each["food_name"]
                unit=each["unit"]
                sSqlJ = r"select 1 from order_detail where orderID={orderID} and itemID={itemID} and itemName='{itemName}' and unit='{unit}'" \
                    "".format(
                        orderID=orderID,
                        itemID=itemID,
                        itemName=itemName,
                        unit=unit
                    )
                sSqlH = r"insert into order_detail ( orderID, storeID, order_time, itemID, itemName, unit, priceOri, price, qty, amt ) " \
                    r"values ( {orderID}, {storeID}, {order_time}, {itemID}, '{itemName}', '{unit}', {priceOri}, {price}, {qty}, {amt} )" \
                    "".format(
                        orderID=orderID,
                        storeID=storeID,
                        order_time=order_time,
                        itemID=itemID,
                        itemName=itemName,
                        unit=unit,
                        priceOri=each["origin_food_price"],
                        price=each["food_price"],
                        qty=each["count"],
                        amt=round(each["food_price"] * each["count"], 2)
                    )
                self.data_handle(sSqlJ, False, sSqlH)
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))

    @config(priority=2)
    def detail_page_prepare(self, response):
        """
        解析备餐数据
        """
        try:
            if type(response.content).__name__ == "bytes":
                response.content = (response.content).decode('utf-8')
            if not response or not response.json["data"]:
                return {"info": "获取备餐数据失败"}
            for key in response.json["data"]:
                sSqlJ = r"select 1 from order_main where erpID = {orderID}".format(orderID=key)
                sSqlH = r"update order_main set prepare_time = {prepare_time} where erpID = {orderID}".format(prepare_time=response.json["data"][key]["prepareDuration"], orderID=key)
                self.data_handle(sSqlJ, True, sSqlH)
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))

    @config(priority=2)
    def detail_page_delivery(self, response):
        """
        解析配送数据
        """
        try:
            if type(response.content).__name__ == "bytes":
                response.content = (response.content).decode('utf-8')
            if not response or not response.json["data"]:
                return {"info": "获取配送数据失败"}
            for key in response.json["data"]:
                sSqlJ = r"select 1 from order_main where erpID = {orderID}".format(orderID=key)
                sSqlH = r"update order_main set delivery_time = {delivery_time} where erpID = {orderID}".format(delivery_time=response.json["data"][key]["latest_delivery_time"], orderID=key)
                self.data_handle(sSqlJ, True, sSqlH)
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))

    @config(priority=2)
    def detail_page_settle(self, response):
        """
        解析结算数据
        """
        try:
            if type(response.content).__name__ == "bytes":
                response.content = (response.content).decode('utf-8')
            if not response or not response.json["data"]:
                return {"info": "获取结算数据失败"}
            for each in response.json["data"]:
                cID = int(each["wmOrderViewIdStr"])
                sSqlJ = r"select 1 from order_main where erpID = {orderID}".format(orderID=cID)
                sSqlH = r"update order_main set settle_time = {settle_time} where erpID = {orderID}".format(settle_time=each["utime"], orderID=cID)
                self.data_handle(sSqlJ, True, sSqlH)
        except Exception as e:
            self.operlog(0, 1, -1, None, None, str(e))

    def on_finished(self, response, task):
        """
        """
        if self.bConnected:
            self.operlog(0, 1, 0, None, None, "")
            self.db.close()
            self.bConnected = False
