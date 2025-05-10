-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 10, 2025 at 07:33 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `update`
--

-- --------------------------------------------------------

--
-- Table structure for table `address`
--

CREATE TABLE `address` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `house_number` varchar(100) NOT NULL,
  `area` varchar(100) NOT NULL,
  `landmark` varchar(100) NOT NULL,
  `pincode` varchar(6) NOT NULL,
  `state` varchar(100) NOT NULL,
  `district` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `address`
--

INSERT INTO `address` (`id`, `customer_id`, `house_number`, `area`, `landmark`, `pincode`, `state`, `district`) VALUES
(1, 1, 'No.4', 'Anna Nagar', 'Near Marina Beach', '600040', 'Tamil Nadu', 'Chennai'),
(2, 2, 'No.12', 'Gandhi Nagar', 'Near Tiruchengode Road', '637001', 'Tamil Nadu', 'Namakkal'),
(3, 3, 'No.25', 'Sea View Road', 'Near Alappuzha Beach', '688007', 'Kerala', 'Alappuzha'),
(6, 6, 'NO.21', 'neru street', 'near Vijay theatre', '613002', 'Tamil Nadu', 'Thanjavur'),
(16, 1, '85', 'neru street', 'near Vijay theatre', '613002', 'Odisha', 'Kendrapara');

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(1, 'admin', '123');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `phone` varchar(10) NOT NULL,
  `password` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`id`, `username`, `phone`, `password`) VALUES
(1, 'customer1', '0987654321', '123'),
(2, 'customer', '6532841111', '123'),
(3, 'Sid', '8348348340', '123'),
(6, 'Kiran', '9525468456', '123');

-- --------------------------------------------------------

--
-- Table structure for table `farmer`
--

CREATE TABLE `farmer` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `phone` varchar(10) NOT NULL,
  `state` varchar(100) NOT NULL,
  `district` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `approved` tinyint(1) DEFAULT 0,
  `status` enum('pending','approved','rejected') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `farmer`
--

