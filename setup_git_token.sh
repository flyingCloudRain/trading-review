#!/bin/bash
# GitHub Token 快速配置脚本

echo "=========================================="
echo "GitHub Personal Access Token 配置助手"
echo "=========================================="
echo ""

# 检查是否已配置credential helper
if git config --global --get credential.helper > /dev/null 2>&1; then
    echo "✅ Git credential helper 已配置"
else
    echo "📝 配置 Git credential helper..."
    git config --global credential.helper store
    echo "✅ 配置完成"
fi

echo ""
echo "=========================================="
echo "下一步操作："
echo "=========================================="
echo ""
echo "1. 创建 GitHub Token："
echo "   访问: https://github.com/settings/tokens/new"
echo "   - Note: trading-review-auto-push"
echo "   - Expiration: 90 days"
echo "   - Scopes: 勾选 'repo'"
echo ""
echo "2. 复制生成的 Token（格式: ghp_xxxxxxxxxxxxx）"
echo ""
echo "3. 执行推送命令："
echo "   git push origin main"
echo ""
echo "4. 当提示输入用户名时，输入: flyingCloudRain"
echo "5. 当提示输入密码时，粘贴你的 Token"
echo ""
echo "之后 Git 会自动保存凭据，后续推送无需再输入。"
echo ""
echo "=========================================="
echo "或者，如果你已经有 Token，可以直接运行："
echo "=========================================="
echo ""
echo "git remote set-url origin https://YOUR_TOKEN@github.com/flyingCloudRain/trading-review.git"
echo "git push origin main"
echo ""
echo "注意：请将 YOUR_TOKEN 替换为你的实际 Token"
echo ""

