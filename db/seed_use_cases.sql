-- ticketing 数据库：用例数据（MySQL）
-- 前置：先执行 db/schema.sql 建表
--
-- 说明：
-- - 本文件会清空 orders/tickets/users 三张表（演示用例数据，避免重复导入冲突）
-- - 默认测试账号：
--   1) demo1@example.com / pass1234
--   2) demo2@example.com / pass5678

SET NAMES utf8mb4;
SET time_zone = '+08:00';

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE orders;
TRUNCATE TABLE tickets;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- users（固定 id，便于订单外键演示）
INSERT INTO users (id, email, password_hash, created_at) VALUES
  (1, 'demo1@example.com', 'scrypt:32768:8:1$evmCnGUBU31h2MRp$953dc44c588870f5e68784aea30db8dedc156f3c554f52a74b805b8187373ac0f784e517e4d1550e1f626028324f2aa1d72dd5844c80b4103f6b9d9aafa7e3e9', '2026-04-01 10:00:00'),
  (2, 'demo2@example.com', 'scrypt:32768:8:1$yQ7SKIadxKFCTSXr$3360f05a597e36ace4c1519b45c66d3bb95b85da26aff811f2ebb17c1b3b66dd4788d72074b7d790d8f25de57f5f46dcdd102b57330539b7f735a52ba04b61c7', '2026-04-02 11:30:00');

-- tickets（固定 id）
INSERT INTO tickets (id, title, venue, start_time, price_cents, stock, created_at) VALUES
  (101, '用例：春季音乐会', '城市音乐厅', '2026-05-01 19:30:00', 19900, 120, '2026-04-10 09:00:00'),
  (102, '用例：科幻电影夜场', '万达影城 3 号厅', '2026-04-28 21:10:00', 6900, 80, '2026-04-10 09:05:00'),
  (103, '用例：话剧《人间喜剧》', '大剧院', '2026-05-10 19:00:00', 29900, 60, '2026-04-10 09:10:00');

-- orders（固定 id；total_cents = price_cents * quantity）
INSERT INTO orders (id, user_id, ticket_id, quantity, total_cents, status, created_at) VALUES
  (1001, 1, 101, 2, 39800, 'PAID', '2026-04-12 12:10:00'),
  (1002, 1, 102, 1, 6900,  'PAID', '2026-04-12 12:20:00'),
  (1003, 2, 103, 1, 29900, 'PAID', '2026-04-12 13:05:00'),
  (1004, 2, 101, 1, 19900, 'PAID', '2026-04-12 13:40:00');

-- 让 AUTO_INCREMENT 继续从合理值增长（可选）
ALTER TABLE users AUTO_INCREMENT = 1000;
ALTER TABLE tickets AUTO_INCREMENT = 1000;
ALTER TABLE orders AUTO_INCREMENT = 2000;
