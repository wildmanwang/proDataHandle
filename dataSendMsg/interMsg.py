# -*- coding:utf-8 -*-
"""
消息处理
"""

class MsgJYKX():
    def __init__(self):
        self._secretStr = "2211800a308a8863cee1bdbca5ace192"
        self._templateId = "7EzOwl5fmyxe1CKvec9z3ya_kZO42k5rQZxMNLHmSoc"
        self.sysParas = {}

    def get_user_list(self):
        import urllib.request
        rtn = {}
        url = r"http://jy.erpit.cn/api/userlist?secret={secret}".format(secret=self._secretStr)
        try:
            response = urllib.request.urlopen(url)
            rtn = response.read().decode("unicode_escape")
        except Exception as e:
            rtn["errInfo"] = str(e)
        return rtn

    def sendMsgCmt(self, person, sStore, msgs, iCnt, msgFlag):
        """
        发消息
            person:     人员ID
            msgs:[{
                cmtTime,        评价时间
                orderScore,     订单评分
                cmtStr,         评价内容
                orderTime,      评价时间
                orderNum,       订单序号
                orderID,        订单ID
                callbackTime,   超时时间
                sureFlag        确认标志
            }]
        消息模板说明：
            监控告警通知：7EzOwl5fmyxe1CKvec9z3ya_kZO42k5rQZxMNLHmSoc
            {{first}}
            告警名称：{{keyword1}}
            告警时间：{{keyword2}}
            告警描述：{{keyword3}}
            {{remark}}
        """
        import time
        rtnData = {
            "result": False,  # 逻辑控制 True/False
            "info": "",  # 信息
            "dataString": "",  # 字符串
            "dataNumber": 0,  # 数字
            "entities": {}
        }
        try:
            nCntAll = len(msgs)            # 需要处理的评价数
            nCntOK = 0                      # 精确定位的评价数
            # 组合文字
            sMsg = "门店名称：{storeName}".format(storeName=sStore)
            iNum = 0
            for line in msgs:
                iNum += 1
                sMsg += "\r\n【{msgFlag}{num}/{cnt}】".format(msgFlag=msgFlag, num=iNum, cnt=nCntAll).ljust(20, "—")
                sMsg += "\r\n评价时间：{comment_time}".format(comment_time=self._prtTime(line["comment_time"]))
                sMsg += "\r\n评分总分：{order_score}".format(order_score=line["order_score"])
                sMsg += "\r\n评价内容：{commentStr}".format(commentStr=line["commentStr"])
                if len(line["orderList"]) == 0:
                    if line["pic_cnt"] > 0:
                        sMsg += "\r\n没有匹配到订单，也许您从评价的图片能看出点什么"
                    else:
                        sMsg += "\r\n没有匹配到订单，评价信息量实在是太少..."
                elif len(line["orderList"]) == 1:
                    sMsg += "\r\n下单时间：{order_time}".format(order_time=self._prtTime(line["orderList"][0]["order_time"]))
                    sMsg += "\r\n订单序号：{orderNum}".format(orderNum=line["orderList"][0]["orderNum"])
                    sMsg += "\r\n订单编号：{orderID}".format(orderID=line["orderList"][0]["orderID"])
                    sMsg += "\r\n回访截止：{callbackTime}".format(callbackTime=self._prtTime(line["orderList"][0]["callbackTime"]))
                    nCntOK += 1
                else:
                    if line["pic_cnt"] > 0:
                        sMsg += "\r\n匹配到{num}条订单，也许您从评价的图片能看出点什么:".format(num=len(line["orderList"]))
                    else:
                        sMsg += "\r\n匹配到{num}条订单，没法再精确了：".format(num=len(line["orderList"]))
                    iOrderNo = 0
                    for orderItem in line["orderList"]:
                        iOrderNo += 1
                        sMsg += "\r\n{num}.{no}".format(num=iNum, no=iOrderNo)
                        sMsg += "\r\n下单时间：{order_time}".format(order_time=self._prtTime(orderItem["order_time"]))
                        sMsg += "\r\n订单序号：{orderNum}".format(orderNum=orderItem["orderNum"])
                        sMsg += "\r\n订单编号：{orderID}".format(orderID=orderItem["orderID"])
                        sMsg += "\r\n回访截止：{callbackTime}".format(callbackTime=self._prtTime(orderItem["callbackTime"]))
                        if orderItem["order_remark"]:
                            sMsg += "\r\n订单备注：{order_remark}".format(order_remark=orderItem["order_remark"])
            data_dict = {
                'first': {
                    'value': '{serviceFlag}数据服务'.format(serviceFlag=self.sysParas["serviceFlag"]),
                    'color': '#173177'
                },
                'keyword1': {
                    'value': '美团客户满意度',
                    'color': '#173177'
                },
                'keyword2': {
                    'value': self._prtTime(time.time()),
                    'color': '#173177'
                },
                'keyword3': {
                    'value': '昨日{cnt}条{msgFlag}，精确匹配{num}条{msgFlag}'.format(cnt=iCnt, msgFlag=msgFlag, num=nCntOK) if iCnt > 0 else '昨日0{msgFlag}'.format(msgFlag=msgFlag),
                    'color': '#173177'
                },
                'remark': {
                    'value': sMsg,
                    'color': '#173177'
                },
            }
            rtnData = self._send_msg(self._secretStr, person, self._templateId, "", data_dict)
        except Exception as e:
            rtnData["info"] = str(e)
        return rtnData

    def sendMsgLog(self, msgs):
        """
        发消息
            person:     人员ID
            msgs:[{
                oper_time,      操作时间
                storeID,        商家ID列表
                busi_type,      业务类型
                step,           日志类型
                begin_date,     业务开始日期
                end_date,       业务截止日期
                remark          备注
            }]
        消息模板说明：
            监控告警通知：7EzOwl5fmyxe1CKvec9z3ya_kZO42k5rQZxMNLHmSoc
            {{first}}
            告警名称：{{keyword1}}
            告警时间：{{keyword2}}
            告警描述：{{keyword3}}
            {{remark}}
        """
        import time
        rtnData = {
            "result": False,  # 逻辑控制 True/False
            "info": "",  # 信息
            "dataString": "",  # 字符串
            "dataNumber": 0,  # 数字
            "entities": {}
        }
        try:
            nCntAll = len(msgs)            # 需要处理的评价数
            # 组合文字
            sMsg = "日志异常报警"
            iNum = 0
            for line in msgs:
                iNum += 1
                sMsg += "\r\n【异常日志{num}/{cnt}】".format(num=iNum, cnt=nCntAll).ljust(20, "—")
                sMsg += "\r\n操作时间：{oper_time}".format(oper_time=self._prtTime(line["oper_time"]))
                sMsg += "\r\n商家 ID：{storeID}".format(storeID=line["storeID"])
                sMsg += "\r\n业务类型：{busi_type}-{step}".format(busi_type=line["busi_type"], step=line["step"])
                sMsg += "\r\n起止日期：{begin_date}-{end_date}".format(begin_date=line["begin_date"], end_date=line["end_date"])
                sMsg += "\r\n日志内容：{remark}".format(remark=line["remark"])
                if iNum >= 3:
                    sMsg += "\r\n更多异常见系统日志..."
                    break
            data_dict = {
                'first': {
                    'value': '{serviceFlag}数据服务'.format(serviceFlag=self.sysParas["serviceFlag"]),
                    'color': '#173177'
                },
                'keyword1': {
                    'value': '日志异常报警',
                    'color': '#173177'
                },
                'keyword2': {
                    'value': self._prtTime(time.time()),
                    'color': '#173177'
                },
                'keyword3': {
                    'value': '昨日共产生{cnt}条异常日志'.format(cnt=len(msgs)),
                    'color': '#173177'
                },
                'remark': {
                    'value': sMsg,
                    'color': '#173177'
                },
            }
            for person in self.sysParas["errLogRecipient"]:
                rtnData = self._send_msg(self._secretStr, person, self._templateId, "", data_dict)
        except Exception as e:
            rtnData["info"] = str(e)
        return rtnData

    def _send_msg(self, secret, uid, template_id, url, data):
        """
        发消息
            secret          系统分配给您的密钥，在用户中心查看
            uid             接收消息人员的ID，通过用户列表获得
            template_id     消息模板ID
            url             消息点击跳转链接,用于消息查看详情，可不填
            data            这是您的消息内容, 参照消息模板列表中的使用说明中的具体参数
        """
        import urllib.request
        import urllib.parse
        import json
        rtnData = {
            "result": False,  # 逻辑控制 True/False
            "info": "",  # 信息
            "dataString": "",  # 字符串
            "dataNumber": 0,  # 数字
            "entities": {}
        }
        request_url = r"http://jy.erpit.cn/api/message/send-user"
        try:
            # 组合参数
            data_dict = {
                "secret": secret,
                "uid": uid,
                "template_id": template_id,
                "url": url,
                "data": data
            }
            headers = {'content-type': 'application/json'}
            dData = json.dumps(data_dict)
            dData = bytes(dData, "utf8")
            request = urllib.request.Request(request_url, headers=headers, data=dData)
            response = urllib.request.urlopen(request)
            opRtn = response.read().decode("unicode_escape")
            opRtn = json.loads(opRtn)
            if opRtn["code"] == 200:
                rtnData["result"] = True
            rtnData["info"] = opRtn["msg"]
        except Exception as e:
            rtnData["info"] = str(e)
        return rtnData

    def _prtTime(self, lTime):
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lTime))

if __name__ == "__main__":
    msg = MsgJYKX()
    rtn = msg.get_user_list()
    print(rtn)
    rtn = msg.send_msg(5421, "测试门店", "", 3)        # 王
    #rtn = msg.send_msg(5402, "测试门店", "", 3)        # 何
    print(rtn)
