# -*- coding:utf-8 -*-
"""
消息处理
"""

class MsgJYKX():
    def __init__(self):
        self._secretStr = "2211800a308a8863cee1bdbca5ace192"
        self._templateId = "7EzOwl5fmyxe1CKvec9z3ya_kZO42k5rQZxMNLHmSoc"

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

    def send_msg(self, person, sStore, msgs, iCnt, msgFlag):
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
        import urllib.request
        import urllib.parse
        import time
        import json
        rtnData = {
            "result": False,  # 逻辑控制 True/False
            "info": "",  # 信息
            "dataString": "",  # 字符串
            "dataNumber": 0,  # 数字
            "entities": {}
        }
        url = r"http://jy.erpit.cn/api/message/send-user"
        try:
            nCntAll = len(msgs)            # 需要处理的评价数
            nCntOK = 0                      # 精确定位的评价数
            # 组合文字
            sCmt = "门店名称：{storeName}".format(storeName=sStore)
            iNum = 0
            for line in msgs:
                iNum += 1
                sCmt += "\r\n【{msgFlag}{num}/{cnt}】".format(msgFlag=msgFlag, num=iNum, cnt=nCntAll).ljust(20, "—")
                sCmt += "\r\n评价时间：{comment_time}".format(comment_time=self._prtTime(line["comment_time"]))
                sCmt += "\r\n评分总分：{order_score}".format(order_score=line["order_score"])
                sCmt += "\r\n评价内容：{commentStr}".format(commentStr=line["commentStr"])
                if len(line["orderList"]) == 0:
                    if line["pic_cnt"] > 0:
                        sCmt += "\r\n没有匹配到订单，也许您从评价的图片能看出点什么"
                    else:
                        sCmt += "\r\n没有匹配到订单，评价信息量实在是太少..."
                elif len(line["orderList"]) == 1:
                    sCmt += "\r\n下单时间：{order_time}".format(order_time=self._prtTime(line["orderList"][0]["order_time"]))
                    sCmt += "\r\n订单序号：{orderNum}".format(orderNum=line["orderList"][0]["orderNum"])
                    sCmt += "\r\n订单编号：{orderID}".format(orderID=line["orderList"][0]["orderID"])
                    sCmt += "\r\n回访截止：{callbackTime}".format(callbackTime=self._prtTime(line["orderList"][0]["callbackTime"]))
                    nCntOK += 1
                else:
                    if line["pic_cnt"] > 0:
                        sCmt += "\r\n匹配到{num}条订单，也许您从评价的图片能看出点什么:".format(num=len(line["orderList"]))
                    else:
                        sCmt += "\r\n匹配到{num}条订单，没法再精确了：".format(num=len(line["orderList"]))
                    iOrderNo = 0
                    for orderItem in line["orderList"]:
                        iOrderNo += 1
                        sCmt += "\r\n{num}.{no}".format(num=iNum, no=iOrderNo)
                        sCmt += "\r\n下单时间：{order_time}".format(order_time=self._prtTime(orderItem["order_time"]))
                        sCmt += "\r\n订单序号：{orderNum}".format(orderNum=orderItem["orderNum"])
                        sCmt += "\r\n订单编号：{orderID}".format(orderID=orderItem["orderID"])
                        sCmt += "\r\n回访截止：{callbackTime}".format(callbackTime=self._prtTime(orderItem["callbackTime"]))
                        if orderItem["order_remark"]:
                            sCmt += "\r\n订单备注：{order_remark}".format(order_remark=orderItem["order_remark"])
            data_dict = {
                "secret": self._secretStr,
                "uid": person,
                "template_id": self._templateId,
                "url": "",
                "data": {
                    'first': {
                        'value': '数据服务',
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
                        'value': sCmt,
                        'color': '#173177'
                    },
                }
            }
            headers = {'content-type': 'application/json'}
            dData = json.dumps(data_dict)
            dData = bytes(dData, "utf8")
            request = urllib.request.Request(url, headers=headers, data=dData)
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
