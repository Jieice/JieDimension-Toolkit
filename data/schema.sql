-- JieDimension Toolkit Database Schema
-- SQLite 3.x
-- Version: 1.0.0
-- Date: 2025-10-08

-- ===== 商品表 =====
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基本信息
    title TEXT NOT NULL,                    -- 商品标题
    title_original TEXT,                    -- 原始标题（AI优化前）
    price REAL NOT NULL,                    -- 价格
    category TEXT NOT NULL,                 -- 分类
    description TEXT,                       -- 商品描述
    images TEXT,                            -- 图片路径（JSON数组）
    quantity INTEGER DEFAULT 1,             -- 数量
    status TEXT DEFAULT '待发布',           -- 状态: 待发布/发布中/已发布/失败
    platform TEXT DEFAULT 'xianyu',         -- 发布平台
    
    -- AI优化信息
    ai_optimized BOOLEAN DEFAULT 0,         -- 是否经过AI优化
    ai_provider TEXT,                       -- 使用的AI提供商
    ai_complexity INTEGER,                  -- AI任务复杂度
    
    -- 发布信息
    published_at DATETIME,                  -- 发布时间
    published_id TEXT,                      -- 平台上的商品ID
    published_url TEXT,                     -- 商品链接
    
    -- 元数据
    import_time DATETIME,                   -- 导入时间
    import_source TEXT,                     -- 导入来源（Excel/CSV文件名）
    row_number INTEGER,                     -- 在Excel中的行号
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基础索引
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_platform ON products(platform);
CREATE INDEX IF NOT EXISTS idx_products_created ON products(created_at);

-- 性能优化：复合索引（Day 8新增）
CREATE INDEX IF NOT EXISTS idx_products_created_status ON products(created_at, status);
CREATE INDEX IF NOT EXISTS idx_products_platform_status ON products(platform, status);
CREATE INDEX IF NOT EXISTS idx_products_status_created ON products(status, created_at DESC);

-- ===== 任务表 =====
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 任务信息
    type TEXT NOT NULL,                     -- 任务类型: publish/chatbot/generate/pack
    name TEXT,                              -- 任务名称
    status TEXT DEFAULT 'pending',          -- 状态: pending/running/completed/failed/cancelled
    progress REAL DEFAULT 0,                -- 进度 0-100
    
    -- 任务数据
    data TEXT,                              -- 任务输入数据（JSON）
    result TEXT,                            -- 任务结果（JSON）
    error TEXT,                             -- 错误信息
    
    -- 统计信息
    total_items INTEGER DEFAULT 0,          -- 总项目数
    processed_items INTEGER DEFAULT 0,      -- 已处理项目数
    success_items INTEGER DEFAULT 0,        -- 成功项目数
    failed_items INTEGER DEFAULT 0,         -- 失败项目数
    
    -- 时间信息
    started_at DATETIME,
    completed_at DATETIME,
    duration REAL,                          -- 执行时长（秒）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 基础索引
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(type);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);

