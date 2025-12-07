# Streamlit可视化应用使用指南

## 功能概述

基于Streamlit的数据可视化应用，支持以下功能：
- 📊 板块信息可视化
- 📈 涨停股票可视化
- 💥 炸板股票可视化
- 📉 跌停股票可视化
- 🔔 板块异动可视化
- 📝 交易复盘可视化

## 安装依赖

```bash
pip install streamlit plotly
```

或使用requirements.txt：
```bash
pip install -r requirements.txt
```

## 启动应用

```bash
streamlit run streamlit_app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

## 功能说明

### 1. 板块信息可视化
- 涨跌幅TOP 10（柱状图）
- 涨跌幅BOTTOM 10（柱状图）
- 涨跌幅分布（直方图）
- 数据来源：数据库或Excel文件

### 2. 涨停股票可视化
- 连板数分布（饼图）
- 行业分布（柱状图）
- 成交额TOP 10（柱状图）
- 数据来源：Excel文件

### 3. 炸板股票可视化
- 炸板次数分布（柱状图）
- 数据来源：Excel文件

### 4. 跌停股票可视化
- 连续跌停分布（柱状图）
- 数据来源：Excel文件

### 5. 板块异动可视化
- 板块异动总次数TOP 20（柱状图）
- 数据来源：Excel文件

### 6. 交易复盘可视化
- 盈亏分布（直方图）
- 统计信息（总记录数、总盈亏、胜率等）
- 数据来源：SQLite数据库

## 图表类型

- **柱状图** - 用于排名、分布
- **饼图** - 用于占比分析
- **直方图** - 用于分布分析
- **数据表格** - 完整数据展示

## 自定义配置

### 修改端口
```bash
streamlit run streamlit_app.py --server.port 8502
```

### 修改主题
在 `~/.streamlit/config.toml` 中配置：
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
```

## 注意事项

1. 确保Excel文件已生成（运行相应的导出脚本）
2. 数据库需要先初始化（运行应用会自动创建）
3. 图表数据基于最新日期的数据
4. 所有时间使用UTC+8时区

## 扩展功能

可以添加更多可视化：
- 时间序列图表（板块涨跌幅趋势）
- 热力图（板块涨跌幅热力图）
- K线图（股票价格走势）
- 仪表盘（实时数据展示）

