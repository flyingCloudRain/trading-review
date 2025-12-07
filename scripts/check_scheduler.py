#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有定时任务配置和状态
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_scheduler_config():
    """检查定时任务配置"""
    print("=" * 80)
    print("🔍 检查定时任务配置")
    print("=" * 80)
    print()
    
    # 1. 检查调度器文件
    print("📋 1. 检查调度器文件...")
    scheduler_file = project_root / "tasks" / "sector_scheduler.py"
    if scheduler_file.exists():
        print(f"   ✅ 调度器文件存在: {scheduler_file}")
    else:
        print(f"   ❌ 调度器文件不存在: {scheduler_file}")
        return False
    
    print()
    
    # 2. 检查调度器类
    print("📋 2. 检查调度器类...")
    try:
        from tasks.sector_scheduler import SectorScheduler, get_scheduler
        
        scheduler = SectorScheduler()
        print("   ✅ 调度器类可以正常实例化")
        
        # 检查任务配置
        jobs = scheduler.scheduler.get_jobs()
        print(f"   ✅ 已配置 {len(jobs)} 个定时任务")
        
        if len(jobs) == 0:
            print("   ⚠️  警告：没有配置任何定时任务")
        else:
            print()
            print("   📝 定时任务详情：")
            for i, job in enumerate(jobs, 1):
                print(f"      {i}. 任务ID: {job.id}")
                print(f"         任务名称: {job.name}")
                print(f"         触发规则: {job.trigger}")
                
                # 获取下次执行时间
                try:
                    next_run = job.next_run_time
                    if next_run:
                        print(f"         下次执行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        print(f"         下次执行: 未安排")
                except:
                    print(f"         下次执行: 无法获取")
                print()
        
    except Exception as e:
        print(f"   ❌ 检查调度器类失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # 3. 检查调度器状态
    print("📋 3. 检查调度器状态...")
    try:
        scheduler = get_scheduler()
        is_running = scheduler.scheduler.running
        print(f"   ✅ 调度器状态: {'🟢 运行中' if is_running else '🔴 已停止'}")
        print(f"   ✅ 任务数量: {len(scheduler.scheduler.get_jobs())}")
    except Exception as e:
        print(f"   ⚠️  无法检查调度器状态: {str(e)}")
        print("   💡 提示：调度器可能需要在 Flask 应用中启动")
    
    print()
    
    # 4. 检查手动执行脚本
    print("📋 4. 检查手动执行脚本...")
    run_script = project_root / "run_scheduler_task.py"
    if run_script.exists():
        print(f"   ✅ 手动执行脚本存在: {run_script}")
    else:
        print(f"   ⚠️  手动执行脚本不存在: {run_script}")
    
    print()
    
    # 5. 检查定时任务管理页面
    print("📋 5. 检查定时任务管理页面...")
    manage_page = project_root / "pages" / "8_定时任务管理.py"
    if manage_page.exists():
        print(f"   ✅ 定时任务管理页面存在: {manage_page}")
    else:
        print(f"   ⚠️  定时任务管理页面不存在: {manage_page}")
    
    print()
    
    # 6. 检查依赖
    print("📋 6. 检查依赖...")
    try:
        import apscheduler
        print(f"   ✅ apscheduler 已安装: {apscheduler.__version__}")
    except ImportError:
        print(f"   ❌ apscheduler 未安装")
        return False
    
    print()
    
    # 7. 总结
    print("=" * 80)
    print("📊 检查结果总结")
    print("=" * 80)
    print()
    print("✅ 定时任务配置检查完成")
    print()
    print("📝 定时任务列表：")
    try:
        scheduler = SectorScheduler()
        jobs = scheduler.scheduler.get_jobs()
        for job in jobs:
            print(f"   - {job.name} (ID: {job.id})")
            print(f"     触发规则: {job.trigger}")
            try:
                next_run = job.next_run_time
                if next_run:
                    print(f"     下次执行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                pass
            print()
    except Exception as e:
        print(f"   ⚠️  无法获取任务列表: {str(e)}")
    
    print()
    print("💡 使用提示：")
    print("   - 手动执行任务: python3 run_scheduler_task.py")
    print("   - 强制执行任务: python3 run_scheduler_task.py --force")
    print("   - 查看任务管理: 访问 Streamlit 应用中的「定时任务管理」页面")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = check_scheduler_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

