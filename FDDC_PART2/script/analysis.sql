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

select `公告id`,count(1) c
from hetong group by `公告id`
having c=2 order by c desc;

select count(1),
count(distinct `公告id`),
count(distinct `公告id`,`乙方`),
count(distinct `公告id`,`乙方`,`甲方`)
from hetong where `公告id`='1665560';

select * from hetong where `公告id`='15697283';