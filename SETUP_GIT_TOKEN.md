# GitHub Personal Access Token 设置指南

## 步骤1：创建 GitHub Personal Access Token

1. 访问 GitHub Token 创建页面：
   ```
   https://github.com/settings/tokens/new
   ```

2. 填写 Token 信息：
   - **Note（备注）**: `trading-review-auto-push` 或任意描述
   - **Expiration（过期时间）**: 建议选择 90 days 或根据需要选择
   - **Select scopes（权限范围）**: 
     - ✅ 勾选 `repo`（完整仓库访问权限）
       - 这会自动包含所有子权限（repo:status, repo_deployment, public_repo, repo:invite, security_events）

3. 点击 **"Generate token"** 按钮

4. **重要**：立即复制生成的 Token（格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
   - ⚠️ 注意：Token 只显示一次，请妥善保存

## 步骤2：配置 Token（三种方式）

### 方式1：使用 Git Credential Store（推荐，安全）

```bash
# 1. 配置 credential helper
git config --global credential.helper store

# 2. 首次推送时输入用户名和token
git push origin main
# Username: flyingCloudRain
# Password: <粘贴你的token>
```

之后 Git 会自动保存凭据到 `~/.git-credentials`，后续推送无需再输入。

### 方式2：直接在 Remote URL 中包含 Token（简单但不安全）

```bash
# 替换 YOUR_TOKEN 为你的实际token
git remote set-url origin https://YOUR_TOKEN@github.com/flyingCloudRain/trading-review.git

# 然后推送
git push origin main
```

⚠️ **注意**：这种方式会将 token 保存在 `.git/config` 中，如果仓库是公开的，token 可能会泄露。

### 方式3：使用环境变量（适合CI/CD）

```bash
# 设置环境变量
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# 使用token推送
git push https://$GITHUB_TOKEN@github.com/flyingCloudRain/trading-review.git main
```

## 步骤3：验证配置

```bash
# 测试推送
git push origin main

# 如果成功，会看到类似输出：
# Enumerating objects: X, done.
# Counting objects: 100% (X/X), done.
# ...
# To https://github.com/flyingCloudRain/trading-review.git
#    xxxxx..xxxxx  main -> main
```

## 安全建议

1. **不要将 token 提交到代码仓库**
   - 确保 `.git-credentials` 在 `.gitignore` 中（如果使用方式1）
   - 不要将包含 token 的配置文件提交到仓库

2. **定期更新 token**
   - 建议每 90 天更新一次
   - 如果 token 泄露，立即在 GitHub 设置中撤销

3. **使用最小权限原则**
   - 只授予必要的权限（repo 权限）

4. **使用 SSH 密钥（更安全的选择）**
   - 如果可能，建议配置 SSH 密钥替代 token
   - SSH 密钥更安全且无需定期更新

## 故障排除

### 问题1：推送时提示 "Authentication failed"
- 检查 token 是否正确复制（没有多余空格）
- 确认 token 未过期
- 确认 token 有 `repo` 权限

### 问题2：提示 "could not read Username"
- 尝试使用方式2，直接在 URL 中包含 token
- 或检查 credential helper 配置

### 问题3：Token 泄露怎么办
1. 立即访问：https://github.com/settings/tokens
2. 找到对应的 token，点击 "Revoke" 撤销
3. 创建新的 token 并重新配置

## 相关链接

- GitHub Token 管理：https://github.com/settings/tokens
- Git Credential 文档：https://git-scm.com/docs/git-credential
- SSH 密钥设置：https://docs.github.com/en/authentication/connecting-to-github-with-ssh

