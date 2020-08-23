CREATE TABLE `mt_orderinfo`.`city_info` (
  `erpID` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`erpID`));

CREATE TABLE `mt_orderinfo`.`store_info` (
  `erpID` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `cityID` INT NOT NULL,
  `longitude` INT NULL,
  `latitude` INT NULL,
  PRIMARY KEY (`erpID`));

CREATE TABLE `mt_orderinfo`.`order_main` (
  `sID` INT NOT NULL AUTO_INCREMENT,
  `erpID` BIGINT NOT NULL,
  `storeID` INT NOT NULL,
  `status` TINYINT NOT NULL,
  `order_time` INT NOT NULL,
  `estimate_arrival_time` INT NULL,
  `prepare_time` INT NULL,
  `delivery_time` INT NULL,
  `arrival_time` INT NULL,
  `settle_time` INT NULL,
  `consumerID` BIGINT NULL,
  `privacy_phone1` VARCHAR(45) NULL,
  `privacy_phone2` VARCHAR(45) NULL,
  PRIMARY KEY (`sID`));

CREATE TABLE `mt_orderinfo`.`order_detail` (
  `sID` INT NOT NULL AUTO_INCREMENT,
  `orderID` BIGINT NOT NULL,
  `itemID` BIGINT NOT NULL,
  `itemName` VARCHAR(100) NOT NULL,
  `unit` VARCHAR(45) NULL,
  `priceOri` DECIMAL(7,2) NULL,
  `price` DECIMAL(7,2) NULL,
  `qty` DECIMAL(7,2) NULL,
  `amt` DECIMAL(9,2) NULL,
  PRIMARY KEY (`sID`));

CREATE TABLE `mt_orderinfo`.`consumer_info` (
  `sID` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NULL,
  `nickname` VARCHAR(45) NULL,
  `name` VARCHAR(45) NULL,
  `gender` TINYINT NULL,
  `phone` VARCHAR(45) NULL,
  `lastNumber` VARCHAR(45) NULL,
  `cityID` INT NULL,
  PRIMARY KEY (`sID`));

CREATE TABLE `mt_orderinfo`.`delivery_address` (
  `sID` INT NOT NULL AUTO_INCREMENT,
  `consumerID` BIGINT NULL,
  `address` VARCHAR(100) NULL,
  `recipient_name` VARCHAR(45) NULL,
  `recipient_phone` VARCHAR(45) NULL,
  `longitude` INT NULL,
  `latitude` INT NULL,
  PRIMARY KEY (`sID`));

CREATE TABLE `mt_orderinfo`.`comment_main` (
  `sID` INT NOT NULL AUTO_INCREMENT,
  `erpID` BIGINT NOT NULL,
  `storeID` INT NOT NULL,
  `orderID` BIGINT NULL,
  `comment_str` VARCHAR(255) NULL,
  `order_score` TINYINT NOT NULL,
  `food_score` TINYINT NULL,
  `delivery_score` TINYINT NULL,
  `package_score` TINYINT NULL,
  `taste_score` TINYINT NULL,
  `ship_score` TINYINT NULL,
  `quality_score` TINYINT NULL,
  `comment_time` INT NULL,
  `ship_duration` INT NULL,
  `over_duration` INT NULL,
  PRIMARY KEY (`sID`));

CREATE TABLE `mt_orderinfo`.`comment_detail` (
  `sID` INT NOT NULL AUTO_INCREMENT,
  `commentID` BIGINT NOT NULL,
  `itemID` BIGINT NULL,
  `itemName` VARCHAR(100) NULL,
  PRIMARY KEY (`sID`));

insert into city_info ( erpID, name ) values ( 440300, '深圳' );
insert into store_info ( erpID, name, cityID, longitude, latitude ) values ( 8867929, '牛家人大碗牛肉面（布吉黑金店）', 440300, 114117975, 22610040 );

CREATE TABLE `mt_service`.`business_notice` (
  `storeID` BIGINT NOT NULL,
  `commentID` BIGINT NOT NULL,
  `commentDate` VARCHAR(10) NOT NULL,
  `order_score` TINYINT NOT NULL,
  `commentStr` VARCHAR(255) NULL,
  `orderID` BIGINT NULL,
  `status` TINYINT NOT NULL,
  PRIMARY KEY (`storeID`, `commentID`));
