# 数据表格分页功能使用指南

## 概述

在Streamlit中显示大量数据时，使用分页功能可以提升用户体验，避免一次性加载过多数据导致页面卡顿。

## 功能特点

✅ **完全可行** - 在Streamlit中实现数据表格翻页效果是完全可行的  
✅ **易于使用** - 提供简单的API，只需几行代码即可集成  
✅ **灵活配置** - 支持自定义每页显示行数  
✅ **用户友好** - 提供首页、上一页、下一页、末页按钮和页码输入框  
✅ **状态保持** - 使用session_state保持分页状态  

## 使用方法

### 基础用法

```python
from utils.pagination import paginate_dataframe

# 对DataFrame进行分页（默认每页50行）
df_paginated = paginate_dataframe(df, page_size=50, key_prefix="my_data")

# 显示分页后的数据
st.dataframe(df_paginated, use_container_width=True)
```

### 带页面大小选择器

```python
from utils.pagination import paginate_dataframe_with_size_selector

# 分页显示，用户可以选择每页显示的行数
df_paginated, page_size = paginate_dataframe_with_size_selector(
    df,
    default_page_size=50,
    page_size_options=[20, 50, 100, 200, 500],
    key_prefix="my_data",
    show_info=True
)

# 显示分页后的数据
st.dataframe(df_paginated, use_container_width=True)
```

## 参数说明

### `paginate_dataframe`

- `df`: 要分页的DataFrame
- `page_size`: 每页显示的行数，默认50
- `key_prefix`: 用于session_state的唯一前缀（避免不同分页组件冲突）
- `show_info`: 是否显示分页信息（当前页/总页数等），默认True

### `paginate_dataframe_with_size_selector`

- `df`: 要分页的DataFrame
- `default_page_size`: 默认每页显示的行数，默认50
- `page_size_options`: 可选的页面大小选项列表，默认[20, 50, 100, 200, 500]
- `key_prefix`: 用于session_state的唯一前缀
- `show_info`: 是否显示分页信息，默认True

## 功能特性

### 1. 分页控件

- **首页按钮** (◀◀): 跳转到第一页
- **上一页按钮** (◀): 跳转到上一页
- **页码输入框**: 直接输入页码跳转
- **下一页按钮** (▶): 跳转到下一页
- **末页按钮** (▶▶): 跳转到最后一页

### 2. 数据统计

显示当前页的数据范围，例如：
- "📊 显示第 1 - 50 行，共 1234 行数据"

### 3. 页面大小选择

用户可以选择每页显示的行数：
- 20行
- 50行（默认）
- 100行
- 200行
- 500行

## 已应用页面

✅ **个股资金页面** (`pages/12_个股资金.py`) - 已集成分页功能

## 在其他页面中应用

### 示例：涨停股票池页面

```python
from utils.pagination import paginate_dataframe_with_size_selector

# 在显示完整数据时使用分页
df_paginated, _ = paginate_dataframe_with_size_selector(
    df_display,
    default_page_size=50,
    key_prefix="zt_stock_pool"
)

st.dataframe(df_paginated, use_container_width=True)
```

### 示例：板块仪表盘页面

```python
from utils.pagination import paginate_dataframe

# 简单分页，固定每页100行
df_paginated = paginate_dataframe(
    df_display,
    page_size=100,
    key_prefix="sector_dashboard"
)

st.dataframe(df_paginated, use_container_width=True, height=400)
```

## 注意事项

1. **key_prefix唯一性**: 确保每个分页组件使用不同的`key_prefix`，避免状态冲突
2. **数据格式化**: 分页应在数据格式化之后进行，确保显示的是格式化后的数据
3. **导出功能**: 导出功能应使用原始数据（未分页的完整DataFrame），而不是分页后的数据
4. **性能考虑**: 对于非常大的数据集（>10万行），建议先进行筛选或聚合，再使用分页

## 技术实现

- 使用`st.session_state`保存当前页码
- 使用`st.rerun()`实现页面刷新和状态更新
- 使用`DataFrame.iloc`进行数据切片

## 优势

1. **提升性能**: 只渲染当前页的数据，减少DOM元素
2. **改善体验**: 用户可以快速浏览和定位数据
3. **灵活配置**: 支持自定义每页显示行数
4. **易于集成**: 只需几行代码即可应用

## 未来改进

- [ ] 支持跳转到指定行号
- [ ] 支持URL参数同步页码（通过query_params）
- [ ] 支持键盘快捷键（左右箭头翻页）
- [ ] 支持记住用户的页面大小偏好

