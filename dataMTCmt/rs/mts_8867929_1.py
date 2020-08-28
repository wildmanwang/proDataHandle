#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-07-17 17:45:04
# Project: mts_8867929_1

# OK 抓订单主数据
# OK 抓备餐、配送、结算等数据
# OK 抓订单明细
# OK 自动分析cookie，减少手动配置
# OK 判断订单状态，根据状态更新订单内容

# 说明：刚部署时，应抓取前一周的订单数据，以便和评价匹配

from pyspider.libs.base_handler import *
import json
import datetime, time
import random
import pymysql

COOKIE_ORDER = r"_lxsdk_cuid=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; ci=30; rvct=30; device_uuid=!9c8e93c5-c909-4a89-9ec7-f6f7af88bfd7; uuid_update=true; acctId=69702070; brandId=-1; wmPoiId=8867929; isOfflineSelfOpen=0; city_id=440307; isChain=0; existBrandPoi=false; ignore_set_router_proxy=false; region_id=1000440300; region_version=1586416007; newCategory=false; logistics_support=1; cityId=440300; provinceId=440000; city_location_id=440300; location_id=440307; pushToken=0ppHHkDn1TwPEytvO3-DQbs_P25JbKCAxdQUHu8xL2d8*; _lxsdk=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; logan_custom_report=; bsid=qXqkpeJB7eUygZ-ROc0I-o39HjxyKetgmAF82unErJFXHh_KagGUyGOTJ58u6IoGcfk1z1SoOKc-cY10HrO6vg; token=0Zi2G0xnVI2Rw3CU54XKk4qFebkUQ1925Axykyc4fWbU*; set_info=%7B%22wmPoiId%22%3A8867929%2C%22region_id%22%3A%221000440300%22%2C%22region_version%22%3A1586416007%7D; setPrivacyTime=1_20200828; logan_session_token=ktom0czjaqbt7xyf3vrq; JSESSIONID=ybglvnqsoam1vpsson0623vz; _lxsdk_s=17432c5aff8-258-c49-184%7C%7C28"

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "0Wangle?",
    "dbname": "mt_orderinfo"
}

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
        self.sDate10StartOrder = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")
        self.sDate10EndOrder = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")
        self.sDate8EndOrder = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y%m%d")

        self.strParse = []
        self.cookie_order = COOKIE_ORDER
        self.cookie_order = self.source_replace(self.cookie_order, "setPrivacyTime", "1_" + datetime.datetime.strftime(datetime.date.today(), "%Y%m%d"))
        self.strParse.append(self.cookie_order)
        self.varDict = {}
        self.source_parse(self.strParse)
        
        self.headers_order = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://e.waimai.meituan.com/v2/order/new/history?region_id=1000440300&region_version={region_version}".format(region_version=self.varDict["region_version"]),
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": self.cookie_order
        }
        
        self.headers_settle = self.headers_order.copy()
        self.headers_settle["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers_settle["Origin"] = "http://e.waimai.meituan.com"

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
        for strSource in strList:
            for line in strSource.split('; '):
                key, value = line.split('=', 1)
                self.varDict[key] = value

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
            print(sHandle)
            print(str(e))
            self.db.rollback()
    
    def data_select(self, sSelect):
        """
        获取数据集
        """
        try:
            cur = self.db.cursor()
            cur.execute("set names utf8mb4")
            cur.execute("SET CHARACTER SET utf8mb4")
            cur.execute("SET character_set_connection=utf8mb4")
            cur.execute(sSelect)
            rsData = cur.fetchall()
        except Exception as e:
            print(sSelect)
            print(str(e))
    
    @every(minutes=24 * 60 * 1000)
    def on_start(self):
        self.bConnected = False
        try:
            self.db = pymysql.connect(host=db_config["host"], user=db_config["user"], password=db_config["password"], database=db_config["dbname"], charset="utf8mb4", use_unicode=True)
            self.bConnected = True
        except Exception as e:
            print(str(e))
        # 获取订单
        sUrl_order = r"http://e.waimai.meituan.com/v2/order/common/history/all/r/list?" \
            r"lastLabel=&nextLabel=&userId=-1&tag=all&startDate={dateStart}&endDate={dateEnd}" \
            r"&region_id=1000440300&region_version=1586416007" \
            "".format(
                dateStart=self.sDate10StartOrder,
                dateEnd=self.sDate10EndOrder
            )
        self.crawl(sUrl_order, headers=self.headers_order, age=2*60, retries=0, callback=self.index_page)

    @config(age=2 * 60)
    def index_page(self, response):
        if not response or not response.json["data"] or not response.json["data"]["wmOrderList"]:
            return {"info": "获取订单首页失败"}
        if len(response.json["data"]["wmOrderList"]) > 0:
            iNum = response.json["data"]["wmOrderList"][0]["num"]
            self.detail_page_order(response)
            iNum -= 10
        else:
            iNum = 0
        while iNum > 0:
            sUrl = r"http://e.waimai.meituan.com/v2/order/common/history/all/r/list?lastLabel=&nextLabel=" \
                r"%7B%22day%22%3A{date8}%2C%22day_seq%22%3A{num}%2C%22page%22%3A0%2C%22setDay_seq%22%3Atrue%2C%22setPage%22%3Afalse%2C%22setDay%22%3Atrue%7D" \
                r"&userId=-1&tag=all&startDate={dateStart}&endDate={dateEnd}&region_id=1000440300&region_version=1586416007" \
                "".format(
                    date8=self.sDate8EndOrder,
                    num=iNum+1,
                    dateStart=self.sDate10StartOrder,
                    dateEnd=self.sDate10EndOrder
                )
            iNum -= 10
            time.sleep(random.randint(5,15))
            self.crawl(sUrl, headers=self.headers_order, age=2*60, retries=0, callback=self.detail_page_order)

    @config(priority=2)
    def detail_page_order(self, response):
        """
        解析订单数据
        """
        if not response or not response.json["data"] or not response.json["data"]["wmOrderList"]:
            return {"info": "获取订单数据失败"}
        sUrl_prepare = ""
        sUrl_delivery = ""
        sUrl_settle = r"http://e.waimai.meituan.com/v2/order/receive/r/chargeInfo?region_id=1000440300&region_version=1586416007"
        listSettle = []
        for each in response.json["data"]["wmOrderList"]:
            cID = int(each["wm_order_id_view_str"])
            iStatus = each["status"]
            sSqlJ = r"select 1 from order_main where erpID = {erpID} and status < {status}".format(erpID=cID, status=iStatus)
            sSqlH = r"delete from order_main where erpID = {erpID}".format(erpID=cID)
            self.data_handle(sSqlJ, True, sSqlH)
            sSqlJ = r"select 1 from order_main where erpID = {erpID}".format(erpID=cID)
            sSqlH = r"insert into order_main ( erpID, storeID, num, status, order_time, estimate_arrival_time, consumerID ) " \
                r"values ( {erpID}, {storeID}, {num}, {status}, {order_time}, {estimate_arrival_time}, {consumerID} )" \
                "".format(
                    erpID=cID,
                    storeID=each["wm_poi_id"],
                    num=each["num"],
                    status=iStatus,
                    order_time=each["order_time"],
                    estimate_arrival_time=int(time.mktime(time.strptime(each["estimate_arrival_time_fmt"], "%Y-%m-%d %H:%M:%S"))),
                    consumerID=each["user_id"]
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
            sUrl_prepare += r"%22%2C%22wmPoiId%22%3A{storeID}%2C%22cityId%22%3A{cityID}%7D".format(storeID=self.varDict["wmPoiId"], cityID=self.varDict["cityId"])
            # 配送
            if len(sUrl_delivery) == 0:
                sUrl_delivery = r"http://e.waimai.meituan.com/v2/order/receive/processed/r/distribute/list/v2?orderInfos="
                sUrl_delivery += r"%5B"
            else:
                sUrl_delivery += r"%2C"
            sUrl_delivery += r"%7B%22wmOrderViewId%22%3A%22"
            sUrl_delivery += each["wm_order_id_view_str"]
            sUrl_delivery += r"%22%2C%22wmPoiId%22%3A{storeID}%2C%22logisticsStatus%22%3A40%2C%22logisticsCode%22%3A%222002%22%7D".format(storeID=self.varDict["wmPoiId"])
            # 结算
            listSettle.append({"wmOrderViewId": each["wm_order_id_view_str"], "wmPoiId": int(self.varDict["wmPoiId"])})
        sUrl_prepare += r"%5D&region_id=1000440300&region_version=1586416007"
        self.crawl(sUrl_prepare, headers=self.headers_order, age=0, retries=0, callback=self.detail_page_prepare)
        sUrl_delivery += r"%5D&region_id=1000440300&region_version=1586416007"
        self.crawl(sUrl_delivery, headers=self.headers_order, age=0, retries=0, callback=self.detail_page_delivery)
        # 注释以下3行代码，暂不需要抓取结算数据
        # sData = json.dumps(listSettle, ensure_ascii = False).replace(' ', '')
        # sItag = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S") + str(cID)
        # self.crawl(sUrl_settle + "#" + sItag, method="POST", data={"chargeInfo": sData}, headers=self.headers_settle, itag=sItag, age=0, retries=0, callback=self.detail_page_settle)

    def detail_page_order_detail(self, orderID, storeID, order_time, itemList):
        """
        解析订单明细
        """
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

    @config(priority=2)
    def detail_page_prepare(self, response):
        """
        解析备餐数据
        """
        if not response or not response.json["data"]:
            return {"info": "获取备餐数据失败"}
        for key in response.json["data"]:
            sSqlJ = r"select 1 from order_main where erpID = {erpID}".format(erpID=key)
            sSqlH = r"update order_main set prepare_time = {prepare_time} where erpID = {erpID}".format(prepare_time=response.json["data"][key]["prepareDuration"], erpID=key)
            self.data_handle(sSqlJ, True, sSqlH)

    @config(priority=2)
    def detail_page_delivery(self, response):
        """
        解析配送数据
        """
        if not response or not response.json["data"]:
            return {"info": "获取配送数据失败"}
        for key in response.json["data"]:
            sSqlJ = r"select 1 from order_main where erpID = {erpID}".format(erpID=key)
            sSqlH = r"update order_main set delivery_time = {delivery_time} where erpID = {erpID}".format(delivery_time=response.json["data"][key]["latest_delivery_time"], erpID=key)
            self.data_handle(sSqlJ, True, sSqlH)

    @config(priority=2)
    def detail_page_settle(self, response):
        """
        解析结算数据
        """
        if not response or not response.json["data"]:
            return {"info": "获取结算数据失败"}
        for each in response.json["data"]:
            cID = int(each["wmOrderViewIdStr"])
            sSqlJ = r"select 1 from order_main where erpID = {erpID}".format(erpID=cID)
            sSqlH = r"update order_main set settle_time = {settle_time} where erpID = {erpID}".format(settle_time=each["utime"], erpID=cID)
            self.data_handle(sSqlJ, True, sSqlH)

    def on_finished(self, response, task):
        """
        """
        if self.bConnected:
            self.db.close()
            self.bConnected = False
