# JieDimension Toolkit - API文档 📚

> **版本**: v1.14.0  
> **更新日期**: 2025-10-12

---

## 📋 目录

1. [核心模块](#核心模块)
2. [AI引擎](#ai引擎)
3. [数据库](#数据库)
4. [插件系统](#插件系统)
5. [平台适配器](#平台适配器)

---

## 🎯 核心模块

### AIEngine

智能AI调度引擎，支持多个AI提供商。

#### 初始化

```python
from core.ai_engine import AIEngine, TaskComplexity

engine = AIEngine()
```

#### 方法

##### `generate()`

生成文本内容

```python
async def generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    complexity: TaskComplexity = TaskComplexity.SIMPLE,
    max_tokens: int = 500,
    temperature: float = 0.7
) -> AIResponse
```

**参数**：
- `prompt` (str): 提示词
- `system_prompt` (str, 可选): 系统提示词
- `complexity` (TaskComplexity): 任务复杂度
- `max_tokens` (int): 最大生成token数
- `temperature` (float): 温度参数（0-1）

**返回**：
- `AIResponse`: AI响应对象

**示例**：
```python
response = await engine.generate(
    prompt="优化这个标题：二手iPhone",
    system_prompt="你是电商标题优化专家",
    complexity=TaskComplexity.SIMPLE,
    max_tokens=100
)

if response.success:
    print(response.content)
    print(f"提供商: {response.provider}")
    print(f"耗时: {response.latency:.2f}秒")
```

##### `test_connection()`

测试AI提供商连接

```python
async def test_connection(provider: str) -> Dict[str, Any]
```

**参数**：
- `provider` (str): 提供商名称（"ollama", "gemini", "claude", "ernie"）

**返回**：
- `dict`: 测试结果
  - `success` (bool): 是否成功
  - `message` (str): 消息
  - `latency` (float): 延迟（秒）

**示例**：
```python
result = await engine.test_connection("gemini")
if result["success"]:
    print(f"连接成功，延迟: {result['latency']:.2f}秒")
else:
    print(f"连接失败: {result['message']}")
```

---

### Database

数据库管理器

#### 初始化

```python
from core.database import Database

db = Database("data/database.db")
await db.connect()
```

#### 任务管理

##### `create_task()`

创建任务

```python
async def create_task(
    type: str,
    platform: Optional[str] = None,
    status: str = "pending",
    progress: float = 0.0,
    data: Optional[Dict] = None,
    result: Optional[Dict] = None
) -> int
```

**返回**: 任务ID

**示例**：
```python
task_id = await db.create_task(
    type="xianyu_publish",
    platform="xianyu",
    status="pending",
    data={"title": "测试商品"}
)
```

##### `get_tasks()`

获取任务列表

```python
async def get_tasks(
    type: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
) -> List[Dict]
```

**参数**：
- `type` (str, 可选): 任务类型
- `platform` (str, 可选): 平台
- `status` (str, 可选): 状态
- `start_date` (str, 可选): 开始日期（ISO格式）
- `end_date` (str, 可选): 结束日期（ISO格式）
- `limit` (int): 最大返回数量

**返回**: 任务列表

**示例**：
```python
# 获取所有完成的闲鱼任务
tasks = await db.get_tasks(
    type="xianyu_publish",
    status="completed",
    limit=50
)

for task in tasks:
    print(f"任务{task['id']}: {task['status']}")
```

##### `update_task_status()`

更新任务状态

```python
async def update_task_status(
    task_id: int,
    status: str,
    progress: Optional[float] = None,
    result: Optional[Dict] = None,
    error: Optional[str] = None
)
```

**示例**：
```python
await db.update_task_status(
    task_id=1,
    status="completed",
    progress=100.0,
    result={"success": True, "url": "https://..."}
)
```

##### `clear_tasks()`

清空任务

```python
async def clear_tasks(
    type: Optional[str] = None,
    status: Optional[str] = None,
    before_date: Optional[str] = None
) -> int
```

**返回**: 删除的任务数

**示例**：
```python
# 清空所有已完成的任务
deleted = await db.clear_tasks(status="completed")
print(f"删除了{deleted}个任务")
```

#### 商品管理

##### `insert_products()`

插入商品

```python
async def insert_products(products: List[Dict]) -> int
```

**参数**：
- `products` (List[Dict]): 商品列表

**返回**: 插入的商品数量

**示例**：
```python
products = [
    {
        "title": "测试商品1",
        "price": 99.9,
        "category": "数码产品",
        "description": "测试描述"
    }
]

count = await db.insert_products(products)
print(f"插入了{count}个商品")
```

##### `get_products()`

获取商品列表

```python
async def get_products(
    status: Optional[str] = None,
    limit: int = 100
) -> List[Dict]
```

##### `update_product_status()`

更新商品状态

```python
async def update_product_status(
    product_id: int,
    status: str,
    published_id: Optional[str] = None
)
```

#### AI统计

##### `log_ai_usage()`

记录AI使用

```python
async def log_ai_usage(
    provider: str,
    model: str,
    task_type: str,
    complexity: int,
    prompt_tokens: int,
    completion_tokens: int,
    latency: float,
    success: bool = True
)
```

##### `get_ai_stats_summary()`

获取AI统计摘要

```python
async def get_ai_stats_summary(days: int = 7) -> Dict[str, Any]
```

**返回**：
```python
{
    "total_calls": 100,
    "successful_calls": 98,
    "failed_calls": 2,
    "success_rate": 0.98,
    "avg_latency": 2.5,
    "providers": {
        "ollama": {"calls": 50, "success_rate": 1.0},
        "gemini": {"calls": 50, "success_rate": 0.96}
    }
}
```

---

## 🤖 AI引擎

### TaskComplexity

任务复杂度枚举

```python
class TaskComplexity(Enum):
    SIMPLE = 1      # 简单任务（标题优化）
    MEDIUM = 2      # 中等任务（描述生成）
    COMPLEX = 3     # 复杂任务（长文章）
    ADVANCED = 4    # 高级任务（创意内容）
```

### AIResponse

AI响应数据类

```python
@dataclass
class AIResponse:
    success: bool           # 是否成功
    content: str           # 生成的内容
    provider: str          # 使用的提供商
    model: str            # 使用的模型
    latency: float        # 延迟（秒）
    prompt_tokens: int    # 输入tokens
    completion_tokens: int # 输出tokens
    error: Optional[str]  # 错误信息
```

---

## 🔌 插件系统

### BasePlatformPlugin

插件基类

```python
from plugins.base_plugin import BasePlatformPlugin

class MyPlugin(BasePlatformPlugin):
    def __init__(self):
        super().__init__()
        self.name = "MyPlugin"
        self.version = "1.0.0"
    
    async def optimize_title(self, title: str) -> str:
        """优化标题"""
        pass
    
    async def generate_tags(self, content: str) -> List[str]:
        """生成标签"""
        pass
    
    async def publish(self, content: Dict) -> Dict:
        """发布内容"""
        pass
```

### XianyuPublisher

闲鱼发布器

#### 初始化

```python
from plugins.xianyu.publisher import XianyuPublisher

publisher = XianyuPublisher()
```

#### 方法

##### `optimize_product()`

优化商品信息

```python
async def optimize_product(product: Dict) -> Dict
```

**参数**：
```python
product = {
    "title": "二手iPhone 13",
    "price": 3999,
    "category": "数码产品",
    "description": "9成新"
}
```

**返回**：
```python
{
    "title": "【95新】iPhone 13 白色 128G 🔥",
    "title_original": "二手iPhone 13",
    "price": 3999,
    "category": "数码产品",
    "description": "精心使用9成新，无划痕...",
    "ai_optimized": True
}
```

##### `batch_publish()`

批量发布商品

```python
async def batch_publish(
    products: List[Dict],
    real_publish: bool = False,
    progress_callback: Optional[Callable] = None
) -> Dict
```

**参数**：
- `products` (List[Dict]): 商品列表
- `real_publish` (bool): 是否真实发布
- `progress_callback` (Callable, 可选): 进度回调

**返回**：
```python
{
    "total": 10,
    "success": 9,
    "failed": 1,
    "results": [...]
}
```

**示例**：
```python
def on_progress(current, total, item):
    print(f"进度: {current}/{total} - {item['title']}")

results = await publisher.batch_publish(
    products=products,
    real_publish=True,
    progress_callback=on_progress
)

print(f"成功: {results['success']}, 失败: {results['failed']}")
```

---

## 🔄 内容适配器

### UniversalContentAdapter

通用内容适配器

#### 初始化

```python
from core.content_adapter import UniversalContentAdapter

adapter = UniversalContentAdapter()
```

#### 方法

##### `adapt_content()`

适配内容到指定平台

```python
def adapt_content(
    content: Dict,
    target_platform: str
) -> Dict
```

**参数**：
```python
content = {
    "title": "这是一个很长的标题，可能超过某些平台的限制",
    "body": "正文内容...",
    "description": "描述...",
    "tags": ["标签1", "标签2"],
    "images": ["img1.jpg", "img2.jpg"],
    "price": 99.9
}
```

**平台**：
- `"xianyu"` - 闲鱼
- `"xiaohongshu"` - 小红书
- `"zhihu"` - 知乎
- `"bilibili"` - B站

**返回**：适配后的内容

**示例**：
```python
# 适配到小红书
xiaohongshu_content = adapter.adapt_content(
    content=content,
    target_platform="xiaohongshu"
)

# 标题自动截断到20字
# 自动添加emoji
# 图片限制为9张
```

---

## 🎨 平台适配器

### 小红书适配器

```python
from plugins.batch_publisher.adapters.xiaohongshu_adapter import XiaohongshuAdapter

adapter = XiaohongshuAdapter()
```

**特点**：
- 标题限制：20字
- 必须包含emoji
- 支持最多9张图片
- 支持10个标签

### 知乎适配器

```python
from plugins.batch_publisher.adapters.zhihu_adapter import ZhihuAdapter

adapter = ZhihuAdapter()
```

**特点**：
- 标题限制：50字
- 移除所有emoji
- 支持Markdown格式
- 支持5个标签

### B站适配器

```python
from plugins.batch_publisher.adapters.bilibili_adapter import BilibiliAdapter

adapter = BilibiliAdapter()
```

**特点**：
- 标题限制：80字
- 动态限制：233字
- 支持10个标签
- 分区特色优化

---

## 🌐 浏览器自动化

### BrowserAutomation

浏览器自动化基类

```python
from core.browser_automation import BrowserAutomation

automation = BrowserAutomation(headless=False)
```

#### 方法

##### `launch()`

启动浏览器

```python
async def launch()
```

##### `close()`

关闭浏览器

```python
async def close()
```

##### `navigate()`

导航到URL

```python
async def navigate(url: str, wait_until: str = "domcontentloaded")
```

##### `screenshot()`

截图

```python
async def screenshot(
    path: Optional[str] = None,
    full_page: bool = False
) -> bytes
```

### XianyuAutomation

闲鱼自动化

```python
from core.browser_automation import XianyuAutomation

xianyu = XianyuAutomation(headless=False)
```

#### 方法

##### `login()`

登录闲鱼

```python
async def login(wait_time: int = 30) -> bool
```

##### `publish_product()`

发布商品

```python
async def publish_product(
    product: Dict,
    screenshots_dir: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> Dict
```

**参数**：
```python
product = {
    "title": "商品标题",
    "price": 99.9,
    "category": "数码产品",
    "description": "描述",
    "images": ["img1.jpg"]
}
```

**返回**：
```python
{
    "success": True,
    "product_id": "12345",
    "url": "https://...",
    "screenshots": [...]
}
```

---

## 📊 导出工具

### ExportManager

导出管理器

```python
from utils.export import ExportManager

exporter = ExportManager(db)
```

#### 方法

##### `export_full_report()`

导出完整报告

```python
async def export_full_report(output_path: str) -> bool
```

**工作表**：
1. 概览 - 关键指标
2. AI统计 - AI使用情况
3. 任务统计 - 任务详情
4. 商品列表 - 商品数据

##### `export_ai_stats_only()`

仅导出AI统计

```python
async def export_ai_stats_only(output_path: str) -> bool
```

---

## 🔧 工具函数

### 文本处理

```python
from utils.text_utils import truncate_text, clean_text, extract_keywords

# 截断文本
truncated = truncate_text("很长的文本...", max_length=20, suffix="...")

# 清理文本
cleaned = clean_text("  文本  \n\n  ")

# 提取关键词
keywords = extract_keywords("这是一段包含关键词的文本", top_n=5)
```

### 图片处理

```python
from utils.image_utils import resize_image, compress_image

# 调整大小
resized = resize_image("input.jpg", max_width=800, max_height=600)

# 压缩图片
compressed = compress_image("input.jpg", quality=85)
```

---

## 📝 使用示例

### 示例1：完整发布流程

```python
import asyncio
from core.database import Database
from plugins.xianyu.data_importer import DataImporter
from plugins.xianyu.publisher import XianyuPublisher

async def main():
    # 1. 初始化
    db = Database()
    await db.connect()
    
    importer = DataImporter()
    publisher = XianyuPublisher()
    
    # 2. 导入数据
    products = importer.import_from_excel("products.xlsx")
    print(f"导入了{len(products)}个商品")
    
    # 3. 批量发布
    def on_progress(current, total, item):
        print(f"进度: {current}/{total}")
    
    results = await publisher.batch_publish(
        products=products,
        real_publish=True,
        progress_callback=on_progress
    )
    
    # 4. 显示结果
    print(f"成功: {results['success']}")
    print(f"失败: {results['failed']}")
    
    # 5. 清理
    await db.close()

asyncio.run(main())
```

### 示例2：AI内容生成

```python
from core.ai_engine import AIEngine, TaskComplexity

async def generate_content():
    engine = AIEngine()
    
    # 生成标题
    title_response = await engine.generate(
        prompt="为这个产品生成标题：二手MacBook Pro 2020",
        complexity=TaskComplexity.SIMPLE
    )
    
    # 生成描述
    desc_response = await engine.generate(
        prompt=f"为标题'{title_response.content}'生成详细描述",
        complexity=TaskComplexity.MEDIUM
    )
    
    return {
        "title": title_response.content,
        "description": desc_response.content
    }
```

### 示例3：跨平台发布

```python
from plugins.batch_publisher.task_manager import BatchPublishManager

async def batch_publish():
    manager = BatchPublishManager()
    
    content = {
        "title": "我的产品",
        "body": "详细介绍...",
        "tags": ["标签1", "标签2"],
        "images": ["1.jpg", "2.jpg"]
    }
    
    platforms = ["xianyu", "xiaohongshu", "zhihu"]
    
    results = await manager.publish_to_multiple_platforms(
        content=content,
        platforms=platforms
    )
    
    for platform, result in results.items():
        print(f"{platform}: {result['success']}")
```

---

## 🔒 安全注意事项

### API密钥管理

- API密钥使用Fernet加密存储
- 不要在代码中硬编码密钥
- 定期更换密钥

### Cookie安全

- Cookie自动加密存储
- 过期自动提示重新登录
- 不要分享Cookie文件

### 数据备份

定期备份：
- `data/database.db`
- `config/credentials.enc`
- `config/settings.json`

---

## 📚 更多资源

- **用户手册**: `docs/用户手册.md`
- **技术设计**: `JieDimension-Toolkit_技术设计文档.md`
- **快速开始**: `JieDimension-Toolkit_快速启动指南.md`
- **README**: `README.md`

---

**版本**: v1.14.0  
**更新日期**: 2025-10-12  
**© 2025 JieDimension Studio**

