美团外卖商家中心
	http://e.waimai.meituan.com/
	username:wmdwnr249780
	password:wm1234

加工数据样板：
	恭喜已定位到差评订单号
	平台：美团外卖 
	门店：牛家人大碗牛肉面（布吉黑金店）
	订单号：39
	订单编号：88679293044539137
	客户下单次数：1
	订单是否超过48小时：48小时内
	订单时间：2020-05-27 06:51:51
	客户实际支付金额：18.89
	回访有效时间：0小时24分35.027秒
	订单完成时间：2020-05-27 07:26:55
	客户名称：刘(先生)
	客户电话：13049813424,0208,13164714121 转 9511
	订单内容：冬季暖汤-鱼丸汤(需配面条单点不送哦),蒜-想熏死我的领导,老北京炸酱面(大),
	订单备注：无
	评价内容：面是冷的，味道不行
	评分：1

I'm doing:
错误日志发送
自动爬取、分析、发送

next to do:
部署爬虫到云端
部署分析程序到云端
部署消息发送服务到云端
客户管理后台
    密码登录客户自动登录
    短信验证登录客户自动登录
    短信验证客户过期提醒
    客户信息接收人管理
    服务有效期管理
    多级分销管理

how to do?
根据备注来识别（如果识别结果大于1小于5，也可发给客户供人工识别？）
动态IP爬虫（是否导致登录失败需要验证码？）

done:
2020-09-21  产品名称确定：云通科技、云通数据服务

规则：
    送达24小时后订单的隐私号码失效
    送达48小时后评价的商品明细显示
    订单商品明细、评价商品明细：带做法；
    评价踩赞明细：不带做法；

客户要求：
    设置密码
    关闭“店铺设置-账号设置-首次登录验证手机”
    开启“店铺设置-账号设置-平台运营长期登录”

reference:
定时任务：
https://blog.csdn.net/weixin_42935779/article/details/104187454
连多数据库：
https://www.cnblogs.com/sunxiuwen/p/9655932.html
解决mysql客户端安装及版本错误的问题：
https://blog.csdn.net/lvluobo/article/details/107850673
自动创建爬虫任务：
https://www.py.cn/faq/python/17827.html
https://www.cnblogs.com/lincappu/p/12911412.html
https://www.cnblogs.com/chengxuyuanaa/p/12042083.html

problem:
    美团服务几点中断？仅一次发现中断，在23:58左右
    美团几点可以查询前一天的评价数据？01:20不可查；06:40可查
    订单一次能查多少数据？超过62后面的取不到，导致初始化店铺无法一次性查6天

技术问题：
报错：'cryptography' package is required for sha256_password or caching_sha2_password auth methods
    解决：重启电脑，mysql服务器有问题
    原因：未知
错误：抓取的数据整页中文乱码，其他页面正常
    解决：抓取到数据后，增加语句response.content = (response.content).decode('utf-8')
    原因：pyspider内置的pyquery没有正确的解析目标站的编码，导致的解码失败；这就是 lxml 的蛋疼之处，给它 unicode 它有的时候它不认，给它 bytes 它又处理不好