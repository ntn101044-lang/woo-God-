-- `project pclo`.vendor definition

CREATE TABLE `vendor` (
  `VendorID` int(11) NOT NULL,
  `Phone` varchar(100) DEFAULT NULL,
  `VendorName` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`VendorID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- `project pclo`.stall definition

CREATE TABLE `stall` (
  `StallID` int(11) NOT NULL AUTO_INCREMENT,
  `StallName` varchar(100) DEFAULT NULL,
  `ZoneType` varchar(100) DEFAULT NULL,
  `Status` varchar(100) DEFAULT NULL,
  `EventID` int(11) DEFAULT NULL,
  `VendorID` int(11) DEFAULT NULL,
  PRIMARY KEY (`StallID`),
  KEY `Stall_vendor_FK` (`VendorID`),
  CONSTRAINT `Stall_vendor_FK` FOREIGN KEY (`VendorID`) REFERENCES `vendor` (`VendorID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- `project pclo`.offers definition

CREATE TABLE `offers` (
  `StallID` int(11) NOT NULL,
  `ProductID` int(11) NOT NULL,
  PRIMARY KEY (`StallID`,`ProductID`),
  CONSTRAINT `Offers_stall_FK` FOREIGN KEY (`StallID`) REFERENCES `stall` (`StallID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;