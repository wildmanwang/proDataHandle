#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-07-17 17:45:04
# Project: mts_8867929

# OK 抓订单主数据
# OK 抓备餐、配送、结算等数据
# OK 抓评价主数据
# OK 抓订单明细、评价明细、点踩、点赞
# OK 自动分析cookie，减少手动配置
# OK 判断订单状态，根据状态更新订单内容
# OK 判断评价分数，不抓取满分评价

# 说明：刚部署时，应抓取前一周的订单数据，以便和评价匹配

from pyspider.libs.base_handler import *
import json
import datetime, time
import random
import pymysql

COOKIE_ORDER = r"_lxsdk_cuid=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; ci=30; rvct=30; " \
    r"device_uuid=!9c8e93c5-c909-4a89-9ec7-f6f7af88bfd7; uuid_update=true; acctId=69702070; brandId=-1; " \
    r"wmPoiId=8867929; isOfflineSelfOpen=0; city_id=440307; isChain=0; existBrandPoi=false; " \
    r"ignore_set_router_proxy=false; region_id=1000440300; region_version=1586416007; newCategory=false; " \
    r"logistics_support=1; cityId=440300; provinceId=440000; city_location_id=440300; location_id=440307; " \
    r"pushToken=0ppHHkDn1TwPEytvO3-DQbs_P25JbKCAxdQUHu8xL2d8*; _lxsdk=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; " \
    r"bsid=hXikqjd__8HzkBEdQ3Na2GOMbWoWHGdATAO0oOle0H82yoQk6bTS14nvFnHswlJAeS3L3MlIbvW4yg2YCUa-JQ; token=073owTRp7D7bEJkbMdNgeP35qw-WD5W9iLGU87bkCw9g*; " \
    r"wpush_server_url=wss://wpush.meituan.com; shopCategory=food; logan_custom_report=; " \
    r"set_info=%7B%22wmPoiId%22%3A8867929%2C%22region_id%22%3A%221000440300%22%2C%22region_version%22%3A1586416007%7D; " \
    r"setPrivacyTime=1_20200821; logan_session_token=ofpanm4w8pu694rwrppe; " \
    r"JSESSIONID=1g34pl0vkrlamxvslypobquak; _lxsdk_s=1740f15f4e3-1d4-c87-829%7C69702070%7C6"

