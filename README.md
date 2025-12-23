
## 一个基于 Python (NiceGUI) 和 MySQL 开发的轻量级酒店管理系统，实现了入住管理、客房管理、住客信息管理等核心业务流程。
## 📋 功能特点
- **入住系统**：支持住客登记、房间预订、快捷入住、退房结算（自动计算费用）
- **客房管理**：支持房间的增删改查，实时更新房间状态
- **住客管理**：集中管理住客信息，支持信息的录入、修改和查询
- **用户管理**：管理系统账号，支持添加用户、修改密码及删除普通用户
- **数据可视化**：通过表格直观展示房间状态、预订记录及当前入住情况
## 🛠 技术栈
- **后端/UI框架**：Python + NiceGUI
- **数据库**：MySQL
- **数据库驱动**：mysql-connector-python
## 🚀 快速开始
### 1. 环境要求
- Python 3.8+
- MySQL 5.7 或 8.0+
### 2. 安装依赖
在项目根目录下执行以下命令安装所需的 Python 库：
```bash
pip install nicegui mysql-connector-python
```
### 3. 数据库配置
1. **创建数据库**
   登录 MySQL，创建名为 `demo01` 的数据库：
   ```sql
   CREATE DATABASE demo01;
   USE demo01;
   ```
2. **创建数据表**
   请在 `demo01` 数据库中执行以下 SQL 语句创建所需的数据表：
   ```sql
    -- 导出  表 DEMO01.checkins 结构
    CREATE TABLE IF NOT EXISTS `checkins` (
    `customer_id` char(18) NOT NULL COMMENT '身份证号',
    `room_id` int DEFAULT NULL COMMENT '房间号',
    `checkin_time` date DEFAULT NULL COMMENT '入住时间',
    `checkout_time` date DEFAULT NULL COMMENT '退房时间',
    PRIMARY KEY (`customer_id`),
    KEY `FK2_ROOM_ID` (`room_id`),
    CONSTRAINT `FK2_CUSTOMER_ID` FOREIGN KEY (`customer_id`) REFERENCES `customer_info` (`customer_id`),
    CONSTRAINT `FK2_ROOM_ID` FOREIGN KEY (`room_id`) REFERENCES `room_info` (`room_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='入住表';

    -- 数据导出被取消选择。


    -- 导出  表 DEMO01.customer_info 结构
    CREATE TABLE IF NOT EXISTS `customer_info` (
    `customer_id` char(18) NOT NULL COMMENT '身份证号',
    `customer_name` char(50) NOT NULL COMMENT '姓名',
    `customer_telephone` char(11) NOT NULL COMMENT '电话号码',
    `customer_sex` char(50) DEFAULT NULL COMMENT '性别男1女0',
    PRIMARY KEY (`customer_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='顾客基本信息';

    -- 数据导出被取消选择。


    -- 导出  表 DEMO01.reservations 结构
    CREATE TABLE IF NOT EXISTS `reservations` (
    `customer_id` char(18) NOT NULL COMMENT '身份证号',
    `room_id` int NOT NULL COMMENT '房间号',
    `expected_checkin` date NOT NULL COMMENT '预计入住日期',
    `expected_checkout` date NOT NULL COMMENT '预计退房日期',
    PRIMARY KEY (`customer_id`),
    KEY `FK_ROOM_ID` (`room_id`),
    CONSTRAINT `FK_CUSTOMER_ID` FOREIGN KEY (`customer_id`) REFERENCES `customer_info` (`customer_id`),
    CONSTRAINT `FK_ROOM_ID` FOREIGN KEY (`room_id`) REFERENCES `room_info` (`room_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='预定表';

    -- 数据导出被取消选择。


    -- 导出  表 DEMO01.room_info 结构
    CREATE TABLE IF NOT EXISTS `room_info` (
    `room_id` int NOT NULL COMMENT '房间号',
    `room_capacity` int NOT NULL COMMENT '房间容量',
    `room_type` char(50) NOT NULL COMMENT '房间类型',
    `price` int NOT NULL COMMENT '价格',
    `room_status` char(50) DEFAULT '空闲' COMMENT '房间状态',
    PRIMARY KEY (`room_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='房间基本信息表';

    -- 数据导出被取消选择。


    -- 导出  表 DEMO01.users 结构
    CREATE TABLE IF NOT EXISTS `users` (
    `username` varchar(50) NOT NULL,
    `password` varchar(50) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='账号信息';

    -- 数据导出被取消选择。


    -- 导出  触发器 DEMO01.checkins_after_delete 结构
    SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='';
    DELIMITER //
    CREATE TRIGGER `checkins_after_delete` AFTER DELETE ON `checkins` FOR EACH ROW BEGIN
    UPDATE room_info
    SET room_status = '空闲'
    WHERE room_id = OLD.room_id;
    END//
    DELIMITER ;
    SET SQL_MODE=@OLDTMP_SQL_MODE;


    -- 导出  触发器 DEMO01.checkins_after_insert 结构
    SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='';
    DELIMITER //
    CREATE TRIGGER `checkins_after_insert` AFTER INSERT ON `checkins` FOR EACH ROW BEGIN
    UPDATE room_info
    SET room_status = '已入住'
    WHERE room_id = NEW.room_id;
    END//
    DELIMITER ;
    SET SQL_MODE=@OLDTMP_SQL_MODE;


    -- 导出  触发器 DEMO01.reservations_after_delete 结构
    SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='';
    DELIMITER //
    CREATE TRIGGER `reservations_after_delete` AFTER DELETE ON `reservations` FOR EACH ROW BEGIN
    UPDATE room_info 
    SET room_status = '空闲'
    WHERE room_id = OLD.room_id;
    END//
    DELIMITER ;
    SET SQL_MODE=@OLDTMP_SQL_MODE;


    -- 导出  触发器 DEMO01.reservations_after_insert 结构
    SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='';
    DELIMITER //
    CREATE TRIGGER `reservations_after_insert` AFTER INSERT ON `reservations` FOR EACH ROW BEGIN
    UPDATE room_info
    SET room_status = '已预定'
    WHERE room_id = NEW.room_id;
    END//
    DELIMITER ;
    SET SQL_MODE=@OLDTMP_SQL_MODE;
   ```
3. **初始化管理员账号**
   
   系统默认需要一个管理员账号，请手动在 `users` 表中插入（或使用系统默认登录逻辑验证）：
   ```sql
   INSERT INTO users (username, password) VALUES ('admin', '123456');
   ```
### 4. 修改配置
如果本地数据库密码不是 `123456`，请修改 `main.py` 中的数据库连接代码：
```python
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="你的数据库密码"  # 修改此处
)
```
### 5. 运行程序
在终端执行：
```bash
python main.py
```
启动成功后，浏览器会自动打开（或访问控制台显示的 URL，通常是 `http://localhost:8080`）。
## 📦 默认账号
- **账号**：`admin`
- **密码**：`123456`
## ⚠️ 开发者注意事项
1. **安全性**：当前版本密码以明文存储，仅适用于学习演示，不建议用于生产环境。
2. **日期格式**：输入日期时请确保格式为 `YYYY-MM-DD`。
## 📂 项目结构
```
.
└── main.py          # 主程序文件（包含所有后端逻辑和前端UI定义）
```
## 📝 许可证
本项目为数据库原理与应用课程设计，仅供学习交流使用。
---
