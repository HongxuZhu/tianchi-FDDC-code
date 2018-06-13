create database fddc default charset utf8 COLLATE utf8_general_ci;
grant all on fddc.* to 'fddc'@'localhost' identified by 'Data2018_';
flush privileges;

CREATE TABLE IF NOT EXISTS `hetong`(
   `公告id` INT UNSIGNED,
   `甲方` VARCHAR(255),
   `乙方` VARCHAR(255),
   `项目名称` VARCHAR(255),
   `合同名称` VARCHAR(255),
   `合同金额上限` DECIMAL(21,6),
   `合同金额下限` DECIMAL(21,6),
   `联合体成员` VARCHAR(255)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `dingzeng`(
   `公告id` INT UNSIGNED,
   `增发对象` VARCHAR(255),
   `增发数量` BIGINT(20),
   `增发金额` DECIMAL(21,6),
   `锁定期` INT UNSIGNED,
   `认购方式` VARCHAR(255)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `zengjianchi`(
   `公告id` INT UNSIGNED,
   `股东全称` VARCHAR(255),
   `股东简称` VARCHAR(255),
   `变动截止日期` DATETIME,
   `变动价格` DECIMAL(22,4),
   `变动数量` BIGINT(20),
   `变动后持股数` BIGINT(20),
   `变动后持股比例` DECIMAL(22,4)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOAD DATA LOCAL INFILE '/media/utopia/U16G/[new] FDDC_announcements_round1_train_result_20180605/dingzeng.train'
 INTO TABLE dingzeng
 CHARACTER SET utf8
 FIELDS TERMINATED BY '\t';

 LOAD DATA LOCAL INFILE '/media/utopia/U16G/[new] FDDC_announcements_round1_train_result_20180605/hetong.train'
 INTO TABLE hetong
 CHARACTER SET utf8
 FIELDS TERMINATED BY '\t';

 LOAD DATA LOCAL INFILE '/media/utopia/U16G/[new] FDDC_announcements_round1_train_result_20180605/zengjianchi.train'
 INTO TABLE zengjianchi
 CHARACTER SET utf8
 FIELDS TERMINATED BY '\t';