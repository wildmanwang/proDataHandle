CREATE TABLE `store_info` (
  `erpID` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `loginType` varchar(45) DEFAULT 'SMS',
  `mobile` varchar(45) DEFAULT NULL,
  `loginAcc` varchar(45) DEFAULT NULL,
  `loginPwd` varchar(45) DEFAULT NULL,
  `recipient` varchar(45) DEFAULT NULL,
  `lastSend` varchar(10) DEFAULT NULL,
  `initFlag` tinyint NOT NULL DEFAULT '0',
  `level` tinyint NOT NULL,
  `loginDate` varchar(10) DEFAULT NULL,
  `cookie_order` varchar(2048) DEFAULT NULL,
  `cookie_comment` varchar(2048) DEFAULT NULL,
  `msgScore` tinyint NOT NULL DEFAULT '2',
  `status` tinyint NOT NULL DEFAULT '0',
  `createTime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`erpID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `order_main` (
  `sID` int NOT NULL AUTO_INCREMENT,
  `erpID` bigint NOT NULL,
  `storeID` int NOT NULL,
  `num` int NOT NULL,
  `status` tinyint NOT NULL,
  `order_time` int NOT NULL,
  `estimate_arrival_time` int DEFAULT NULL,
  `prepare_time` int DEFAULT NULL,
  `delivery_time` int DEFAULT NULL,
  `settle_time` int DEFAULT NULL,
  `consumerID` bigint DEFAULT NULL,
  `privacy_phone1` varchar(45) DEFAULT NULL,
  `privacy_phone2` varchar(45) DEFAULT NULL,
  `matched` tinyint NOT NULL DEFAULT '0',
  `remark` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`sID`)
) ENGINE=InnoDB AUTO_INCREMENT=6378 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `order_detail` (
  `sID` int NOT NULL AUTO_INCREMENT,
  `orderID` bigint NOT NULL,
  `storeID` int NOT NULL,
  `order_time` int NOT NULL,
  `itemID` bigint NOT NULL,
  `itemName` varchar(100) NOT NULL,
  `unit` varchar(45) DEFAULT NULL,
  `priceOri` decimal(7,2) DEFAULT NULL,
  `price` decimal(7,2) DEFAULT NULL,
  `qty` decimal(7,2) DEFAULT NULL,
  `amt` decimal(9,2) DEFAULT NULL,
  PRIMARY KEY (`sID`)
) ENGINE=InnoDB AUTO_INCREMENT=14574 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `comment_main` (
  `sID` int NOT NULL AUTO_INCREMENT,
  `erpID` bigint NOT NULL,
  `storeID` int NOT NULL,
  `orderID` bigint DEFAULT NULL,
  `order_score` tinyint NOT NULL,
  `food_score` tinyint DEFAULT NULL,
  `delivery_score` tinyint DEFAULT NULL,
  `package_score` tinyint DEFAULT NULL,
  `taste_score` tinyint DEFAULT NULL,
  `ship_score` tinyint DEFAULT NULL,
  `quality_score` tinyint DEFAULT NULL,
  `pic_cnt` tinyint NOT NULL DEFAULT '0',
  `comment_time` int NOT NULL,
  `data_time` int NOT NULL,
  `from_time` int NOT NULL DEFAULT '0',
  `to_time` int NOT NULL,
  `ship_duration` int NOT NULL,
  `over_duration` int NOT NULL,
  `consumerSName` varchar(45) DEFAULT NULL,
  `tmpName` varchar(45) DEFAULT NULL,
  `comment_str` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`sID`)
) ENGINE=InnoDB AUTO_INCREMENT=1108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `comment_detail` (
  `sID` int NOT NULL AUTO_INCREMENT,
  `commentID` bigint NOT NULL,
  `storeID` int NOT NULL,
  `comment_time` int NOT NULL,
  `itemSource` tinyint NOT NULL,
  `itemID` bigint DEFAULT NULL,
  `itemName` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`sID`)
) ENGINE=InnoDB AUTO_INCREMENT=3072 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `sys_paras` (
  `paraCode` varchar(45) NOT NULL,
  `paraName` varchar(45) NOT NULL,
  `paraValue` varchar(255) DEFAULT NULL,
  `remark` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`paraCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `oper_log` (
  `sID` int NOT NULL AUTO_INCREMENT,
  `oper_time` int DEFAULT NULL,
  `storeID` int NOT NULL,
  `busi_type` tinyint NOT NULL,
  `step` tinyint NOT NULL,
  `begin_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `status` tinyint DEFAULT '0',
  `remark` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`sID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `business_notice` (
  `storeID` bigint NOT NULL,
  `commentID` bigint NOT NULL,
  `orderID` bigint NOT NULL,
  `comment_time` int NOT NULL,
  `order_score` tinyint NOT NULL,
  `pic_cnt` tinyint NOT NULL DEFAULT '0',
  `commentStr` varchar(255) DEFAULT NULL,
  `orderNum` int NOT NULL DEFAULT '0',
  `order_time` int NOT NULL,
  `delivery_time` int NOT NULL,
  `order_remark` varchar(255) DEFAULT NULL,
  `sure_flag` tinyint NOT NULL DEFAULT '0',
  `status` tinyint NOT NULL DEFAULT '0',
  `remark` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`storeID`,`commentID`,`orderID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
