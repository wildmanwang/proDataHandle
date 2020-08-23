#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-07-17 17:45:04
# Project: mts_8867929

from pyspider.libs.base_handler import *
import json
import datetime, time
import random
import pymysql

COOKIE_ORDER = r"_lxsdk_cuid=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; ci=30; rvct=30; " \
    r"device_uuid=u00219c8e93c5-c909-4a89-9ec7-f6f7af88bfd7; uuid_update=true; " \
    r"bsid=Q8dwerZl-dvkqU7uCQAiUUAT_MaezTmTAb40Lqiv69T71BveoOJ0aA6jCn2OjJRR-JrKIO4jT-jDjZaHOC0ERQ; " \
    r"acctId=69702070; brandId=-1; wmPoiId=8867929; isOfflineSelfOpen=0; city_id=440307; isChain=0; " \
    r"existBrandPoi=false; ignore_set_router_proxy=false; region_id=1000440300; region_version=1586416007; " \
    r"newCategory=false; logistics_support=1; cityId=440300; provinceId=440000; city_location_id=440300; " \
    r"location_id=440307; pushToken=0ppHHkDn1TwPEytvO3-DQbs_P25JbKCAxdQUHu8xL2d8*; " \
    r"wpush_server_url=wss://wpush.meituan.com; logan_custom_report=; " \
    r"_lxsdk=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; setPrivacyTime=2_20200712; " \
    r"token=0hpSpYFVPvN_quA8ZvhDmeinI-sukt5WpQfbO1fdUNLM*; " \
    r"set_info=%7B%22wmPoiId%22%3A8867929%2C%22region_id%22%3A%221000440300%22%2C%22region_version%22%3A1586416007%7D; " \
    r"shopCategory=food; logan_session_token=zcorofgl60tu69pzpaut; JSESSIONID=45nrg6u4jo7halzh9kmcmmad; " \
    r"_lxsdk_s=1735cd0dedd-ba0-23f-443%7C69702070%7C15"
COOKIE_ORDER = r"_lxsdk_cuid=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; ci=30; rvct=30; " \
    r"device_uuid=!9c8e93c5-c909-4a89-9ec7-f6f7af88bfd7; uuid_update=true; acctId=69702070; brandId=-1; " \
    r"wmPoiId=8867929; isOfflineSelfOpen=0; city_id=440307; isChain=0; existBrandPoi=false; " \
    r"ignore_set_router_proxy=false; region_id=1000440300; region_version=1586416007; newCategory=false; " \
    r"logistics_support=1; cityId=440300; provinceId=440000; city_location_id=440300; location_id=440307; " \
    r"pushToken=0ppHHkDn1TwPEytvO3-DQbs_P25JbKCAxdQUHu8xL2d8*; _lxsdk=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; " \
    r"wpush_server_url=wss://wpush.meituan.com; logan_custom_report=; " \
    r"bsid=4FsVIF-uyN6xKwuMGqw3_Pbwldg9fusI8N-HAhzy4QfBs4OKly3hfcujKRx9973XbV61OVQkzoNbZjkSRsHpAQ; token=0ikoyJpFlY7nA2wgs3CG878igmckJBVAnhQL-RY8Fulg*; " \
    r"set_info=%7B%22wmPoiId%22%3A8867929%2C%22region_id%22%3A%221000440300%22%2C%22region_version%22%3A1586416007%7D; " \
    r"setPrivacyTime=2_20200721; shopCategory=food; logan_session_token=jt9aedkak9sm99y8lngr; " \
    r"JSESSIONID=10tfmvzw39l4eractxernwxxd; _lxsdk_s=1737458f371-cce-a82-b79%7C69702070%7C16"
