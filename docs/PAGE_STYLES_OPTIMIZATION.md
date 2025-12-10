# 页面样式优化说明

## 概述

本次优化统一了所有Streamlit页面的样式代码，创建了统一的样式工具模块，提高了代码的可维护性和一致性。

## 优化内容

### 1. 创建统一样式工具模块

**文件**: `utils/page_styles.py`

提供了以下功能：
- `get_common_styles()`: 获取通用样式CSS
- `get_metric_delta_script()`: 获取涨跌幅颜色动态设置脚本
- `apply_common_styles(additional_styles="")`: 应用通用样式到当前页面
- `get_dashboard_specific_styles()`: 获取仪表盘页面特定样式
- `get_calendar_specific_styles()`: 获取复盘日历页面特定样式
- `get_scheduler_specific_styles()`: 获取定时任务管理页面特定样式

### 2. 统一样式规范

#### 主标题样式 (`.main-header`)
- 字体大小: `1.5rem`
- 字体粗细: `700` (bold)
- 颜色: `#1f77b4`
- 底部边框: `3px solid #1f77b4`

#### 章节标题样式 (`.section-header`)
- 字体大小: `1.1rem`
- 字体粗细: `600`
- 颜色: `#2c3e50`
- 底部边框: `2px solid #e0e0e0`

#### 组件样式优化
- Metric卡片: 渐变背景，圆角，阴影
- 按钮: 圆角，悬停效果，过渡动画
- 输入框: 圆角，聚焦效果
- 表格: 优化的边框和悬停效果
- 涨跌幅颜色: 上涨红色 `#dc2626`，下跌绿色 `#059669`

### 3. 页面更新情况

所有13个页面已更新为使用统一样式工具：

| 页面 | 样式类型 | 状态 |
|------|---------|------|
| 0_实时仪表盘.py | 通用 + 仪表盘特定 | ✅ |
| 1_历史仪表盘.py | 通用 + 仪表盘特定 | ✅ |
| 2_指数信息.py | 通用 | ✅ |
| 3_板块仪表盘.py | 通用 | ✅ |
| 4_涨停股票池.py | 通用 | ✅ |
| 5_跌停股票池.py | 通用 | ✅ |
| 6_炸板股票池.py | 通用 | ✅ |
| 7_交易日志.py | 通用 | ✅ |
| 8_个股表现.py | 通用 | ✅ |
| 9_复盘日历.py | 通用 + 日历特定 | ✅ |
| 10_关注管理.py | 通用 | ✅ |
| 11_定时任务管理.py | 通用 + 定时任务特定 | ✅ |
| 12_个股资金.py | 通用 | ✅ |

## 使用方式

### 基础使用（大多数页面）

```python
from utils.page_styles import apply_common_styles
apply_common_styles()
```

### 带特定样式（仪表盘页面）

```python
from utils.page_styles import apply_common_styles, get_dashboard_specific_styles
apply_common_styles(additional_styles=get_dashboard_specific_styles())
```

### 带特定样式（日历页面）

```python
from utils.page_styles import apply_common_styles, get_calendar_specific_styles
apply_common_styles(additional_styles=get_calendar_specific_styles())
```

### 带特定样式（定时任务管理页面）

```python
from utils.page_styles import apply_common_styles, get_scheduler_specific_styles
apply_common_styles(additional_styles=get_scheduler_specific_styles())
```

## 优势

1. **代码复用**: 消除了重复的样式定义，减少代码量
2. **易于维护**: 样式修改只需在一个地方进行
3. **一致性**: 确保所有页面使用相同的样式规范
4. **可扩展性**: 支持页面特定样式的扩展
5. **响应式设计**: 包含移动端适配的响应式样式

## 响应式设计

样式工具包含了响应式设计支持：
- 移动端（宽度 < 768px）自动调整字体大小
- 主标题: `1.5rem` → `1.2rem`
- 章节标题: `1.1rem` → `1rem`

## 注意事项

1. 所有样式都使用 `!important` 确保优先级
2. 涨跌幅颜色通过CSS和JavaScript双重设置，确保颜色正确显示
3. 特定页面样式会与通用样式合并，不会冲突

## 未来改进

1. 可以考虑添加暗色主题支持
2. 可以添加更多页面特定样式函数
3. 可以优化CSS选择器性能

