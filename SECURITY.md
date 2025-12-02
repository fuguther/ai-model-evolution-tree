# 🔒 安全指南

## 密钥安全检查清单

在将代码推送到 GitHub 之前，请务必完成以下检查：

### ✅ 1. 环境变量文件检查

- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 所有 `.env` 文件都被 Git 忽略（运行 `git check-ignore .env` 确认）
- [ ] 没有将 `.env` 文件添加到 Git 跟踪中

### ✅ 2. 代码检查

- [ ] 代码中没有硬编码的 API 密钥
- [ ] 所有密钥都通过环境变量读取（`os.getenv()`）
- [ ] 没有在注释中留下真实的密钥

### ✅ 3. 文件检查

运行以下命令检查是否有敏感文件：

```bash
# 检查 .env 文件是否被忽略
git check-ignore .env 模型生长树代码/.env 模型生长树代码/pipeline/.env

# 检查是否有硬编码的密钥（查找常见的密钥格式）
grep -r "sk-[a-zA-Z0-9]\{32,\}" --exclude-dir=venv --exclude-dir=node_modules .

# 检查是否有其他敏感文件
find . -name "*secret*" -o -name "*key*" -o -name "*password*" | grep -v node_modules | grep -v venv
```

### ✅ 4. Git 历史检查

如果之前已经提交过敏感信息，需要清理 Git 历史：

```bash
# 检查 Git 历史中是否有敏感信息
git log --all --full-history --source -- "*secret*" "*key*" "*.env"

# 如果发现敏感信息，需要使用 git filter-branch 或 BFG Repo-Cleaner 清理
```

### ✅ 5. 提交前最终检查

```bash
# 查看将要提交的文件
git status

# 确认没有敏感文件
git diff --cached --name-only | grep -E "\.env|secret|key|password"
```

## 🚨 如果发现密钥泄漏

如果发现密钥已经被提交到 Git：

1. **立即撤销提交**（如果还没有推送）：
   ```bash
   git reset HEAD~1  # 撤销最后一次提交
   ```

2. **如果已经推送到 GitHub**：
   - 立即在 GitHub 上删除该仓库
   - 或使用 `git filter-branch` 清理历史
   - **立即更换所有泄漏的 API 密钥**

3. **使用 GitHub 的密钥扫描功能**：
   - GitHub 会自动扫描提交中的密钥
   - 如果检测到，会发送通知

## 📋 最佳实践

1. **使用环境变量**：永远不要在代码中硬编码密钥
2. **使用 .gitignore**：确保所有敏感文件都被忽略
3. **使用模板文件**：提供 `env.example` 作为配置模板
4. **定期检查**：定期运行安全检查命令
5. **使用密钥管理工具**：考虑使用密钥管理服务（如 AWS Secrets Manager）

## 🔍 自动检查脚本

可以创建一个简单的检查脚本：

```bash
#!/bin/bash
# security_check.sh

echo "🔍 开始安全检查..."

# 检查 .env 文件
if git ls-files | grep -q "\.env$"; then
    echo "❌ 错误：发现 .env 文件被 Git 跟踪！"
    exit 1
fi

# 检查硬编码密钥
if grep -r "sk-[a-zA-Z0-9]\{32,\}" --exclude-dir=venv --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null; then
    echo "❌ 警告：发现可能的硬编码密钥！"
    exit 1
fi

echo "✅ 安全检查通过！"
```