-- 性能优化：复合索引（Day 8新增）
CREATE INDEX IF NOT EXISTS idx_tasks_type_status ON tasks(type, status);
CREATE INDEX IF NOT EXISTS idx_tasks_status_created ON tasks(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_created_status ON tasks(created_at, status);

-- ===== AI使用统计表 =====
CREATE TABLE IF NOT EXISTS ai_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- AI提供商信息
    provider TEXT NOT NULL,                 -- 提供商: ollama/gemini/cohere/doubao
    model TEXT,                             -- 模型名称
    
    -- 使用统计
    prompt_tokens INTEGER DEFAULT 0,        -- 输入tokens数量
    completion_tokens INTEGER DEFAULT 0,    -- 输出tokens数量
    total_tokens INTEGER DEFAULT 0,         -- 总tokens
    
    -- 任务信息
    task_type TEXT,                         -- 任务类型
    task_id INTEGER,                        -- 关联任务ID
    complexity INTEGER,                     -- 任务复杂度 1-4
    
    -- 提示词信息
    prompt_length INTEGER,                  -- 提示词长度
    completion_length INTEGER,              -- 生成内容长度
    
    -- 性能指标
    latency REAL,                           -- 延迟（秒）
    success BOOLEAN DEFAULT 1,              -- 是否成功
    error TEXT,                             -- 错误信息
    
    -- 质量评估（可选，用户反馈）
    quality_score INTEGER,                  -- 质量评分 1-5
    user_feedback TEXT,                     -- 用户反馈
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

-- 基础索引
CREATE INDEX IF NOT EXISTS idx_ai_usage_provider ON ai_usage(provider);
CREATE INDEX IF NOT EXISTS idx_ai_usage_created ON ai_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_usage_task ON ai_usage(task_id);

-- 性能优化：复合索引（Day 8新增）
CREATE INDEX IF NOT EXISTS idx_ai_usage_created_provider ON ai_usage(created_at, provider);
CREATE INDEX IF NOT EXISTS idx_ai_usage_provider_created ON ai_usage(provider, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_usage_provider_success ON ai_usage(provider, success);
CREATE INDEX IF NOT EXISTS idx_ai_usage_created_success ON ai_usage(created_at, success);

-- ===== API配额管理表 =====
CREATE TABLE IF NOT EXISTS api_quota (
    provider TEXT PRIMARY KEY,              -- API提供商名称
    
    -- 配额信息
    quota INTEGER NOT NULL,                 -- 总配额
    quota_period TEXT,                      -- 配额周期: minute/hour/day/month
    used INTEGER DEFAULT 0,                 -- 已使用数量
    
    -- 重置信息
    reset_time DATETIME,                    -- 下次重置时间
    last_reset DATETIME,                    -- 上次重置时间
    auto_reset BOOLEAN DEFAULT 1,           -- 是否自动重置
    
    -- 状态
    enabled BOOLEAN DEFAULT 1,              -- 是否启用
    priority INTEGER DEFAULT 5,             -- 优先级 1-10（高到低）
    
    -- 性能统计
    avg_latency REAL,                       -- 平均延迟
    success_rate REAL,                      -- 成功率 0-1
    
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 初始化API配额数据
INSERT OR IGNORE INTO api_quota (provider, quota, quota_period, priority) VALUES
    ('ollama', 999999, 'unlimited', 10),    -- 本地无限制，最高优先级
    ('gemini', 60, 'minute', 9),            -- Gemini 60次/分钟
    ('cohere', 5000, 'month', 8),           -- Cohere 5000次/月
    ('doubao', 1000, 'day', 8);             -- 豆包 1000次/天

-- ===== 配置表 =====
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,                   -- 配置键
    value TEXT,                             -- 配置值
    type TEXT DEFAULT 'string',             -- 类型: string/int/float/bool/json
    category TEXT,                          -- 分类: ai/ui/database/system
    description TEXT,                       -- 说明
    editable BOOLEAN DEFAULT 1,             -- 是否可编辑
    
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 初始化默认配置
INSERT OR IGNORE INTO config (key, value, type, category, description) VALUES
    -- AI配置
    ('ai.ollama.model', 'deepseek-r1:1.5b', 'string', 'ai', 'Ollama模型名称'),
    ('ai.ollama.url', 'http://localhost:11434', 'string', 'ai', 'Ollama服务地址'),
    ('ai.default_complexity', '2', 'int', 'ai', '默认任务复杂度'),
    ('ai.max_retries', '3', 'int', 'ai', 'API最大重试次数'),
    ('ai.timeout', '30', 'int', 'ai', 'API超时时间（秒）'),
    
    -- UI配置
    ('ui.theme', 'dark', 'string', 'ui', '界面主题'),
    ('ui.language', 'zh-CN', 'string', 'ui', '界面语言'),
    ('ui.window_width', '1200', 'int', 'ui', '窗口宽度'),
    ('ui.window_height', '800', 'int', 'ui', '窗口高度'),
    
    -- 系统配置
    ('system.version', '1.0.0', 'string', 'system', '系统版本'),
    ('system.debug', 'false', 'bool', 'system', '调试模式'),
    ('system.log_level', 'INFO', 'string', 'system', '日志级别'),
    ('system.auto_backup', 'true', 'bool', 'system', '自动备份'),
    ('system.backup_interval', '86400', 'int', 'system', '备份间隔（秒）'),
    
    -- 闲鱼配置
    ('xianyu.batch_size', '50', 'int', 'xianyu', '批量发布数量'),
    ('xianyu.publish_interval', '2', 'int', 'xianyu', '发布间隔（秒）'),
    ('xianyu.auto_optimize', 'true', 'bool', 'xianyu', 'AI自动优化'),
    ('xianyu.chatbot_enabled', 'false', 'bool', 'xianyu', '启用智能客服');

-- ===== 日志表 =====
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 日志信息
    level TEXT NOT NULL,                    -- 级别: DEBUG/INFO/WARNING/ERROR/CRITICAL
    module TEXT,                            -- 模块名称
    message TEXT NOT NULL,                  -- 日志消息
    
    -- 上下文信息
    user_id INTEGER,                        -- 用户ID（如果有）
    task_id INTEGER,                        -- 关联任务ID
    extra TEXT,                             -- 额外信息（JSON）
    
    -- 异常信息
    exception TEXT,                         -- 异常类型
    stack_trace TEXT,                       -- 堆栈跟踪
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_task ON logs(task_id);

-- ===== 用户反馈表 =====
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 反馈信息
    type TEXT NOT NULL,                     -- 类型: bug/feature/improvement/other
    title TEXT NOT NULL,                    -- 标题
    content TEXT NOT NULL,                  -- 内容
    
    -- 关联信息
    related_feature TEXT,                   -- 相关功能
    task_id INTEGER,                        -- 关联任务ID
    
    -- 状态
    status TEXT DEFAULT 'pending',          -- 状态: pending/reviewing/resolved/closed
    priority INTEGER DEFAULT 3,             -- 优先级 1-5
    
    -- 处理信息
    response TEXT,                          -- 回复
    resolved_at DATETIME,                   -- 解决时间
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(type);

-- ===== 触发器：自动更新updated_at =====
CREATE TRIGGER IF NOT EXISTS update_products_timestamp 
AFTER UPDATE ON products
BEGIN
    UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_config_timestamp 
AFTER UPDATE ON config
BEGIN
    UPDATE config SET updated_at = CURRENT_TIMESTAMP WHERE key = NEW.key;
END;

CREATE TRIGGER IF NOT EXISTS update_api_quota_timestamp 
AFTER UPDATE ON api_quota
BEGIN
    UPDATE api_quota SET updated_at = CURRENT_TIMESTAMP WHERE provider = NEW.provider;
END;

-- ===== 视图：统计信息 =====

-- 今日统计视图
CREATE VIEW IF NOT EXISTS v_today_stats AS
SELECT 
    (SELECT COUNT(*) FROM products WHERE DATE(created_at) = DATE('now')) as products_today,
    (SELECT COUNT(*) FROM products WHERE status = '已发布' AND DATE(published_at) = DATE('now')) as published_today,
    (SELECT COUNT(*) FROM tasks WHERE DATE(created_at) = DATE('now')) as tasks_today,
    (SELECT COUNT(*) FROM tasks WHERE status = 'completed' AND DATE(completed_at) = DATE('now')) as tasks_completed_today,
    (SELECT COUNT(*) FROM ai_usage WHERE DATE(created_at) = DATE('now')) as ai_calls_today,
    (SELECT SUM(total_tokens) FROM ai_usage WHERE DATE(created_at) = DATE('now')) as ai_tokens_today;

-- AI使用统计视图（最近7天）
CREATE VIEW IF NOT EXISTS v_ai_stats_7days AS
SELECT 
    provider,
    COUNT(*) as total_calls,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_calls,
    AVG(latency) as avg_latency,
    SUM(total_tokens) as total_tokens,
    DATE(created_at) as date
FROM ai_usage
WHERE created_at >= DATE('now', '-7 days')
GROUP BY provider, DATE(created_at)
ORDER BY date DESC, provider;

-- 商品发布成功率视图
CREATE VIEW IF NOT EXISTS v_publish_success_rate AS
SELECT 
    platform,
    COUNT(*) as total,
    SUM(CASE WHEN status = '已发布' THEN 1 ELSE 0 END) as published,
    ROUND(CAST(SUM(CASE WHEN status = '已发布' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as success_rate
FROM products
GROUP BY platform;

-- ===== 清理过期数据的存储过程（手动调用）=====

-- 清理30天前的日志
-- DELETE FROM logs WHERE created_at < datetime('now', '-30 days');

-- 清理90天前的AI使用记录
-- DELETE FROM ai_usage WHERE created_at < datetime('now', '-90 days');

-- ===== 数据库版本信息 =====
CREATE TABLE IF NOT EXISTS db_version (
    version TEXT PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO db_version (version, description) VALUES 
    ('1.0.0', 'Initial database schema');

-- ===== 完成 =====
-- Schema创建完成
-- 使用方法：sqlite3 database.db < schema.sql