COOKIE_ORDER = r"_lxsdk_cuid=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; ci=30; rvct=30; " \
    r"device_uuid=u00219c8e93c5-c909-4a89-9ec7-f6f7af88bfd7; uuid_update=true; acctId=69702070; brandId=-1; " \
    r"wmPoiId=8867929; isOfflineSelfOpen=0; city_id=440307; isChain=0; existBrandPoi=false; " \
    r"ignore_set_router_proxy=false; region_id=1000440300; region_version=1586416007; newCategory=false; " \
    r"logistics_support=1; cityId=440300; provinceId=440000; city_location_id=440300; location_id=440307; " \
    r"pushToken=0ppHHkDn1TwPEytvO3-DQbs_P25JbKCAxdQUHu8xL2d8*; _lxsdk=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; " \
    r"bsid=hXikqjd__8HzkBEdQ3Na2GOMbWoWHGdATAO0oOle0H82yoQk6bTS14nvFnHswlJAeS3L3MlIbvW4yg2YCUa-JQ; token=0zPtX38YdinGCksHuhW-QW_zFJxhJ0mbIQOnQF7OnsFg*; " \
    r"wpush_server_url=wss://wpush.meituan.com; shopCategory=food; logan_custom_report=; " \
    r"set_info=%7B%22wmPoiId%22%3A8867929%2C%22region_id%22%3A%221000440300%22%2C%22region_version%22%3A1586416007%7D; " \
    r"setPrivacyTime=1_20200724; logan_session_token=a721hg9jgyl97trxflx5; " \
    r"JSESSIONID=m2fon23tr8z71k6sqfqm52is4; _lxsdk_s=1737fa905ec-3c1-8ce-1b%7C%7C17"

