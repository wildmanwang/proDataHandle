评价时间大于送达时间
商品精确匹配（数量和名称匹配）
评价商品匹配（名称模糊匹配）
送达时间匹配（四舍五入、进位？）
超时时间匹配

评价时间匹配：
	1天内评论可以打电话回访，有效匹配
    2天内评论合情合理
    取时间最短的记录
select from_unixtime(1597855142)
select * from mt_orderinfo.comment_main where left(from_unixtime(comment_time), 10) < '2020-08-21' order by sID desc;
select * from mt_orderinfo.comment_main where erpID = 3584812922;
select * from mt_orderinfo.comment_detail where commentID = 3584812922;
select	erpID, 
		from_unixtime(order_time) 下单时间,
		from_unixtime(delivery_time) 送达时间,
		from_unixtime(1597855142) 评价时间,
		(estimate_arrival_time - order_time)/60 预计时长,
		(delivery_time - order_time)/60 实际时长（按秒）,
		floor(delivery_time/60) - floor(order_time/60) 实际时长（按分舍尾）,
		round(delivery_time/60) - round(order_time/60) 实际时长（按分舍入）,
		ceil(delivery_time/60) - ceil(order_time/60) 实际时长（按分进位）,
        (((1597855142 - delivery_time)/60)/60)/24 收到多久评价,
        (1597855142 - delivery_time)/60 收到多久评价 
from order_main where delivery_time < 1597855142 and erpID in (select orderID from t2) and delivery_time - order_time >= 43 * 60 and delivery_time - order_time < 45 * 60 and estimate_arrival_time > delivery_time;
from order_main where delivery_time < 1598007179 and delivery_time - order_time > 30 * 60 and delivery_time - order_time < 32 * 60 and estimate_arrival_time > delivery_time
and abs((((1598007179 - delivery_time)/60)/60)/24 - round((((1598007179 - delivery_time)/60)/60)/24)) < 0.1 order by abs((((1598007179 - delivery_time)/60)/60)/24 - round((((1598007179 - delivery_time)/60)/60)/24)) asc;
and (estimate_arrival_time - order_time)/60 between 46 and 48
from order_main where erpID = 88679290075602343;
select * from order_detail where orderID in (select orderID from t2) and itemName like '招牌！香辣牛肉面（大）（辣）%';
select erpID, from_unixtime(order_time), num from order_main where erpID = 88679290066038059;
select * from order_detail where orderID in (88679290661019997, 88679290066038059);

招牌！香辣牛肉面 （大碗）（不辣）
蒜-想熏死我的领导
香菜-我就好这口

truncate table t1;
truncate table t2;

select * from t1;
select * from t2;

insert t2( orderID ) 
select distinct orderID from mt_orderinfo.order_detail where order_time < 1597855142 and orderID in (select orderID from t1) and itemName like '香菜-我就好这口%';
select distinct orderID from mt_orderinfo.order_detail where order_time < 1597855142 group by orderID having count(*) = 3;
select distinct orderID from mt_orderinfo.order_detail where order_time < 1597855142 and itemName like '大碗炸酱面+卤蛋+牛肉丸（2个）套餐%' group by orderID having count(*) = 1;
select distinct orderID from mt_orderinfo.order_detail where order_time < 1597855142 and itemName like '卤蛋1个(需配面条，单点不送哦）%';

update mt_orderinfo.comment_main set orderID = 0 where sID = 1;

insert into relation_test ( commentID, orderID, comment_time ) values ( 3584812922, 88679291752717855, 1597855142 );
