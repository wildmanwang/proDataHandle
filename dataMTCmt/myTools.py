# -*- coding:utf-8 -*-
"""
自定义工具类
"""
__author__ = "Cliff.wang"

import json
from decimal import Decimal

class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        else:
            return super().default(o)
