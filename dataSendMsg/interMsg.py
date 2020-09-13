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

    def send_msg(self, person, sStore, msgs, iCnt):
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
        rtn = {}
        url = r"http://jy.erpit.cn/api/message/send-user"
        try:
            nCnt = len(msgs)
            # 组合文字
            sCmt = "门店名称：{storeName}".format(storeName=sStore)
            iNum = 0
            for line in msgs:
                iNum += 1
                sCmt += "\r\n{num}/{cnt}".format(num=iNum, cnt=nCnt).ljust(20, "—")
                sCmt += "\r\n评价时间：{cmtTime}".format(cmtTime=self._prtTime(line["cmtTime"]))
                sCmt += "\r\n评分总分：{orderScore}".format(orderScore=line["orderScore"])
                sCmt += "\r\n评价内容：{cmtStr}".format(cmtStr=line["cmtStr"])
                sCmt += "\r\n下单时间：{orderTime}".format(orderTime=self._prtTime(line["orderTime"]))
                sCmt += "\r\n订单序号：{orderNum}".format(orderNum=line["orderNum"])
                sCmt += "\r\n订单编号：{orderID}".format(orderID=line["orderID"])
                sCmt += "\r\n回访截止：{callbackTime}".format(callbackTime=self._prtTime(line["callbackTime"]))
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
                        'value': '昨日{cnt}条差评，找到{num}条对应订单号'.format(cnt=iCnt, num=nCnt) if iCnt > 0 else '昨日0差评',
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
            rtn = response.read().decode("unicode_escape")
        except Exception as e:
            rtn["errInfo"] = str(e)
        return rtn

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
