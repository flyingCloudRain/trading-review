# 项目目录结构说明

## 📁 完整目录结构

```
review/
├── api/                          # API路由模块
│   ├── __init__.py
│   ├── board_change.py          # 板块异动API
│   ├── dtgc.py                  # 跌停股票API
│   ├── sector.py                # 板块信息API
│   ├── stock_index.py           # 股票指数API
│   ├── trading_review.py        # 交易复盘API
│   ├── zbgc.py                  # 炸板股票API
│   └── zt_pool.py               # 涨停股票API
│
├── components/                    # Streamlit可视化组件（新增）
│   ├── __init__.py
│   ├── kpi_cards.py             # KPI指标卡片组件
│   ├── date_selector.py         # 日期选择器组件
│   └── sector_selector.py       # 板块选择器组件
│
├── chart_config/                 # 图表配置模块（新增）
│   ├── __init__.py
│   └── chart_config.py          # 图表配置（颜色、尺寸等）
│
├── database/                     # 数据库连接模块
│   ├── __init__.py
│   ├── db_supabase.py          # Supabase数据库连接
│   └── db.py                    # 数据库统一入口
│
├── docs/                         # 文档目录
│   ├── CHART_DASHBOARD_DESIGN.md
│   ├── CHART_DASHBOARD_QUICK_START.md
│   ├── CHART_IMPLEMENTATION_EXAMPLES.md
│   ├── DATABASE_DESIGN.md
│   ├── DATABASE_ER_DIAGRAM.md
│   ├── DATABASE_RECOMMENDATION.md
│   ├── SUPABASE_DESIGN.md
│   ├── VISUALIZATION_DATABASE.md
│   └── VISUALIZATION_SETUP.md
│
├── models/                       # 数据模型
│   ├── __init__.py
│   ├── dtgc_pool_history.py    # 跌停股票池历史模型
│   ├── sector_history.py       # 板块历史模型
│   ├── trading_review.py        # 交易复盘模型
│   ├── zbgc_pool_history.py    # 炸板股票池历史模型
│   └── zt_pool_history.py      # 涨停股票池历史模型
│
├── pages/                        # Streamlit多页面（新增）
│   ├── __init__.py
│   ├── 1_板块仪表盘.py         # 板块信息仪表盘页面
│   └── 2_板块趋势分析.py       # 板块趋势分析页面
│
├── scripts/                      # 工具脚本
│   ├── check_database.py
│   ├── configure_supabase.py
│   ├── diagnose_supabase.py
│   ├── export_board_changes.py
│   ├── export_dtgc.py
│   ├── export_zbgc.py
│   ├── export_zt_pool.py
│   ├── manual_save_sectors.py
│   ├── quick_test_supabase.py
│   ├── setup_supabase_connection.py
│   ├── supabase_setup.sql
│   └── test_supabase_connection.py
│
├── services/                     # 业务逻辑服务
│   ├── __init__.py
│   ├── board_change_service.py
│   ├── dtgc_pool_history_service.py
│   ├── dtgc_service.py
│   ├── sector_history_service.py
│   ├── sector_service.py
│   ├── stock_index_service.py
│   ├── trading_review_service.py
│   ├── zbgc_pool_history_service.py
│   ├── zbgc_service.py
│   ├── zt_pool_history_service.py
│   └── zt_pool_service.py
│
├── tasks/                        # 定时任务
│   ├── __init__.py
│   └── sector_scheduler.py      # 板块数据定时任务
│
├── tests/                        # 单元测试
│   ├── __init__.py
│   ├── test_sector_service.py
│   └── test_trading_review_service.py
│
├── utils/                        # 工具函数
│   ├── __init__.py
│   ├── board_change_excel_export.py
│   ├── chart_utils.py           # 图表工具函数（新增）
│   ├── data_loader.py           # 数据加载工具（新增）
│   ├── dtgc_excel_export.py
│   ├── excel_export.py
│   ├── time_utils.py
│   ├── zbgc_excel_export.py
│   └── zt_pool_excel_export.py
│
├── data/                         # 数据目录
│   ├── trading_review.db        # SQLite数据库（后备）
│   ├── 板块信息历史.xlsx
│   ├── 板块异动.xlsx
│   ├── 涨停股票池.xlsx
│   ├── 炸板股票池.xlsx
│   └── 跌停股票池.xlsx
│
├── app.py                        # Flask应用入口
├── config.py                     # 应用配置
├── config_supabase.py           # Supabase配置
├── streamlit_app.py             # Streamlit可视化应用
├── requirements.txt             # Python依赖
├── .gitignore                   # Git忽略文件
│
└── README文件
    ├── README.md                # 主README
    ├── README_SCHEDULER.md      # 定时任务说明
    ├── README_STREAMLIT.md      # Streamlit说明
    ├── README_SUPABASE.md       # Supabase说明
    ├── README_ZT_POOL.md        # 涨停股票池说明
    ├── README_VISUALIZATION.md  # 可视化说明（新增）
    └── PROJECT_STRUCTURE.md     # 项目结构说明（本文件）
```

## 🎯 新增目录说明

### 1. `components/` - 可视化组件
可复用的Streamlit UI组件，遵循单一职责原则。

**文件**:
- `kpi_cards.py` - KPI指标卡片
- `date_selector.py` - 日期选择器
- `sector_selector.py` - 板块选择器

### 2. `config/` - 配置模块
集中管理配置信息。

**文件**:
- `chart_config.py` - 图表配置（颜色、尺寸、布局等）

### 3. `pages/` - Streamlit多页面
Streamlit会自动识别此目录下的文件作为独立页面。

**文件**:
- `1_板块仪表盘.py` - 板块信息仪表盘
- `2_板块趋势分析.py` - 板块趋势分析

**注意**: 文件名前的数字用于页面排序。

### 4. `utils/` - 工具函数（扩展）
新增可视化相关的工具函数。

**新增文件**:
- `chart_utils.py` - 图表创建工具函数
- `data_loader.py` - 数据加载工具（带缓存）

## 📊 模块依赖关系

```
streamlit_app.py / pages/
    ├── components/          (UI组件)
    ├── utils/
    │   ├── data_loader.py   (数据加载，带缓存)
    │   └── chart_utils.py   (图表创建)
    └── config/
        └── chart_config.py  (图表配置)
```

## 🔄 使用方式

### 方式1: 单页面应用（现有方式）
使用 `streamlit_app.py`，通过侧边栏选择页面。

### 方式2: 多页面应用（推荐）
使用 `pages/` 目录，Streamlit自动创建多页面导航。

**运行**:
```bash
streamlit run streamlit_app.py
# 或直接运行pages目录下的文件
streamlit run pages/1_板块仪表盘.py
```

## 📝 代码组织原则

1. **组件化**: UI组件放在 `components/`
2. **工具化**: 工具函数放在 `utils/`
3. **配置化**: 配置信息放在 `config/`
4. **模块化**: 功能模块放在 `pages/` 或 `api/`
5. **服务化**: 业务逻辑放在 `services/`
6. **模型化**: 数据模型放在 `models/`

## 🚀 快速开始

1. **查看可视化文档**: `README_VISUALIZATION.md`
2. **查看设计文档**: `docs/CHART_DASHBOARD_DESIGN.md`
3. **查看示例代码**: `docs/CHART_IMPLEMENTATION_EXAMPLES.md`
4. **运行应用**: `streamlit run streamlit_app.py`

