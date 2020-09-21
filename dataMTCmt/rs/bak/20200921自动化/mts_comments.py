#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-09-10 18:32:18
# Project: mts_comments

from pyspider.libs.base_handler import *
import json
import datetime, time
import random
import pymysql

class Handler(BaseHandler):
    """
    1 评价数据 comment
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
            self.operlog(0, 2, -1, None, None, str(e))
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
            self.operlog(0, 2, -1, None, None, str(e))
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
            lsSql = r"insert into oper_log ( storeID, busi_type, step, begin_date, end_date, remark ) " \
                    r"values ( {storeID}, {busi_type}, {step}, {begin_date}, {end_date}, '{remark}' ) ".format(
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
            print(lsSql)
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
            self.operlog(0, 2, 1, None, None, "")
            lsSql = r"select erpID, initFlag, cookie_order, cookie_comment from store_info where status = 1 and cookie_order is not null and cookie_comment is not null order by level asc, createTime asc"
            ldCol = ["storeID", "initFlag", "cookie_order", "cookie_comment"]
            rsStore = self.data_select(lsSql, ldCol)
            for rcStore in rsStore:
                storeVar = {}
                if rcStore["initFlag"] == 1:
                    iFromDays = 3
                else:
                    iFromDays = 6
                storeVar["sDate10StartComment"] = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=iFromDays),"%Y-%m-%d")
                storeVar["sDate10EndComment"] = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),"%Y-%m-%d")

                strParse = []
                storeVar["cookie_order"] = rcStore["cookie_order"]
                storeVar["cookie_order"] = self.source_replace(storeVar["cookie_order"], "setPrivacyTime", "1_" + datetime.datetime.strftime(datetime.date.today(), "%Y%m%d"))
                strParse.append(storeVar["cookie_order"])
                storeVar["cookie_comment"] = rcStore["cookie_comment"]
                strParse.append(storeVar["cookie_comment"])
                storeVar["varDict"] = self.source_parse(strParse)
                
                storeVar["refer_comment"] = r"https://waimaieapp.meituan.com/frontweb/userComment?" \
                    r"_source=PC&token={token}&acctId={acctId}&wmPoiId={wmPoiId}&region_id={region_id}" \
                    r"&device_uuid={device_uuid}&bsid={bsid}&appType=3&fromPoiChange=false" \
                    "".format(
                        token = storeVar["varDict"]["token"],
                        acctId = storeVar["varDict"]["acctId"],
                        wmPoiId = storeVar["varDict"]["wmPoiId"],
                        region_id = storeVar["varDict"]["region_id"],
                        device_uuid = storeVar["varDict"]["device_uuid"],
                        bsid = storeVar["varDict"]["bsid"]
                    )
                storeVar["headers_comment"] = {
                    "Connection": "keep-alive",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://waimaieapp.meituan.com",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": storeVar["refer_comment"],
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cookie": storeVar["cookie_comment"]
                }
                storeVar["data_comment"] = {
                    "token": storeVar["varDict"]["token"],
                    "acctId": storeVar["varDict"]["acctId"],
                    "wmPoiId": storeVar["varDict"]["wmPoiId"],
                    "bsid": storeVar["varDict"]["bsid"],
                    "appType": "3",
                    "pageNum": "1",
                    "rate": "-1",
                    "reply": "-1",
                    "context": "-1",
                    "startDate": storeVar["sDate10StartComment"],
                    "endDate": storeVar["sDate10EndComment"],
                    "timeType": "4",
                    "commentKeyWord": ""
                }
                # 获取评价
                sUrl_comment = r"https://waimaieapp.meituan.com/gw/api/customer/comment/r/list?ignoreSetRouterProxy=true"
                sItag = str(rcStore["storeID"]) + "1" + datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f")
                self.crawl(sUrl_comment + "#" + sItag, method="POST", data=storeVar["data_comment"], headers=storeVar["headers_comment"], itag=sItag, age=2*60, retries=2, validate_cert=False, callback=self.index_comment, save=storeVar)
                self.operlog(rcStore["storeID"], 2, 2, storeVar["sDate10StartComment"], storeVar["sDate10EndComment"], "")
                time.sleep(random.randint(5,15))
        except Exception as e:
            self.operlog(0, 2, -1, None, None, str(e))

    @config(age=2 * 60)
    def index_comment(self, response):
        if type(response.content).__name__ == "bytes":
            response.content = (response.content).decode('utf-8')
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
            response.save["data_comment"]["pageNum"] = str(iNum)
            time.sleep(random.randint(5,15))
            sItag = str(response.save["varDict"]["wmPoiId"]) + str(iNum) + datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f")
            self.crawl(sUrl_comment + "#" + sItag, method="POST", data=response.save["data_comment"], headers=response.save["headers_comment"], itag=sItag, age=0, retries=2, validate_cert=False, callback=self.detail_page_comment)
    
    @config(priority=2)
    def detail_page_comment(self, response):
        """
        解析评价数据
        """
        if type(response.content).__name__ == "bytes":
            response.content = (response.content).decode('utf-8')
        if not response or not response.json["data"] or not response.json["data"]["comments"]:
            return {"info": "获取评价数据失败"}
        for each in response.json["data"]["comments"]:
            cID = each["id"]
            sSqlJ = r"select 1 from comment_main where erpID = {commentID}".format(commentID=cID)
            sSqlH = r"insert into comment_main ( erpID, storeID, order_score, food_score, delivery_score, package_score, taste_score, " \
                r"ship_score, quality_score, pic_cnt, comment_time, data_time, to_time, ship_duration, over_duration, consumerSName, comment_str ) " \
                r"value ( {commentID}, {storeID}, {order_score}, {food_score}, {delivery_score}, {package_score}, {taste_score}, " \
                r"{ship_score}, {quality_score}, {pic_cnt}, {comment_time}, {data_time}, {to_time}, {ship_duration}, {over_duration}, '{consumerSName}', '{comment_str}' )".format(
                    commentID=cID,
                    storeID=each["wm_poi_id"],
                    order_score=each["order_comment_score"],
                    food_score=each["food_comment_score"],
                    delivery_score=each["delivery_comment_score"],
                    package_score=each["packaging_score"],
                    taste_score=each["taste_score"],
                    ship_score=each["ship_score"],
                    quality_score=each["quality_score"],
                    pic_cnt=len(each["picture_urls"]),
                    comment_time=each["ctime"],
                    data_time=int(time.time()),
                    to_time=each["ctime"],
                    ship_duration=each["ship_time"],
                    over_duration=each["overDeliveryTime"],
                    consumerSName=each["username"],
                    comment_str=str(each["comment"])
                )
            self.data_handle(sSqlJ, False, sSqlH)
            # 商品明细
            if each["orderStatus"]["details"]:
                self.detail_page_comment_detail(cID, each["wm_poi_id"], each["ctime"], 1, each["orderStatus"]["details"])
                sSqlH = r"update comment_main set to_time = {to_time} where erpID = {commentID} and to_time > {to_time}".format(
                        to_time=int(time.time()) - each["showOrderInfoTime"] * 60 * 60,
                        commentID=cID
                    )
                self.data_handle("", False, sSqlH)
            else:
                sSqlH = r"update comment_main set from_time = {from_time} where erpID = {commentID} and from_time < {from_time}".format(
                        from_time=int(time.time()) - each["showOrderInfoTime"] * 60 * 60 - 60,
                        commentID=cID
                    )
                self.data_handle("", False, sSqlH)
            # 点踩
            if len(each["critic_food_list"]) > 0:
                self.detail_page_comment_detail(cID, each["wm_poi_id"], each["ctime"], 2, each["critic_food_list"])
            # 点赞
            if len(each["praise_food_list"]) > 0:
                self.detail_page_comment_detail(cID, each["wm_poi_id"], each["ctime"], 3, each["praise_food_list"])

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
            self.operlog(0, 2, 0, None, None, "")
            self.db.close()
            self.bConnected = False
