-- SQLite 資料庫建表與預填數據腳本 (schema.sql)

-- 啟用外鍵約束
PRAGMA foreign_keys = ON;

-- 1. 刪除舊表 (若存在，防衝突)
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS lottery_history;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;

-- 2. 建立 users 表 (使用者帳號)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. 建立 games 表 (彩券種類規格)
CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    game_code TEXT UNIQUE NOT NULL,
    max_number INTEGER NOT NULL,
    pick_count INTEGER NOT NULL,
    has_special INTEGER NOT NULL DEFAULT 0
);

-- 4. 建立 lottery_history 表 (歷史開獎數據)
CREATE TABLE lottery_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_code TEXT NOT NULL,
    draw_period TEXT NOT NULL,
    draw_date TEXT NOT NULL,
    winning_numbers TEXT NOT NULL,
    special_number INTEGER,
    FOREIGN KEY (game_code) REFERENCES games (game_code) ON DELETE CASCADE
);

-- 5. 建立 records 表 (投注盈虧記帳)
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    game_code TEXT NOT NULL,
    cost INTEGER NOT NULL CHECK(cost > 0),
    prize INTEGER NOT NULL CHECK(prize >= 0),
    record_date TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (game_code) REFERENCES games (game_code) ON DELETE CASCADE
);

-- ==========================================
-- 預填數據 (Seed Data)
-- ==========================================

-- 預填彩券種類
INSERT INTO games (name, game_code, max_number, pick_count, has_special) VALUES 
('大樂透', 'lotto', 49, 6, 1),
('六合彩', 'mark_six', 49, 6, 1),
('今彩 539', 'daily_cash_539', 39, 5, 0);

-- 預填大樂透歷史開獎數據 (最近 5 期)
INSERT INTO lottery_history (game_code, draw_period, draw_date, winning_numbers, special_number) VALUES
('lotto', '113000045', '2026-05-26', '08,12,19,25,32,44', 09),
('lotto', '113000044', '2026-05-22', '03,11,18,24,31,45', 14),
('lotto', '113000043', '2026-05-19', '02,07,15,22,35,49', 28),
('lotto', '113000042', '2026-05-15', '05,14,23,29,38,41', 06),
('lotto', '113000041', '2026-05-12', '09,17,21,30,40,47', 15);

-- 預填六合彩歷史開獎數據 (最近 5 期)
INSERT INTO lottery_history (game_code, draw_period, draw_date, winning_numbers, special_number) VALUES
('mark_six', '2026045', '2026-05-25', '01,10,18,27,33,48', 12),
('mark_six', '2026044', '2026-05-21', '05,11,20,29,35,42', 08),
('mark_six', '2026043', '2026-05-18', '02,08,14,25,38,44', 33),
('mark_six', '2026042', '2026-05-14', '04,13,22,31,39,47', 24),
('mark_six', '2026041', '2026-05-11', '07,16,24,35,41,49', 03);

-- 預填今彩 539 歷史開獎數據 (最近 5 期)
INSERT INTO lottery_history (game_code, draw_period, draw_date, winning_numbers, special_number) VALUES
('daily_cash_539', '115000045', '2026-05-26', '04,12,19,25,31', NULL),
('daily_cash_539', '115000044', '2026-05-25', '02,08,15,24,38', NULL),
('daily_cash_539', '115000043', '2026-05-23', '03,11,21,29,35', NULL),
('daily_cash_539', '115000042', '2026-05-22', '05,14,22,30,37', NULL),
('daily_cash_539', '115000041', '2026-05-21', '07,16,23,32,39', NULL);
