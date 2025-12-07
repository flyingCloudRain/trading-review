# 定时任务配置文档

## 📋 定时任务总览

### 当前配置的定时任务

| 任务ID | 任务名称 | 执行时间 | 时区 | 状态 |
|--------|---------|---------|------|------|
| `save_daily_data` | 每日15:10保存板块和股票池数据 | 每日 15:10 | UTC+8 (北京时间) | ✅ 已配置 |

---

## 🔍 详细任务说明

### 1. save_daily_data - 每日数据保存任务

**任务ID**: `save_daily_data`  
**任务名称**: 每日15:10保存板块和股票池数据  
**执行时间**: 每日 15:10（北京时间）  
**时区**: UTC+8 (北京时间)  
**触发规则**: `cron[hour='15', minute='10']`

#### 执行内容

1. **保存板块数据**
   - 从 API 获取当日板块数据
   - 保存到数据库 `sector_history` 表
   - 追加到 Excel 文件 `data/板块信息历史.xlsx`

2. **保存涨停股票池数据**
   - 从 API 获取当日涨停股票数据
   - 保存到数据库 `zt_pool_history` 表

3. **保存炸板股票池数据**
   - 从 API 获取当日炸板股票数据
   - 保存到数据库 `zbgc_pool_history` 表

4. **保存跌停股票池数据**
   - 从 API 获取当日跌停股票数据
   - 保存到数据库 `dtgc_pool_history` 表

5. **保存指数数据**
   - 从 API 获取当日指数数据
   - 保存到数据库 `index_history` 表

#### 交易日检查

- ✅ 自动检查是否为交易日
- ✅ 非交易日自动跳过执行
- ✅ 使用 `ak.tool_trade_date_hist_sina()` 获取交易日历

#### 错误处理

- ✅ 每个数据源独立处理，单个失败不影响其他
- ✅ 详细的错误日志记录
- ✅ 异常不会中断整个任务

---

## 📁 相关文件

### 核心文件

1. **`tasks/sector_scheduler.py`**
   - 定时任务调度器类
   - 任务配置和执行逻辑
   - 交易日检查功能

2. **`run_scheduler_task.py`**
   - 手动执行定时任务的脚本
   - 支持 `--force` 参数跳过交易日检查
   - 命令行工具

3. **`pages/8_定时任务管理.py`**
   - Streamlit 定时任务管理页面
   - 查看任务状态
   - 手动执行任务
   - 查看执行历史

4. **`app.py`**
   - Flask 应用入口
   - 自动启动定时任务调度器（非测试环境）

### 依赖服务

- `services/sector_history_service.py` - 板块数据服务
- `services/zt_pool_history_service.py` - 涨停股票池服务
- `services/zbgc_pool_history_service.py` - 炸板股票池服务
- `services/dtgc_pool_history_service.py` - 跌停股票池服务
- `services/index_history_service.py` - 指数数据服务

---

## 🚀 使用方式

### 方式 1: 自动执行（推荐）

定时任务会在 Flask 应用启动时自动启动，每日 15:10 自动执行。

**启动 Flask 应用**：
```bash
python3 app.py
```

### 方式 2: 手动执行

**正常执行**（检查交易日）：
```bash
python3 run_scheduler_task.py
```

**强制执行**（跳过交易日检查）：
```bash
python3 run_scheduler_task.py --force
```

### 方式 3: 通过 Streamlit 管理页面

1. 访问 Streamlit 应用
2. 进入「定时任务管理」页面
3. 查看任务状态
4. 点击「立即执行」手动触发任务

---

## ⚙️ 配置说明

### 调度器配置

- **调度器类型**: `BackgroundScheduler`
- **时区**: UTC+8 (北京时间)
- **任务存储**: 内存存储 (`memory`)
- **任务替换**: 支持 (`replace_existing=True`)

### 任务触发配置

```python
CronTrigger(
    hour=15,      # 15点
    minute=10,    # 10分
    timezone=UTC8 # UTC+8时区
)
```

### 修改执行时间

如需修改执行时间，编辑 `tasks/sector_scheduler.py`：

```python
self.scheduler.add_job(
    func=self.save_daily_data,
    trigger=CronTrigger(hour=15, minute=10, timezone=UTC8),  # 修改这里
    id='save_daily_data',
    name='每日15:10保存板块和股票池数据',
    replace_existing=True
)
```

---

## 🔍 检查定时任务

### 使用检查脚本

```bash
python3 scripts/check_scheduler.py
```

### 检查内容

- ✅ 调度器文件是否存在
- ✅ 调度器类是否可以正常实例化
- ✅ 已配置的任务列表
- ✅ 任务触发规则
- ✅ 调度器运行状态
- ✅ 依赖是否安装

---

## 📊 任务执行流程

```
1. 调度器触发任务 (15:10)
   ↓
2. 检查是否为交易日
   ├─ 是交易日 → 继续执行
   └─ 非交易日 → 跳过执行
   ↓
3. 获取数据库会话
   ↓
4. 并行执行数据保存：
   ├─ 保存板块数据
   ├─ 保存涨停股票池
   ├─ 保存炸板股票池
   ├─ 保存跌停股票池
   └─ 保存指数数据
   ↓
5. 记录执行结果
   ↓
6. 关闭数据库会话
   ↓
7. 任务完成
```

---

## 🛠️ 故障排查

### 问题 1: 任务未执行

**检查**：
1. 调度器是否启动（Flask 应用是否运行）
2. 是否为交易日
3. 查看日志文件

**解决**：
- 确保 Flask 应用正在运行
- 或手动执行任务：`python3 run_scheduler_task.py --force`

### 问题 2: 任务执行失败

**检查**：
1. 查看执行日志
2. 检查数据库连接
3. 检查 API 是否可用

**解决**：
- 查看 Streamlit「定时任务管理」页面的执行历史
- 检查错误信息
- 手动执行任务查看详细错误

### 问题 3: 调度器未启动

**检查**：
1. Flask 应用是否运行
2. 是否在测试环境（测试环境不会启动调度器）

**解决**：
- 启动 Flask 应用：`python3 app.py`
- 或在 Streamlit「定时任务管理」页面手动启动

---

## 📝 日志记录

定时任务会记录以下日志：

- ✅ 任务开始执行
- ✅ 每个数据源的保存结果
- ✅ 任务执行完成
- ❌ 执行失败的错误信息
- ⚠️ 非交易日跳过执行

日志格式：
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

---

## 🔄 添加新任务

如需添加新的定时任务：

1. **在 `tasks/sector_scheduler.py` 中添加任务方法**：
```python
def new_task(self):
    """新任务"""
    logger.info("执行新任务...")
    # 任务逻辑
    logger.info("新任务完成")
```

2. **在 `_setup_jobs()` 中注册任务**：
```python
self.scheduler.add_job(
    func=self.new_task,
    trigger=CronTrigger(hour=16, minute=0, timezone=UTC8),
    id='new_task',
    name='新任务名称',
    replace_existing=True
)
```

---

## 📚 相关文档

- [定时任务管理页面](../pages/8_定时任务管理.py)
- [手动执行脚本](../run_scheduler_task.py)
- [调度器实现](../tasks/sector_scheduler.py)
- [README - 定时任务](../README_SCHEDULER.md)

---

**最后更新**: 2025-12-07

