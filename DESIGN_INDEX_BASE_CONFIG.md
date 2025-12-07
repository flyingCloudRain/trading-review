# 指数基础配置设计方案

## 概述
从CSV文件中获取所有指数的基本信息（代码和名称），作为基础配置，在指数关注管理中可以从这个基础配置中选择需要关注的指数。

## 设计目标
1. **数据源**：从CSV文件（`data/stock_zh_index_spot_sina.csv`）读取所有指数信息
2. **存储方式**：JSON配置文件（`data/index_base_config.json`）
3. **代码格式**：统一为6位格式，保留前导0（如 `000001`、`399006`）
4. **功能**：在关注管理页面中可以从基础配置中选择指数

## 架构设计

### 1. 数据层
- **CSV文件**：`data/stock_zh_index_spot_sina.csv`
  - 包含所有指数的实时数据
  - 字段：代码、名称、最新价等
- **基础配置JSON**：`data/index_base_config.json`
  - 存储所有指数的基本信息（代码和名称）
  - 格式：
    ```json
    {
      "indices": [
        {
          "code": "000001",
          "name": "上证指数",
          "raw_code": "sh000001"
        },
        ...
      ],
      "total_count": 564,
      "updated_at": "2025-11-20T..."
    }
    ```

### 2. 服务层
- **`utils/index_base_config.py`**：指数基础配置管理工具
  - `load_index_base_config()`：加载基础配置
  - `save_index_base_config()`：保存基础配置
  - `generate_base_config_from_csv()`：从CSV生成基础配置
  - `get_index_by_code()`：根据代码获取指数信息
  - `get_index_name()`：根据代码获取指数名称
  - `search_indices()`：搜索指数（根据代码或名称）

### 3. 应用层
- **`pages/3_关注管理.py`**：关注管理页面
  - 从基础配置加载所有可用指数
  - 支持搜索和筛选
  - 支持单个和批量添加关注指数
  - 显示格式：指数名称（指数代码）

## 工作流程

### 初始化流程
1. 运行 `scripts/generate_index_base_config.py`
2. 从CSV文件读取所有指数
3. 标准化代码为6位格式
4. 保存到 `data/index_base_config.json`

### 使用流程
1. 用户打开"关注管理"页面
2. 系统从 `index_base_config.json` 加载所有指数
3. 过滤出未关注的指数
4. 用户可以通过搜索查找指数
5. 用户选择指数并添加到关注列表
6. 关注列表保存到 `data/focused_indices.json`

## 数据格式

### 基础配置格式
```json
{
  "indices": [
    {
      "code": "000001",      // 6位标准化代码
      "name": "上证指数",     // 指数名称
      "raw_code": "sh000001" // 原始代码（带前缀）
    }
  ],
  "total_count": 564,
  "updated_at": "2025-11-20T21:00:00"
}
```

### 关注指数格式
```json
{
  "indices": [
    "000001",  // 6位标准化代码
    "000016",
    "000300"
  ],
  "updated_at": "2025-11-20T21:00:00"
}
```

## 优势

1. **离线可用**：不依赖API，即使网络不稳定也能使用
2. **完整数据**：包含CSV中的所有指数（564个）
3. **快速搜索**：本地JSON文件，搜索速度快
4. **统一格式**：代码统一为6位格式，便于管理
5. **易于维护**：可以定期更新CSV文件并重新生成配置

## 更新机制

### 手动更新
运行脚本重新生成基础配置：
```bash
python scripts/generate_index_base_config.py
```

### 自动更新（可选）
可以在定时任务中添加更新逻辑，定期从最新的CSV文件生成基础配置。

## 使用示例

### 在关注管理页面
1. 用户打开"关注管理" → "关注指数管理"标签页
2. 系统显示当前关注的指数列表
3. 在"添加关注指数"区域：
   - 显示基础配置中的指数总数
   - 支持搜索（代码或名称）
   - 下拉选择框显示：指数名称（指数代码）
   - 支持单个添加和批量添加

### 代码示例
```python
# 加载基础配置
from utils.index_base_config import load_index_base_config, search_indices

# 获取所有指数
all_indices = load_index_base_config()

# 搜索指数
results = search_indices('上证')

# 获取指数名称
from utils.index_base_config import get_index_name
name = get_index_name('000001')  # 返回 '上证指数'
```

## 文件结构

```
project/
├── data/
│   ├── stock_zh_index_spot_sina.csv      # CSV数据源
│   ├── index_base_config.json            # 基础配置（自动生成）
│   └── focused_indices.json              # 关注指数列表
├── utils/
│   └── index_base_config.py             # 基础配置管理工具
├── scripts/
│   └── generate_index_base_config.py    # 生成基础配置脚本
└── pages/
    └── 3_关注管理.py                      # 关注管理页面
```