COOKIE_COMMENT = r"_lxsdk_cuid=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; ci=30; rvct=30; " \
    r"acctId=69702070; wmPoiId=8867929; bizad_cityId=440307; bizad_second_city_id=440300; bizad_third_city_id=440307; " \
    r"wmPoiName=%E7%89%9B%E5%AE%B6%E4%BA%BA%E5%A4%A7%E7%A2%97%E7%89%9B%E8%82%89%E9%9D%A2%EF%BC%88%E5%B8%83%E5%90%89%E9%BB%91%E9%87%91%E5%BA%97%EF%BC%89; " \
    r"_lxsdk=172ff28d6a6c8-046a7ed55deba9-5d462912-1fa400-172ff28d6a6c8; uuid=4fb8048b12d00dc0ee8b.1594726664.1.0.0; " \
    r"token=0zPtX38YdinGCksHuhW-QW_zFJxhJ0mbIQOnQF7OnsFg*; bsid=hXikqjd__8HzkBEdQ3Na2GOMbWoWHGdATAO0oOle0H82yoQk6bTS14nvFnHswlJAeS3L3MlIbvW4yg2YCUa-JQ; " \
    r"_lxsdk_s=1739dc24301-60f-afa-9da%7C69702070%7C11"

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
        self.sDate10End = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")
        self.sDate8End = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y%m%d")
        self.sDate10StartOrder = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=2),"%Y-%m-%d")
        self.sDate10StartComment = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=3),"%Y-%m-%d")

        self.strParse = []
        self.cookie_order = COOKIE_ORDER
        self.strParse.append(self.cookie_order)
        self.cookie_comment = COOKIE_COMMENT
        sllf.strParse.append(self.cookie_comment)
        self.varDict = {}
        self.source_parse(sllf.strParse)
        
        self.headers_order = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://e.waimai.meituan.com/v2/order/new/history?region_id=1000440300&region_version={region_version}".format(region_version=self.varDict["region_version"]),
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": self.cookieOrder
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
            "Cookie": self.cookieComment
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
            "endDate": self.sDate10End,
            "timeType": "4",
            "commentKeyWord": ""
        }

    def source_parse(self, strList):
        for strSource in strList:
            for line in strSource.split('; '):
                key, value = line.split('=', 1)
                slef.varDict[key] = value

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
                dateEnd=self.sDate10End
            )
        self.crawl(sUrl_order, headers=headers_order, age=2*60, retries=0, callback=self.index_page)
        time.sleep(random.randint(30,60))
        # 获取评价
        sUrl_comment = r"https://waimaieapp.meituan.com/gw/api/customer/comment/r/list?ignoreSetRouterProxy=true"
        data_comment["pageNum"] = "1"
        self.crawl(sUrl_comment, method="POST", data=data_comment, headers=headers_comment, age=2*60, retries=0, validate_cert=False, callback=self.index_comment)

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
                    date8=self.sDate8End,
                    num=iNum+1,
                    dateStart=self.sDate10StartOrder,
                    dateEnd=self.sDate10End
                )
            iNum -= 10
            time.sleep(random.randint(5,15))
            self.crawl(sUrl, headers=headers_order, age=2*60, retries=0, callback=self.detail_page_order)

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
            sSqlH = r"insert into order_main ( erpID, storeID, status, order_time, estimate_arrival_time, consumerID, privacy_phone1 ) " \
                r"values ( {erpID}, {storeID}, {status}, {order_time}, {estimate_arrival_time}, {consumerID}, '{privacy_phone1}' )" \
                "".format(
                    erpID=cID,
                    storeID=each["wm_poi_id"],
                    status=iStatus,
                    order_time=each["order_time"],
                    estimate_arrival_time=int(time.mktime(time.strptime(each["estimate_arrival_time_fmt"], "%Y-%m-%d %H:%M:%S"))),
                    consumerID=each["user_id"],
                    privacy_phone1=each["privacy_phone"]
                )
            self.data_handle(sSqlJ, False, sSqlH)
            # 订单明细
            lItem = []
            for bag in each["cartDetailVos"]:
                lItem.extend(bag["details"])
            self.detail_page_order_detail(cID, lItem)
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
        self.crawl(sUrl_prepare, headers=headers_order, age=0, retries=0, callback=self.detail_page_prepare)
        sUrl_delivery += r"%5D&region_id=1000440300&region_version=1586416007"
        self.crawl(sUrl_delivery, headers=headers_order, age=0, retries=0, callback=self.detail_page_delivery)
        sData = json.dumps(listSettle, ensure_ascii = False).replace(' ', '')
        sItag = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S") + str(cID)
        self.crawl(sUrl_settle + "#" + sItag, method="POST", data={"chargeInfo": sData}, headers=headers_settle, itag=sItag, age=0, retries=0, callback=self.detail_page_settle)

    def detail_page_order_detail(self, orderID, itemList):
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
            sSqlH = r"insert into order_detail ( orderID, itemID, itemName, unit, priceOri, price, qty, amt ) " \
                r"values ( {orderID}, {itemID}, '{itemName}', '{unit}', {priceOri}, {price}, {qty}, {amt} )" \
                "".format(
                    orderID=orderID,
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
            data_comment["pageNum"] = str(iNum)
            time.sleep(random.randint(5,15))
            sItag = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S") + str(iNum)
            self.crawl(sUrl_comment + "#" + sItag, method="POST", data=data_comment, headers=headers_comment, itag=sItag, age=0, retries=0, validate_cert=False, callback=self.detail_page_comment)
    
    @config(priority=2)
    def detail_page_comment(self, response):
        """
        解析评价数据
        """
        if not response or not response.json["data"] or not response.json["data"]["comments"]:
            return {"info": "获取评价数据失败"}
        for each in response.json["data"]["comments"]:
            cID = each["id"]
            sSqlJ = r"select 1 from comment_main where erpID = {erpID}".format(erpID=cID)
            sSqlH = r"insert into comment_main ( erpID, storeID, comment_str, order_score, food_score, delivery_score, package_score, taste_score, " \
                r"ship_score, quality_score, comment_time, ship_duration, over_duration ) " \
                r"value ( {erpID}, {storeID}, '{comment_str}', {order_score}, {food_score}, {delivery_score}, {package_score}, {taste_score}, " \
                r"{ship_score}, {quality_score}, {comment_time}, {ship_duration}, {over_duration} )".format(
                    erpID=cID,
                    storeID=self.varDict["wmPoiId"],
                    comment_str=str(each["comment"]),
                    order_score=each["order_comment_score"],
                    food_score=each["food_comment_score"],
                    delivery_score=each["delivery_comment_score"],
                    package_score=each["packaging_score"],
                    taste_score=each["taste_score"],
                    ship_score=each["ship_score"],
                    quality_score=each["quality_score"],
                    comment_time=each["ctime"],
                    ship_duration=each["ship_time"],
                    over_duration=each["overDeliveryTime"]
                )
            self.data_handle(sSqlJ, False, sSqlH)
            if each["orderStatus"]["details"]:
                self.detail_page_comment_detail(cID, each["orderStatus"]["details"])

    def detail_page_comment_detail(self, commentID, itemList):
        """
        解析评价详情
        """
        for each in itemList:
            sSqlJ = r"select 1 from comment_detail where commentID = {commentID} and itemName = '{itemName}'".format(commentID=commentID, itemName=each["food_name"])
            sSqlH = r"insert into comment_detail ( commentID, itemName ) values ( {commentID}, '{itemName}' )".format(commentID=commentID, itemName=each["food_name"])
            self.data_handle(sSqlJ, False, sSqlH)

    def on_finished(self, response, task):
        """
        """
        if self.bConnected:
            pass
            self.db.close()
            self.bConnected = False
