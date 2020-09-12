CREATE TABLE `store_info` (
  `erpID` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `mobile` varchar(45) DEFAULT NULL,
  `recipient` varchar(45) DEFAULT NULL,
  `lastSend` varchar(10) DEFAULT NULL,
  `initFlag` tinyint NOT NULL DEFAULT '0',
  `level` tinyint NOT NULL,
  `loginDate` varchar(10) DEFAULT NULL,
  `cookie_order` varchar(2048) DEFAULT NULL,
  `cookie_comment` varchar(2048) DEFAULT NULL,
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
  PRIMARY KEY (`sID`)
) ENGINE=InnoDB AUTO_INCREMENT=4189 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=10584 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `comment_main` (
  `sID` int NOT NULL AUTO_INCREMENT,
  `erpID` bigint NOT NULL,
  `storeID` int NOT NULL,
  `orderID` bigint DEFAULT NULL,
  `userName` varchar(45) DEFAULT NULL,
  `comment_str` varchar(255) DEFAULT NULL,
  `order_score` tinyint NOT NULL,
  `food_score` tinyint DEFAULT NULL,
  `delivery_score` tinyint DEFAULT NULL,
  `package_score` tinyint DEFAULT NULL,
  `taste_score` tinyint DEFAULT NULL,
  `ship_score` tinyint DEFAULT NULL,
  `quality_score` tinyint DEFAULT NULL,
  `comment_time` int NOT NULL,
  `data_time` int NOT NULL,
  `from_time` int NOT NULL DEFAULT '0',
  `to_time` int NOT NULL,
  `ship_duration` int NOT NULL,
  `over_duration` int NOT NULL,
  PRIMARY KEY (`sID`)
) ENGINE=InnoDB AUTO_INCREMENT=408 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `comment_detail` (
  `sID` int NOT NULL AUTO_INCREMENT,
  `commentID` bigint NOT NULL,
  `storeID` int NOT NULL,
  `comment_time` int NOT NULL,
  `itemSource` tinyint NOT NULL,
  `itemID` bigint DEFAULT NULL,
  `itemName` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`sID`)
) ENGINE=InnoDB AUTO_INCREMENT=1692 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `business_notice` (
  `storeID` bigint NOT NULL,
  `commentID` bigint NOT NULL,
  `comment_time` int NOT NULL,
  `order_score` tinyint NOT NULL,
  `commentStr` varchar(255) DEFAULT NULL,
  `orderNum` int NOT NULL DEFAULT '0',
  `orderID` bigint NOT NULL,
  `order_time` int NOT NULL,
  `delivery_time` int NOT NULL,
  `sure_flag` tinyint NOT NULL DEFAULT '0',
  `status` tinyint NOT NULL,
  `remark` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`storeID`,`commentID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