COOKIE_COMMENT = r"_lxsdk_cuid=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; ci=30; rvct=30; " \
    r"acctId=69702070; wmPoiId=8867929; bizad_cityId=440307; bizad_second_city_id=440300; bizad_third_city_id=440307; " \
    r"wmPoiName=%E7%89%9B%E5%AE%B6%E4%BA%BA%E5%A4%A7%E7%A2%97%E7%89%9B%E8%82%89%E9%9D%A2%EF%BC%88%E5%B8%83%E5%90%89%E9%BB%91%E9%87%91%E5%BA%97%EF%BC%89; " \
    r"_lxsdk=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; uuid=4fb8048b12d00dc0ee8b.1594726664.1.0.0; " \
    r"bsid=hXikqjd__8HzkBEdQ3Na2GOMbWoWHGdATAO0oOle0H82yoQk6bTS14nvFnHswlJAeS3L3MlIbvW4yg2YCUa-JQ; token=073owTRp7D7bEJkbMdNgeP35qw-WD5W9iLGU87bkCw9g*; " \
    r"_lxsdk_s=1740f15f4e3-1d4-c87-829%7C69702070%7C13"

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
    5 评价数据 comment
    """
    crawl_config = {
    }

    def __init__(self):
        self.sDate10StartOrder = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")
        self.sDate10StartComment = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")
        
        self.sDate10EndOrder = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")
        self.sDate8EndOrder = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y%m%d")
        self.sDate10EndComment = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")

        self.strParse = []
        self.cookie_order = COOKIE_ORDER
        self.strParse.append(self.cookie_order)
        self.cookie_comment = COOKIE_COMMENT
        self.strParse.append(self.cookie_comment)
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
        
        self.refer_comment = r"https://waimaieapp.meituan.com/frontweb/userComment?" \
            r"_source=PC&token={token}&acctId={acctId}&wmPoiId={wmPoiId}&region_id={region_id}" \
            r"&device_uuid={device_uuid}&bsid={bsid}&appType=3&fromPoiChange=false" \
            "".format(
                token = self.varDict["token"],
                acctId = self.varDict["acctId"],
                wmPoiId = self.varDict["wmPoiId"],
                region_id = self.varDict["region_id"],
                device_uuid = self.varDict["device_uuid"],
                bsid = self.varDict["bsid"]
            )
        self.headers_comment = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://waimaieapp.meituan.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": self.refer_comment,
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": self.cookie_comment
        }
        self.data_comment = {
            "token": self.varDict["token"],
            "acctId": self.varDict["acctId"],
            "wmPoiId": self.varDict["wmPoiId"],
            "bsid": self.varDict["bsid"],
            "appType": "3",
            "pageNum": "1",
            "rate": "-1",
            "reply": "-1",
            "context": "-1",
            "startDate": self.sDate10StartComment,
            "endDate": self.sDate10EndComment,
            "timeType": "4",
            "commentKeyWord": ""
        }

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
            cur.execute(sSelect)
            rsData = cur.fetchall()
        except Exception as e:
            print(sSelect)
            print(str(e))
    
    @every(minutes=24 * 60 * 1000)
    def on_start(self):
        self.bConnected = False
        try:
            self.db = pymysql.connect(host=db_config["host"], user=db_config["user"], password=db_config["password"], database=db_config["dbname"], charset="utf8")
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
        time.sleep(random.randint(30,60))
        # 获取评价
        sUrl_comment = r"https://waimaieapp.meituan.com/gw/api/customer/comment/r/list?ignoreSetRouterProxy=true"
        self.crawl(sUrl_comment, method="POST", data=self.data_comment, headers=self.headers_comment, age=2*60, retries=0, validate_cert=False, callback=self.index_comment)

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

    @config(age=2 * 60)
    def index_comment(self, response):
        if not response or not response.json["data"] or not response.json["data"]["pageCount"]:
            return {"info": "获取评价首页失败"}
        pageNum = response.json["data"]["pageCount"]
        if pageNum > 0:
            self.detail_page_comment(response)
            iNum = 1
        else:
            iNum = 0
        sUrl_comment = r"https://waimaieapp.meituan.com/gw/api/customer/comment/r/list?ignoreSetRouterProxy=true"
        while iNum < pageNum:
            iNum += 1
            self.data_comment["pageNum"] = str(iNum)
            time.sleep(random.randint(5,15))
            sItag = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S") + str(iNum)
            self.crawl(sUrl_comment + "#" + sItag, method="POST", data=self.data_comment, headers=self.headers_comment, itag=sItag, age=0, retries=0, validate_cert=False, callback=self.detail_page_comment)
    
    @config(priority=2)
    def detail_page_comment(self, response):
        """
        解析评价数据
        """
        if not response or not response.json["data"] or not response.json["data"]["comments"]:
            return {"info": "获取评价数据失败"}
        for each in response.json["data"]["comments"]:
            cID = each["id"]
            iScore = each["order_comment_score"]
            # 测试阶段，把全部评价下载下来
            # if iScore == 5:
            #     continue
            sSqlJ = r"select 1 from comment_main where erpID = {erpID}".format(erpID=cID)
            sSqlH = r"insert into comment_main ( erpID, storeID, userName, comment_str, order_score, food_score, delivery_score, package_score, taste_score, " \
                r"ship_score, quality_score, comment_time, data_time, ship_duration, over_duration ) " \
                r"value ( {erpID}, {storeID}, '{userName}', '{comment_str}', {order_score}, {food_score}, {delivery_score}, {package_score}, {taste_score}, " \
                r"{ship_score}, {quality_score}, {comment_time}, {data_time}, {ship_duration}, {over_duration} )".format(
                    erpID=cID,
                    storeID=self.varDict["wmPoiId"],
                    userName=each["username"],
                    comment_str=str(each["comment"]),
                    order_score=iScore,
                    food_score=each["food_comment_score"],
                    delivery_score=each["delivery_comment_score"],
                    package_score=each["packaging_score"],
                    taste_score=each["taste_score"],
                    ship_score=each["ship_score"],
                    quality_score=each["quality_score"],
                    comment_time=each["ctime"],
                    data_time=int(time.time()),
                    ship_duration=each["ship_time"],
                    over_duration=each["overDeliveryTime"]
                )
            self.data_handle(sSqlJ, False, sSqlH)
            # 商品明细
            if each["orderStatus"]["details"]:
                self.detail_page_comment_detail(cID, self.varDict["wmPoiId"], each["ctime"], 1, each["orderStatus"]["details"])
            else:
                if each["showOrderInfo"]:
                    sSqlH = r"update comment_main set from_time = {from_time} where erpID = {erpID}".format(
                            from_time=int(time.time()) - each["showOrderInfoTime"] * 60 * 60 + 60,
                            erpID=cID
                        )
                    self.data_handle("", False, sSqlH)
            # 点踩
            if len(each["critic_food_list"]) > 0:
                self.detail_page_comment_detail(cID, self.varDict["wmPoiId"], each["ctime"], 2, each["critic_food_list"])
            # 点赞
            if len(each["praise_food_list"]) > 0:
                self.detail_page_comment_detail(cID, self.varDict["wmPoiId"], each["ctime"], 3, each["praise_food_list"])

    def detail_page_comment_detail(self, commentID, storeID, comment_time, itemSource, itemList):
        """
        解析评价详情
        """
        for each in itemList:
            if itemSource == 1:
                itemName = each["food_name"]
            else:
                itemName = each
            sSqlJ = r"select 1 from comment_detail where commentID = {commentID} and itemSource = {itemSource} and itemName = '{itemName}'".format(
                commentID=commentID, 
                itemSource=itemSource, 
                itemName=itemName
            )
            sSqlH = r"insert into comment_detail ( commentID, storeID, comment_time, itemSource, itemName ) values ( {commentID}, {storeID}, {comment_time}, {itemSource}, '{itemName}' )".format(
                commentID=commentID, 
                storeID=storeID, 
                comment_time=comment_time, 
                itemSource=itemSource, 
                itemName=itemName
            )
            self.data_handle(sSqlJ, False, sSqlH)

    def on_finished(self, response, task):
        """
        """
        if self.bConnected:
            pass
            self.db.close()
            self.bConnected = False
