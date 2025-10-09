"""
JieDimension Toolkit - Excel/CSV 数据导入器
支持从 Excel 和 CSV 文件导入商品数据
Version: 1.0.0
"""

import pandas as pd
import os
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataImporter:
    """数据导入器"""
    
    def __init__(self):
        """初始化导入器"""
        self.required_columns = ["title", "price", "category"]
        self.optional_columns = ["description", "images", "quantity", "status"]
    
    def import_from_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """
        从 Excel 导入商品数据
        
        Args:
            file_path: Excel 文件路径
            
        Returns:
            商品列表
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 缺少必填列
        """
        logger.info(f"📥 开始导入Excel: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            # 读取Excel
            df = pd.read_excel(file_path)
            
            logger.info(f"读取到 {len(df)} 行数据")
            
            # 验证必填列
            missing_cols = set(self.required_columns) - set(df.columns)
            if missing_cols:
                raise ValueError(f"缺少必填列: {', '.join(missing_cols)}")
            
            # 转换为字典列表
            products = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    product = self._clean_product_data(row, idx)
                    products.append(product)
                except Exception as e:
                    error_msg = f"第 {idx + 2} 行数据错误: {e}"
                    logger.warning(f"⚠️ {error_msg}")
                    errors.append(error_msg)
            
            logger.info(f"✅ 成功导入 {len(products)} 个商品")
            if errors:
                logger.warning(f"⚠️ {len(errors)} 行数据有错误")
                for error in errors[:5]:  # 只显示前5个错误
                    logger.warning(f"   - {error}")
            
            return products
            
        except Exception as e:
            logger.error(f"❌ 导入Excel失败: {e}")
            raise
    
    def import_from_csv(self, file_path: str, encoding: str = 'utf-8-sig') -> List[Dict[str, Any]]:
        """
        从 CSV 导入商品数据
        
        Args:
            file_path: CSV 文件路径
            encoding: 文件编码
            
        Returns:
            商品列表
        """
        logger.info(f"📥 开始导入CSV: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            # 读取CSV
            df = pd.read_csv(file_path, encoding=encoding)
            
            logger.info(f"读取到 {len(df)} 行数据")
            
            # 验证必填列
            missing_cols = set(self.required_columns) - set(df.columns)
            if missing_cols:
                raise ValueError(f"缺少必填列: {', '.join(missing_cols)}")
            
            # 转换为字典列表
            products = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    product = self._clean_product_data(row, idx)
                    products.append(product)
                except Exception as e:
                    error_msg = f"第 {idx + 2} 行数据错误: {e}"
                    logger.warning(f"⚠️ {error_msg}")
                    errors.append(error_msg)
            
            logger.info(f"✅ 成功导入 {len(products)} 个商品")
            if errors:
                logger.warning(f"⚠️ {len(errors)} 行数据有错误")
            
            return products
            
        except Exception as e:
            logger.error(f"❌ 导入CSV失败: {e}")
            raise
    
    def _clean_product_data(self, row: pd.Series, row_index: int) -> Dict[str, Any]:
        """
        清洗商品数据
        
        Args:
            row: 数据行
            row_index: 行索引
            
        Returns:
            清洗后的商品数据
            
        Raises:
            ValueError: 数据验证失败
        """
        cleaned = {}
        
        # 1. 标题（必填）
        title = str(row.get("title", "")).strip()
        if not title or title == "nan":
            raise ValueError("标题不能为空")
        if len(title) > 100:
            logger.warning(f"⚠️ 标题过长（{len(title)}字），将自动截断")
            title = title[:100]
        cleaned["title"] = title
        
        # 2. 价格（必填）
        try:
            price = float(row.get("price", 0))
            if price <= 0:
                raise ValueError("价格必须大于0")
            cleaned["price"] = price
        except (ValueError, TypeError):
            raise ValueError(f"无效的价格: {row.get('price')}")
        
        # 3. 分类（必填）
        category = str(row.get("category", "")).strip()
        if not category or category == "nan":
            raise ValueError("分类不能为空")
        cleaned["category"] = category
        
        # 4. 描述（可选）
        description = str(row.get("description", "")).strip()
        if description and description != "nan":
            cleaned["description"] = description
        else:
            cleaned["description"] = ""
        
        # 5. 图片路径（可选）
        images = str(row.get("images", "")).strip()
        if images and images != "nan":
            # 支持分号或逗号分隔
            image_list = [
                img.strip() 
                for img in images.replace(";", ",").split(",") 
                if img.strip()
            ]
            cleaned["images"] = image_list
        else:
            cleaned["images"] = []
        
        # 6. 数量（可选）
        try:
            quantity = int(row.get("quantity", 1))
            cleaned["quantity"] = max(1, quantity)
        except (ValueError, TypeError):
            cleaned["quantity"] = 1
        
        # 7. 状态（可选）
        status = str(row.get("status", "待发布")).strip()
        cleaned["status"] = status if status and status != "nan" else "待发布"
        
        # 8. 元数据
        cleaned["import_time"] = datetime.now().isoformat()
        cleaned["row_number"] = row_index + 2  # Excel行号（+2因为表头+索引从0开始）
        cleaned["import_source"] = "excel"
        
        return cleaned
    
    def validate_images(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证图片文件是否存在
        
        Args:
            products: 商品列表
            
        Returns:
            验证后的商品列表（移除无效图片）
        """
        for product in products:
            valid_images = []
            
            for img_path in product.get("images", []):
                if os.path.exists(img_path):
                    # 检查文件格式
                    ext = os.path.splitext(img_path)[1].lower()
                    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                        valid_images.append(img_path)
                    else:
                        logger.warning(f"⚠️ 不支持的图片格式: {img_path}")
                else:
                    logger.warning(f"⚠️ 图片文件不存在: {img_path}")
            
            product["images"] = valid_images
        
        return products
    
    def export_template(self, file_path: str = "data/商品导入模板.xlsx"):
        """
        导出Excel模板
        
        Args:
            file_path: 保存路径
        """
        template_data = {
            "title": ["示例：九成新iPhone 13 128G 白色", "示例：全新AirPods Pro 2代"],
            "price": [3999, 1599],
            "category": ["数码产品", "数码配件"],
            "description": ["9成新，自用爱护，功能完好", "正品全新，未拆封"],
            "images": ["", ""],
            "quantity": [1, 2],
            "status": ["待发布", "待发布"]
        }
        
        df = pd.DataFrame(template_data)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存Excel
        df.to_excel(file_path, index=False)
        
        logger.info(f"✅ 模板已导出: {file_path}")
        print(f"\n✅ Excel模板已创建: {file_path}")
        print("\n模板说明:")
        print("  - title: 商品标题（必填）")
        print("  - price: 价格（必填）")
        print("  - category: 分类（必填）")
        print("  - description: 商品描述（可选，留空则AI自动生成）")
        print("  - images: 图片路径（可选，多个用分号分隔）")
        print("  - quantity: 数量（可选，默认1）")
        print('  - status: 状态（可选，默认"待发布"）')
        print("\n请修改模板中的示例数据后导入！\n")


# ===== 测试函数 =====

def test_importer():
    """测试导入器"""
    
    print("\n" + "="*60)
    print("🧪 测试Excel导入器")
    print("="*60)
    
    importer = DataImporter()
    
    # 1. 创建测试Excel
    print("\n1️⃣ 创建测试Excel...")
    test_data = {
        "title": [
            "二手iPhone 13 128G",
            "全新AirPods Pro 2代",
            "小米手环7",
            "索尼降噪耳机WH-1000XM5"
        ],
        "price": [3999, 1599, 199, 1999],
        "category": ["数码产品", "数码配件", "数码配件", "数码配件"],
        "description": [
            "9成新，自用爱护",
            "全新未拆封，正品保证",
            "",  # 空描述，测试AI生成
            "降噪效果一流"
        ],
        "images": ["", "", "", ""],
        "quantity": [1, 2, 5, 1],
        "status": ["待发布", "待发布", "待发布", "待发布"]
    }
    
    df = pd.DataFrame(test_data)
    
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    
    test_file = "data/test_products.xlsx"
    df.to_excel(test_file, index=False)
    print(f"✅ 测试Excel已创建: {test_file}")
    
    # 2. 导入Excel
    print("\n2️⃣ 导入Excel...")
    try:
        products = importer.import_from_excel(test_file)
        
        print(f"\n导入结果:")
        for i, p in enumerate(products, 1):
            print(f"\n商品 {i}:")
            print(f"  标题: {p['title']}")
            print(f"  价格: ¥{p['price']}")
            print(f"  分类: {p['category']}")
            print(f"  描述: {p['description'] or '(无)'}")
            print(f"  数量: {p['quantity']}")
            print(f"  状态: {p['status']}")
        
        print("\n" + "="*60)
        print(f"✅ 测试完成！成功导入 {len(products)} 个商品")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 导出模板
    print("\n3️⃣ 导出模板...")
    importer.export_template()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    test_importer()

