update hetong set `联合体成员`='' where `联合体成员`='\r';
# 每个字段得空值数
select
COUNT(CASE WHEN `公告id`='' THEN 1 END) as GGN,
COUNT(CASE WHEN `甲方`='' THEN 1 END) as JFN,
COUNT(CASE WHEN `乙方`='' THEN 1 END) as YFN,
COUNT(CASE WHEN `项目名称`='' THEN 1 END) as XMN,
COUNT(CASE WHEN `合同名称`='' THEN 1 END) as HTN,
COUNT(CASE WHEN `合同金额上限`='' THEN 1 END) as JEUN,
COUNT(CASE WHEN `合同金额下限`='' THEN 1 END) as JEDN,
COUNT(CASE WHEN `联合体成员`!='' THEN 1 END) as LHN1,
COUNT(CASE WHEN `联合体成员` like '%、%' THEN 1 END) as LHN2,
COUNT(CASE WHEN `联合体成员` like '%、%、%' THEN 1 END) as LHN3
from hetong;

select `联合体成员`,count(1) c from hetong
group by `联合体成员` order by c desc;

select count(1),
count(distinct `公告id`),
count(distinct `公告id`,`乙方`) a,
count(distinct `公告id`,`甲方`) b,# 说明甲方唯一情况更多
count(distinct `公告id`,`项目名称`) c,
count(distinct `公告id`,`合同名称`) d,
count(distinct `公告id`,`合同金额上限`) e,
count(distinct `公告id`,`合同金额下限`) f,
count(distinct `公告id`,`联合体成员`) g,
count(CASE WHEN `合同金额上限`=`合同金额下限` THEN 1 END) h,
count(distinct `公告id`,`乙方`,`甲方`)
from hetong;
# 一个甲方发布多个 35/3138
select `公告id`,`甲方`,count(distinct `乙方`) c from hetong
group by `公告id`,`甲方` having c>1
order by c desc;
# 一个乙方中标多个 145/2982
select `公告id`,`乙方`,count(distinct `甲方`) c from hetong
group by `公告id`,`乙方` having c>1
order by c desc;

select `公告id`,count(1) c
from hetong group by `公告id`
having c=2 order by c desc;

select count(1),
count(distinct `公告id`),
count(distinct `公告id`,`乙方`),
count(distinct `公告id`,`乙方`,`甲方`)
from hetong where `公告id`='1665560';

select * from hetong where `公告id`='15697283';

select count(1)/count(distinct `公告id`) 
from hetong;#1.1207
select count(1)/count(distinct `公告id`),count(1),count(distinct `公告id`) 
from dingzeng;#4.5283
select count(1)/count(distinct `公告id`) ,
count(distinct `公告id`)/count(distinct `公告id`,`股东全称`)
from zengjianchi;#2.2256

select 
count(1),
count(distinct `公告id`),
count(distinct `增发对象`),
count(distinct `增发数量`),
count(distinct `增发金额`),
count(distinct `锁定期`),
count(distinct `认购方式`)
 from dingzeng;
 
select 
`公告id`,count(distinct `增发对象`) c
 from dingzeng group by `公告id` order by c desc;
 
 select 
`公告id`,count(distinct `增发金额`) c,count(distinct `增发对象`)
 from dingzeng group by `公告id` order by c desc;
 
 select * from dingzeng where `增发金额`=0 and `增发数量`=0;
 
select `锁定期`,count(1) c from dingzeng group by `锁定期` order by c desc;
select `认购方式`,count(1) c from dingzeng group by `认购方式` order by c desc;

select min(`增发数量`),max(`增发数量`),min(`增发金额`),max(`增发金额`) 
from dingzeng where `增发数量`>0 and `增发金额`>0;

select min(`增发数量`),min(`增发金额`)
from dingzeng where `增发数量`>0 and `增发金额`>0;

select count(1) from dingzeng where `增发数量`=0;#844
select count(1) from dingzeng where `增发金额`=0;#5586
select count(1) from dingzeng where `增发金额`=0 or `增发数量`=0;#5878
select count(1) from dingzeng where `增发金额`=0 and `增发数量`=0;#552

select sum(case when `增发数量`>10000 then 1 else 0 end),
sum(case when `增发金额`>10000 then 1 else 0 end),
count(1)
from dingzeng;

select sum(case when `增发对象` like '%公司' then 1 else 0 end),
sum(case when `增发对象` like '%计划' then 1 else 0 end),
sum(case when length(`增发对象`)<10 then 1 else 0 end),
count(1)
from dingzeng;

select min(length(`增发对象`)) from dingzeng where `增发对象` like '%公司';
select * from dingzeng where `增发对象` like '%公司' and length(`增发对象`)=9;
select * from dingzeng where length(`增发对象`)>9 and length(`增发对象`)<12;