#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-07-17 17:45:04
# Project: mts_8867929_2

# OK 抓评价主数据
# OK 抓评价明细、点踩、点赞
# OK 自动分析cookie，减少手动配置
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
    1 评价数据 comment
    """
    crawl_config = {
    }

    def __init__(self):
        self.sDate10StartComment = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")
        self.sDate10EndComment = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")

        self.strParse = []
        self.cookie_order = COOKIE_ORDER
        self.cookie_order = self.source_replace(self.cookie_order, "setPrivacyTime", "1_" + datetime.datetime.strftime(datetime.date.today(), "%Y%m%d"))
        self.strParse.append(self.cookie_order)
        self.cookie_comment = COOKIE_COMMENT
        self.strParse.append(self.cookie_comment)
        self.varDict = {}
        self.source_parse(self.strParse)
        
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
        # 获取评价
        sUrl_comment = r"https://waimaieapp.meituan.com/gw/api/customer/comment/r/list?ignoreSetRouterProxy=true"
        self.crawl(sUrl_comment, method="POST", data=self.data_comment, headers=self.headers_comment, age=2*60, retries=0, validate_cert=False, callback=self.index_comment)

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
                r"ship_score, quality_score, comment_time, data_time, to_time, ship_duration, over_duration ) " \
                r"value ( {erpID}, {storeID}, '{userName}', '{comment_str}', {order_score}, {food_score}, {delivery_score}, {package_score}, {taste_score}, " \
                r"{ship_score}, {quality_score}, {comment_time}, {data_time}, {to_time}, {ship_duration}, {over_duration} )".format(
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
                    to_time=each["ctime"],
                    ship_duration=each["ship_time"],
                    over_duration=each["overDeliveryTime"]
                )
            self.data_handle(sSqlJ, False, sSqlH)
            # 商品明细
            if each["orderStatus"]["details"]:
                self.detail_page_comment_detail(cID, self.varDict["wmPoiId"], each["ctime"], 1, each["orderStatus"]["details"])
                if each["showOrderInfo"]:
                    sSqlH = r"update comment_main set to_time = {to_time} where erpID = {erpID} and to_time > {to_time}".format(
                            to_time=int(time.time()) - each["showOrderInfoTime"] * 60 * 60,
                            erpID=cID
                        )
                    self.data_handle(sSqlJ, False, sSqlH)
            else:
                if each["showOrderInfo"]:
                    sSqlH = r"update comment_main set from_time = {from_time} where erpID = {erpID} and from_time < {from_time}".format(
                            from_time=int(time.time()) - each["showOrderInfoTime"] * 60 * 60 - 60,
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
