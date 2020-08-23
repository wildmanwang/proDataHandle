/*
订单时间：orderlist1orders.order_time
送达时间：orderlist4dispatchs.latest_delivery_time
评价时间：ordercomments.ctime

【时间关系判定】-模糊判定
	订单时间 < 评价时间 < 订单时间 + 12小时
	送达时间 < 评价时间 < 送达时间 + 60分钟
【商品明细判定】-直接判定
	订单商品：cartDetailVos[]
	评价商品：
		praise_food_list[]		商品名称直接判定，大部分空
		critic_food_list[]		商品名称直接判定，大部分空
		orderStatus.details[]	猜测为时效性字段，大部分空
		comment					商品名称模糊判定，大部分空，有也难判断，可以建立简称词语库辅助判断

update orderlist4dispatchs
set wm_poi_id = CONVERT(nvarchar(50),CONVERT(decimal(28,0), convert(float, wm_poi_id)))

3405719405	1593704979	36	88679293282891287
3405240668	1593693026	56
3405030962	1593689566	42	88679291588494815
3404927549	1593688032	20
3404773898	1593685826	31-
3404611521	1593683360	45	88679291326327211
3404394508	1593679038	42
3404185157	1593673668	37-	88679291643513272	88679290211668595
3403946520	1593668538	29	88679291963112241
3403885304	1593667578	84
3403848378	1593667064	41	88679291768326188	88679293641306599	88679293929693562
3403608338	1593664407	57
3403426763	1593662680	38	88679292178627952
3403129811	1593658982	33-
3402873761	1593647839	42-
3402741877	1593622754	21
3402725276	1593621603	41
*/
declare	@comtime numeric(26,0)			-- 评价时间
declare @shiptime int					-- 配送分钟
declare	@comrange int					-- 送达几分钟内评价

select	@comtime = 1593673668,
		@shiptime = 37,
		@comrange = 80

select	t1.wm_poi_id,
		t1.wm_order_id_view,
		t1.USER_ID,
		substring(convert(varchar, DATEADD(s, t1.confirm_time, '1970-1-1 08:00:00'), 120), 9, 11) confirm_time,
		substring(convert(varchar, t1.order_time_fmt, 120), 9, 11) order_time_s,
		substring(convert(varchar, t1.estimate_arrival_time_fmt, 120), 9, 11) estimate_time_s,
		t1.estimated_make_time,
		substring(convert(varchar, DATEADD(s, t5.confirmTime, '1970-1-1 08:00:00'), 120), 9, 11) confirmTime,
		substring(convert(varchar, DATEADD(s, t5.standardSendoutTime, '1970-1-1 08:00:00'), 120), 9, 11) standardSendoutTime,
		substring(convert(varchar, DATEADD(s, t5.actualSendoutTime, '1970-1-1 08:00:00'), 120), 9, 11) actualSendoutTime,
		substring(convert(varchar, DATEADD(s, t1.order_time, '1970-1-1 08:00:00'), 120), 9, 11) order_time,
		substring(convert(varchar, DATEADD(s, t1.utime, '1970-1-1 08:00:00'), 120), 9, 11) utime,
		--substring(convert(varchar, DATEADD(s, t2.prepareDuration, '1970-1-1 08:00:00'), 120), 9, 11) prepareDuration,
		substring(convert(varchar, DATEADD(s, t3.utime, '1970-1-1 08:00:00'), 120), 9, 11) utime,
		substring(convert(varchar, DATEADD(s, t4.latest_delivery_time, '1970-1-1 08:00:00'), 120), 9, 11) latest_delivery_time,
		substring(convert(varchar, DATEADD(s, @comtime, '1970-1-1 08:00:00'), 120), 9, 11) comment_time,
		(t4.latest_delivery_time - t1.order_time) - @shiptime * 60 left_seconds
from	orderlist1orders t1
left join orderlist2assigns t2 on t1.wm_order_id_view = t2.wm_order_id_view_str
left join orderlist3settles t3 on t1.wm_order_id_view = t3.wmOrderViewIdStr
left join orderlist4dispatchs t4 on t1.wm_order_id_view = t4.wmOrderViewId
left join dispatchtime t5 on t1.wm_order_id_view = t5.wmOrderViewId
where	t1.order_time < @comtime
and		t1.order_time > @comtime - 12 * 3600
and		@comtime > t4.latest_delivery_time 
and		t4.latest_delivery_time + @comrange * 60 > @comtime
and		convert(int, (t4.latest_delivery_time - t1.order_time) / 60) = @shiptime
