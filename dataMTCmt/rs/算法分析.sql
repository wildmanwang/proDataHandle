select sID, erpID, ship_duration, comment_time, userName, comment_str, order_score, taste_score, delivery_score from mt_orderinfo.comment_main where left(from_unixtime(comment_time), 10) >= '2020-08-26' order by sID desc;
select sID, userName, comment_str, order_score, food_score, taste_score, delivery_score, package_score, comment_time, from_time, to_time, ship_duration, over_duration from comment_main where erpID = 3608017670;
select * from comment_detail where commentID = 3610431631;
select	erpID, 
		from_unixtime(order_time) 下单时间,
		from_unixtime(delivery_time) 送达时间,
		from_unixtime(1598203785) 评价时间,
		(estimate_arrival_time - order_time)/60 预计时长,
		(delivery_time - order_time)/60 实际时长（按秒）,
		floor(delivery_time/60) - floor(order_time/60) 实际时长（按分舍尾）,
		round(delivery_time/60) - round(order_time/60) 实际时长（按分舍入）,
		ceil(delivery_time/60) - ceil(order_time/60) 实际时长（按分进位）,
        (((1598203785 - delivery_time)/60)/60)/24 收到多久评价,
        (1598203785 - delivery_time)/60 收到多久评价 
from order_main where delivery_time < 1598203785 and erpID in (select orderID from t2) and delivery_time - order_time >= 24 * 60 and delivery_time - order_time < 29 * 60 and estimate_arrival_time > delivery_time;
from order_main where delivery_time < 1598365719 and order_time between 1598326955 and 1598365719 and delivery_time - order_time > 31 * 60 and delivery_time - order_time < 36 * 60 and estimate_arrival_time > delivery_time
from order_main where erpID = 88679290890902196;
and abs((((1598195195 - delivery_time)/60)/60)/24 - round((((1598195195 - delivery_time)/60)/60)/24)) < 0.1 order by abs((((1598195195 - delivery_time)/60)/60)/24 - round((((1598195195 - delivery_time)/60)/60)/24)) asc;
and (estimate_arrival_time - order_time)/60 between 46 and 48
select * from order_detail where orderID in (select orderID from t2) and itemName like '招牌！香辣牛肉面（大）（辣）%';
select erpID, from_unixtime(order_time), num from order_main where erpID = 88679290066038059;
select * from order_main where erpID = 88679292742235259;
select * from order_detail where orderID in (88679290890902196);

招牌！香辣牛肉面（大）（不辣）

truncate table t1;
truncate table t2;

select * from t1;
select * from t2;

insert t2( orderID ) 
select distinct orderID from mt_orderinfo.order_detail where order_time between 0 and 1598194499 and orderID in (select orderID from t1) and itemName like '招牌！香辣牛肉面（大）（不辣）';
select distinct orderID from mt_orderinfo.order_detail where order_time between 0 and 1598194499 group by orderID having count(*) = 1;

update mt_orderinfo.comment_main set orderID = 0 where sID = 1;

insert into test_relation ( commentID, orderID, comment_time ) values ( 3599959098, 88679293871876947, 1598193001 );

select erpID, (delivery_time - order_time)/60 from order_main where erpID = '88679290661019997';
3597168513	23	1598154806	88679293091803107	18.8-40=0			4	4.2
3597494955	32	1598157578	88679291624344390	28.72-40=0			3	3.28
3599272818	56	1598181868	88679292840903245	51.75-50=2			4	4.25
3599274243	46	1598181886	88679292173841887	42.37-46=0			4	3.63
3599362080	49	1598182987	88679290180074891	44.7-40=5			4	4.3
3599959098	36	1598193001	88679293871876947	36.38-40=0				-0.38
3592540794	25	1598029614	88679293089632125	22.13-40=0			3	2.87
3592947077	18	1598063379	88679292011040185	15.95-40=0			2	2.05
3593569535	37	1598070415	88679290275958126	36.5-45=0				0.5
3595000915	45	1598091055	88679293304657349	45.08-40=6				-0.08
3595355755	58	1598095430	88679291091703748	55.85-40=16			2	2.15
3595391638	42	1598095896	88679292245165932	41.6-40=2				0.4
3595677026	32	1598099878	88679292086419988	22.55-40=0			9	8.45		!!!!!!!!!!!!!!!!!!!!!!!!!!
3589982440	24	1597985580	88679290661019997	22.77-42=0			1	1.23
3589308082	39	1597979915	88679293467950645	34.93-40=0			4	4.07
3589461721	22	1597981420	88679292623184363	17.57-40=0			4	4.43
3589681050	32	1597983221	88679291436352694	30.87-40=0			1	1.13
3590461887	33	1597991579	88679290802511030	29.07-40=0			4	3.93
3591177772	20	1598004183	88679294104073005	16.18-40=0			4	3.82
3591491998	29	1598008173	88679290172538673	25.13-40=0			4	3.87
3584812922	44	1597855142	88679290066038059	41.32-44=0			3	2.68
3584950431	37	1597872117	88679292677733532	35.18-40=0			2	1.82
3585722205	42	1597896009	88679291000512031	42.27-41=2				-0.27
3585850084	412	1597896983	88679290075602343	408.70-422.42=0		4	3.3
3585975524	140	1597897919	88679292011786547	136.65-150.45=0		3	3.35
3586001249	41	1597898115	88679290908368516	39.25-40=0			2	1.75
3586085612	55	1597898777	88679294110288693	53.30-46=8			2	1.7
3586286390	136	1597900583	88679292769130430	135.1-146.55=0		1	0.9
3588126252	41	1597928072	88679292884831435	40.52-40=2				0.48
3588318578	63	1597931684	88679293560493064	60.57-55=6			2	2.43
3588518881	42	1597936235	88679293456420143	38.5-48=0			3	3.5
3588551995	18	1597937086	88679291613437106	17.15-40=0			1	0.85
