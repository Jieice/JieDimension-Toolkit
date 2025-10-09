"""
JieDimension Toolkit - 数据库管理器
支持商品、任务、AI使用统计等数据管理
Version: 1.17.1
"""

import aiosqlite
import json
import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def get_base_path():
    """获取程序基础路径"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent


def get_resource_path(relative_path):
    """获取资源文件路径"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / relative_path
    else:
        return Path(__file__).parent.parent / relative_path


class Database:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径（可选，默认使用BASE_DIR/data/database.db）
        """
        # 如果未提供路径，使用默认路径
        if db_path is None:
            base_path = get_base_path()
            db_path = str(base_path / "data" / "database.db")
        
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(db_path):
            base_path = get_base_path()
            db_path = str(base_path / db_path)
        
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
        
        # 确保data目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    async def connect(self):
        """连接数据库"""
        try:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row  # 返回字典形式的行
            await self.conn.execute("PRAGMA foreign_keys = ON")
            await self._init_tables()
            logger.info(f"✅ 数据库连接成功: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise
    
    async def close(self):
        """关闭数据库连接"""
        if self.conn:
            await self.conn.close()
            logger.info("数据库连接已关闭")
    
    async def _init_tables(self):
        """初始化表结构"""
        try:
            # 优先从资源目录查找schema文件（打包后）
            schema_path = get_resource_path("data/schema.sql")
            
            # 如果不存在，尝试从基础目录查找
            if not schema_path.exists():
                schema_path = get_base_path() / "data" / "schema.sql"
            
            if not schema_path.exists():
                logger.warning(f"⚠️ Schema文件不存在: {schema_path}")
                logger.info("将使用内置的默认表结构")
                # 这里可以添加默认的表结构SQL
                return
            
            # 读取并执行schema
            with open(schema_path, "r", encoding="utf-8") as f:
                sql = f.read()
            
            await self.conn.executescript(sql)
            await self.conn.commit()
            
            logger.info(f"✅ 数据库表初始化完成: {schema_path}")
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            raise
    
    # ===== 商品相关操作 =====
    
    async def insert_products(self, products: List[Dict[str, Any]]) -> int:
        """
        批量插入商品
        
        Args:
            products: 商品列表
            
        Returns:
            插入的商品数量
        """
        if not products:
            return 0
        
        sql = """
        INSERT INTO products (
            title, title_original, price, category, 
            description, images, quantity, status,
            platform, import_time, row_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        data = []
        for p in products:
            data.append((
                p.get("title", ""),
                p.get("title_original", p.get("title", "")),
                p.get("price", 0),
                p.get("category", ""),
                p.get("description", ""),
                json.dumps(p.get("images", []), ensure_ascii=False),
                p.get("quantity", 1),
                p.get("status", "待发布"),
                p.get("platform", "xianyu"),
                p.get("import_time", datetime.now().isoformat()),
                p.get("row_number", 0)
            ))
        
        try:
            cursor = await self.conn.executemany(sql, data)
            await self.conn.commit()
            
            count = cursor.rowcount
            logger.info(f"✅ 成功插入 {count} 个商品")
            return count
        except Exception as e:
            logger.error(f"❌ 插入商品失败: {e}")
            raise
    
    async def get_products(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取商品列表
        
        Args:
            status: 状态过滤
            platform: 平台过滤
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            商品列表
        """
        sql = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        if platform:
            sql += " AND platform = ?"
            params.append(platform)
        
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        try:
            cursor = await self.conn.execute(sql, params)
            rows = await cursor.fetchall()
            
            # 转换为字典并解析JSON字段
            products = []
            for row in rows:
                product = dict(row)
                # 解析images JSON
                if product.get("images"):
                    try:
                        product["images"] = json.loads(product["images"])
                    except:
                        product["images"] = []
                products.append(product)
            
            return products
        except Exception as e:
            logger.error(f"❌ 查询商品失败: {e}")
            return []
    
    async def update_product_status(
        self,
        product_id: int,
        status: str,
        published_id: Optional[str] = None,
        published_url: Optional[str] = None
    ):
        """
        更新商品状态
        
        Args:
            product_id: 商品ID
            status: 新状态
            published_id: 平台商品ID
            published_url: 商品链接
        """
        sql = """
        UPDATE products 
        SET status = ?, 
            published_id = ?,
            published_url = ?,
            published_at = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        published_at = datetime.now().isoformat() if status == "已发布" else None
        
        try:
            await self.conn.execute(sql, (
                status,
                published_id,
                published_url,
                published_at,
                product_id
            ))
            await self.conn.commit()
            logger.info(f"✅ 更新商品状态: ID={product_id}, status={status}")
        except Exception as e:
            logger.error(f"❌ 更新商品状态失败: {e}")
            raise
    
    async def delete_product(self, product_id: int):
        """
        删除商品
        
        Args:
            product_id: 商品ID
        """
        sql = "DELETE FROM products WHERE id = ?"
        
        try:
            await self.conn.execute(sql, (product_id,))
            await self.conn.commit()
            logger.info(f"✅ 删除商品: ID={product_id}")
        except Exception as e:
            logger.error(f"❌ 删除商品失败: {e}")
            raise
    
    async def count_products(self, platform: Optional[str] = None) -> int:
        """
        统计商品数量
        
        Args:
            platform: 平台名称（可选）
            
        Returns:
            int: 商品数量
        """
        if platform:
            sql = "SELECT COUNT(*) FROM products WHERE platform = ?"
            cursor = await self.conn.execute(sql, (platform,))
        else:
            sql = "SELECT COUNT(*) FROM products"
            cursor = await self.conn.execute(sql)
        
        result = await cursor.fetchone()
        return result[0] if result else 0
    
    # ===== 任务相关操作 =====
    
    async def create_task(
        self,
        task_type: str,
        name: Optional[str] = None,
        data: Optional[Dict] = None
    ) -> int:
        """
        创建任务
        
        Args:
            task_type: 任务类型
            name: 任务名称
            data: 任务数据
            
        Returns:
            任务ID
        """
        sql = """
        INSERT INTO tasks (type, name, data, status)
        VALUES (?, ?, ?, 'pending')
        """
        
        try:
            cursor = await self.conn.execute(sql, (
                task_type,
                name,
                json.dumps(data, ensure_ascii=False) if data else None
            ))
            await self.conn.commit()
            
            task_id = cursor.lastrowid
            logger.info(f"✅ 创建任务: ID={task_id}, type={task_type}")
            return task_id
        except Exception as e:
            logger.error(f"❌ 创建任务失败: {e}")
            raise
    
    async def update_task_progress(
        self,
        task_id: int,
        progress: float,
        status: Optional[str] = None
    ):
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            progress: 进度 (0-100)
            status: 状态
        """
        sql = "UPDATE tasks SET progress = ?"
        params = [progress]
        
        if status:
            sql += ", status = ?"
            params.append(status)
        
        sql += " WHERE id = ?"
        params.append(task_id)
        
        try:
            await self.conn.execute(sql, params)
            await self.conn.commit()
        except Exception as e:
            logger.error(f"❌ 更新任务进度失败: {e}")
    
    async def complete_task(
        self,
        task_id: int,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """
        完成任务
        
        Args:
            task_id: 任务ID
            result: 任务结果
            error: 错误信息
        """
        status = "failed" if error else "completed"
        
        sql = """
        UPDATE tasks 
        SET status = ?,
            progress = 100,
            result = ?,
            error = ?,
            completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        try:
            await self.conn.execute(sql, (
                status,
                json.dumps(result, ensure_ascii=False) if result else None,
                error,
                task_id
            ))
            await self.conn.commit()
            logger.info(f"✅ 任务完成: ID={task_id}, status={status}")
        except Exception as e:
            logger.error(f"❌ 完成任务失败: {e}")
    
    async def get_tasks_by_date_range(
        self,
        start_time: str,
        end_time: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取指定时间范围内的任务
        
        Args:
            start_time: 开始时间（ISO格式）
            end_time: 结束时间（ISO格式）
            status: 任务状态（可选）
            
        Returns:
            任务列表
        """
        if status:
            sql = """
            SELECT * FROM tasks 
            WHERE created_at >= ? AND created_at <= ? AND status = ?
            ORDER BY created_at DESC
            """
            cursor = await self.conn.execute(sql, (start_time, end_time, status))
        else:
            sql = """
            SELECT * FROM tasks 
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY created_at DESC
            """
            cursor = await self.conn.execute(sql, (start_time, end_time))
        
        rows = await cursor.fetchall()
        
        tasks = []
        for row in rows:
            task = dict(row)
            # 解析JSON字段
            if task.get('data'):
                task['data'] = json.loads(task['data'])
            if task.get('result'):
                task['result'] = json.loads(task['result'])
            tasks.append(task)
        
        return tasks
    
    async def get_tasks(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        start_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取任务列表（支持多条件筛选）
        
        Args:
            type: 任务类型筛选
            status: 状态筛选
            platform: 平台筛选
            start_date: 开始日期（ISO格式）
            limit: 返回数量限制
            
        Returns:
            任务列表
        """
        sql = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if type:
            sql += " AND type = ?"
            params.append(type)
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        if platform:
            sql += " AND json_extract(data, '$.platform') = ?"
            params.append(platform)
        
        if start_date:
            sql += " AND created_at >= ?"
            params.append(start_date)
        
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        try:
            cursor = await self.conn.execute(sql, params)
            rows = await cursor.fetchall()
            
            tasks = []
            for row in rows:
                task = dict(row)
                # 解析JSON字段
                if task.get('data'):
                    try:
                        task['data'] = json.loads(task['data'])
                    except:
                        pass
                if task.get('result'):
                    try:
                        task['result'] = json.loads(task['result'])
                    except:
                        pass
                tasks.append(task)
            
            logger.info(f"✅ 查询任务成功: {len(tasks)}个")
            return tasks
        except Exception as e:
            logger.error(f"❌ 查询任务失败: {e}")
            return []
    
    async def clear_tasks(
        self,
        type: Optional[str] = None,
        before_date: Optional[str] = None
    ):
        """
        清空任务记录
        
        Args:
            type: 任务类型（可选，不指定则清空所有）
            before_date: 日期（可选，清空此日期之前的任务）
        """
        sql = "DELETE FROM tasks WHERE 1=1"
        params = []
        
        if type:
            sql += " AND type = ?"
            params.append(type)
        
        if before_date:
            sql += " AND created_at < ?"
            params.append(before_date)
        
        try:
            cursor = await self.conn.execute(sql, params)
            await self.conn.commit()
            deleted_count = cursor.rowcount
            logger.info(f"✅ 清空任务成功: 删除了{deleted_count}个任务")
        except Exception as e:
            logger.error(f"❌ 清空任务失败: {e}")
    
    # ===== AI使用统计 =====
    
    async def log_ai_usage(
        self,
        provider: str,
        model: str,
        task_type: str,
        complexity: int,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency: float = 0.0,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        记录AI使用情况
        
        Args:
            provider: AI提供商
            model: 模型名称
            task_type: 任务类型
            complexity: 任务复杂度
            prompt_tokens: 输入tokens
            completion_tokens: 输出tokens
            latency: 延迟（秒）
            success: 是否成功
            error: 错误信息
        """
        sql = """
        INSERT INTO ai_usage (
            provider, model, task_type, complexity,
            prompt_tokens, completion_tokens, total_tokens,
            latency, success, error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        total_tokens = prompt_tokens + completion_tokens
        
        try:
            await self.conn.execute(sql, (
                provider, model, task_type, complexity,
                prompt_tokens, completion_tokens, total_tokens,
                latency, 1 if success else 0, error
            ))
            await self.conn.commit()
        except Exception as e:
            logger.error(f"❌ 记录AI使用失败: {e}")
    
    async def get_ai_stats(
        self,
        provider: Optional[str] = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        获取AI使用统计
        
        Args:
            provider: AI提供商（可选）
            days: 统计天数
            
        Returns:
            统计数据
        """
        sql = """
        SELECT 
            provider,
            COUNT(*) as total_calls,
            SUM(prompt_tokens) as total_prompt_tokens,
            SUM(completion_tokens) as total_completion_tokens,
            SUM(total_tokens) as total_tokens,
            AVG(latency) as avg_latency,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
        FROM ai_usage
        WHERE created_at >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        if provider:
            sql += " AND provider = ?"
            params.append(provider)
        
        sql += " GROUP BY provider"
        
        try:
            cursor = await self.conn.execute(sql, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ 查询AI统计失败: {e}")
            return []
    
    async def get_ai_stats_summary(self) -> Dict[str, Any]:
        """
        获取AI使用统计摘要（用于仪表板）
        
        Returns:
            统计摘要
        """
        sql = """
        SELECT 
            COUNT(*) as total_calls,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
            AVG(latency) as avg_latency,
            SUM(total_tokens) as total_tokens
        FROM ai_usage
        """
        
        try:
            cursor = await self.conn.execute(sql)
            row = await cursor.fetchone()
            
            if row:
                result = dict(row)
                # 计算成功率
                if result['total_calls'] > 0:
                    result['success_rate'] = (result['success_count'] / result['total_calls']) * 100
                else:
                    result['success_rate'] = 0
                return result
            else:
                return {
                    'total_calls': 0,
                    'success_count': 0,
                    'avg_latency': 0,
                    'total_tokens': 0,
                    'success_rate': 0
                }
        except Exception as e:
            logger.error(f"❌ 查询AI统计摘要失败: {e}")
            return {
                'total_calls': 0,
                'success_count': 0,
                'avg_latency': 0,
                'total_tokens': 0,
                'success_rate': 0
            }
    
    async def get_ai_calls(
        self,
        start_time: str,
        end_time: str,
        provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取指定时间范围内的AI调用记录（用于图表）
        
        Args:
            start_time: 开始时间（ISO格式）
            end_time: 结束时间（ISO格式）
            provider: AI提供商（可选）
            
        Returns:
            AI调用记录列表
        """
        if provider:
            sql = """
            SELECT 
                id, provider, model, task_type, complexity,
                prompt_tokens, completion_tokens, total_tokens,
                latency, success, error, created_at
            FROM ai_usage
            WHERE created_at >= ? AND created_at <= ? AND provider = ?
            ORDER BY created_at ASC
            """
            params = (start_time, end_time, provider)
        else:
            sql = """
            SELECT 
                id, provider, model, task_type, complexity,
                prompt_tokens, completion_tokens, total_tokens,
                latency, success, error, created_at
            FROM ai_usage
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY created_at ASC
            """
            params = (start_time, end_time)
        
        try:
            cursor = await self.conn.execute(sql, params)
            rows = await cursor.fetchall()
            
            calls = []
            for row in rows:
                call = dict(row)
                # 将success字段从0/1转换为布尔值
                call['success'] = bool(call['success'])
                calls.append(call)
            
            return calls
        except Exception as e:
            logger.error(f"❌ 查询AI调用记录失败: {e}")
            return []
    
    # ===== 配置管理 =====
    
    async def get_config(self, key: str) -> Optional[str]:
        """
        获取配置值
        
        Args:
            key: 配置键
            
        Returns:
            配置值
        """
        sql = "SELECT value FROM config WHERE key = ?"
        
        try:
            cursor = await self.conn.execute(sql, (key,))
            row = await cursor.fetchone()
            return row["value"] if row else None
        except Exception as e:
            logger.error(f"❌ 获取配置失败: {e}")
            return None
    
    async def set_config(self, key: str, value: str):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        sql = """
        INSERT OR REPLACE INTO config (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        """
        
        try:
            await self.conn.execute(sql, (key, value))
            await self.conn.commit()
        except Exception as e:
            logger.error(f"❌ 设置配置失败: {e}")


# ===== 测试函数 =====

async def test_database():
    """测试数据库功能"""
    
    print("\n" + "="*60)
    print("🧪 测试数据库管理器")
    print("="*60)
    
    # 创建数据库实例
    db = Database("data/database.db")
    
    try:
        # 1. 连接数据库
        print("\n1️⃣ 连接数据库...")
        await db.connect()
        
        # 2. 插入测试商品
        print("\n2️⃣ 插入测试商品...")
        test_products = [
            {
                "title": "测试商品1 - iPhone 13",
                "price": 3999,
                "category": "数码产品",
                "description": "测试描述",
                "images": ["image1.jpg"],
                "import_time": datetime.now().isoformat(),
                "row_number": 1
            },
            {
                "title": "测试商品2 - AirPods Pro",
                "price": 1599,
                "category": "数码配件",
                "description": "测试描述",
                "images": ["image2.jpg"],
                "import_time": datetime.now().isoformat(),
                "row_number": 2
            }
        ]
        
        count = await db.insert_products(test_products)
        print(f"成功插入 {count} 个商品")
        
        # 3. 查询商品
        print("\n3️⃣ 查询商品...")
        products = await db.get_products(status="待发布", limit=10)
        print(f"查询到 {len(products)} 个商品")
        for p in products:
            print(f"  - {p['title']} (¥{p['price']})")
        
        # 4. 记录AI使用
        print("\n4️⃣ 记录AI使用...")
        await db.log_ai_usage(
            provider="ollama",
            model="deepseek-r1:1.5b",
            task_type="title_optimization",
            complexity=1,
            prompt_tokens=50,
            completion_tokens=30,
            latency=2.5,
            success=True
        )
        print("AI使用记录成功")
        
        # 5. 查看AI统计
        print("\n5️⃣ 查看AI统计...")
        stats = await db.get_ai_stats()
        for stat in stats:
            print(f"  - {stat['provider']}: {stat['total_calls']} 次调用")
        
        print("\n" + "="*60)
        print("✅ 数据库测试完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭连接
        await db.close()


if __name__ == "__main__":
    import asyncio
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    asyncio.run(test_database())