INSERT INTO `farmer` (`id`, `name`, `phone`, `state`, `district`, `password`, `approved`, `status`) VALUES
(1, 'farmer1', '1234567890', 'Tamil Nadu', 'Chennai', '123', 1, 'approved'),
(2, 'farmer2', '9632587410', 'Kerala', 'Kannur', '123', 1, 'approved'),
(3, 'dns', '1234235333', 'Tamil Nadu', 'Nagapattinam', '123', 0, 'rejected'),
(4, 'raja', '6664845555', 'Tamil Nadu', 'Namakkal', '123', 1, 'approved'),
(5, 'Unni Krishnan', '9898989898', 'Kerala', 'Palakkad', '123', 0, 'pending');

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `id` int(11) NOT NULL,
  `farmer_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `price` float NOT NULL,
  `kilo` float NOT NULL,
  `image_url` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`id`, `farmer_id`, `name`, `price`, `kilo`, `image_url`) VALUES
(1, 1, 'Mango', 110, 35, '/static/uploads/mango.jpg'),
(2, 1, 'Orange', 120, 0, '/static/uploads/orange.jpg'),
(3, 1, 'Apple', 132, 0, '/static/uploads/apple.jpg'),
(4, 1, 'Banana', 72, 14, '/static/uploads/banana.jpg'),
(5, 1, 'Guava', 70, 45, '/static/uploads/Guava.jpg'),
(6, 1, 'Papaya', 60, 18, '/static/uploads/papaya.jpg'),
(7, 1, 'Watermelon', 40, 138, '/static/uploads/watermelon.jpg'),
(8, 1, 'Chikoo(Sapotta)', 60, 18, '/static/uploads/chikoo.jpg'),
(9, 1, 'Pomegranate', 125, 30, '/static/uploads/pomegranate.jpg'),
(10, 1, 'Lemon', 120, 23, '/static/uploads/lemon.jpg'),
(11, 1, 'Coconut', 145, 20, '/static/uploads/coconut.jpg'),
(12, 1, 'Muskmelon', 50, 34, '/static/uploads/Muskmelomn.jpg'),
(13, 1, 'Custard Apple', 130, 43, '/static/uploads/Custard-Apple.jpg'),
(14, 1, 'Avacado', 160, 33, '/static/uploads/Avocado.jpg'),
(15, 1, 'Green Grapes', 120, 40, '/static/uploads/greengrape.jpg'),
(16, 1, 'Black Grapes', 180, 45, '/static/uploads/blackgrape.jpg'),
(17, 1, 'Red Banana', 120, 55, '/static/uploads/redbanana.jpg'),
(18, 1, 'Pear', 140, 34, '/static/uploads/pear.jpg'),
(19, 1, 'Strawberry', 400, 39, '/static/uploads/strawberry.jpg'),
(20, 1, 'DragonFruit', 260, 60, '/static/uploads/dragonfruit.jpg'),
(21, 1, 'Amla', 110, 120, '/static/uploads/amla.jpg'),
(22, 1, 'BabyCorn', 80, 50, '/static/uploads/babycorn.jpg'),
(23, 1, 'Small Onion', 78, 50, '/static/uploads/smallonion.jpg'),
(24, 1, 'Big Onion', 40, 80, '/static/uploads/onion.jpg'),
(25, 1, 'SweetPotato', 105, 50, '/static/uploads/sweetpotato.jpg'),
(26, 1, 'Potato', 48, 30, '/static/uploads/potato.jpg'),
(27, 1, 'Capsicum', 52, 30, '/static/uploads/capsicum-256.png'),
(28, 1, 'Carrot', 95, 34, '/static/uploads/carrot.jpg'),
(29, 1, 'Cucumber', 40, 50, '/static/uploads/cucumber.jpg'),
(30, 1, 'Bitter Gourd', 40, 20, '/static/uploads/bittergourd-256.png'),
(31, 1, 'Cabbage', 28, 20, '/static/uploads/cabbage-256.png'),
(32, 1, 'Cauliflower', 38, 19, '/static/uploads/culi.jpg'),
(33, 1, 'Brinjal', 88, 20, '/static/uploads/Brinjal.jpg'),
(34, 1, 'Ginger', 70, 20, '/static/uploads/ginger.jpg'),
(35, 1, 'Garlic', 125, 38, '/static/uploads/garlic.jpg'),
(36, 1, 'Greenpeas', 100, 34, '/static/uploads/Greenpeas.jpg'),
(37, 1, 'RawMango', 90, 44, '/static/uploads/RawMango.jpg'),
(38, 1, 'Pumpkin', 75, 22, '/static/uploads/pumpkin.jpg'),
(39, 1, 'Radish', 55, 34, '/static/uploads/radish.jpg'),
(40, 1, 'Drumsticks', 80, 60, '/static/uploads/drumstick.jpg'),
(64, 2, 'Chow Chow', 70, 120, '/static/uploads/chow.jpg'),
(65, 2, 'Corn', 40, 100, '/static/uploads/corn.jpg'),
(66, 4, 'Thuvaram Paruppu', 210, 190, '/static/uploads/toor.jpg'),
(67, 4, 'Green Chilli', 90, 89, '/static/uploads/greenchilli.jpg');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `address`
--
ALTER TABLE `address`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`);

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `phone` (`phone`);

--
-- Indexes for table `farmer`
--
ALTER TABLE `farmer`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD UNIQUE KEY `phone` (`phone`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`id`),
  ADD KEY `farmer_id` (`farmer_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `address`
--
ALTER TABLE `address`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `farmer`
--
ALTER TABLE `farmer`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=68;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `address`
--
ALTER TABLE `address`
  ADD CONSTRAINT `address_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`farmer_id`) REFERENCES `farmer` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
