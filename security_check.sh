#!/bin/bash
# 🔒 密钥安全检查脚本
# 在提交代码到 GitHub 之前运行此脚本

echo "🔍 开始安全检查..."
echo ""

ERRORS=0

# 1. 检查 .env 文件是否被 Git 跟踪
echo "1️⃣ 检查 .env 文件..."
if git ls-files | grep -q "\.env$"; then
    echo "   ❌ 错误：发现 .env 文件被 Git 跟踪！"
    echo "   请从 Git 中移除：git rm --cached .env"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ .env 文件未被 Git 跟踪"
fi

# 2. 检查是否有硬编码的密钥（排除 .env 文件，因为它们已被忽略）
echo ""
echo "2️⃣ 检查硬编码的 API 密钥（排除 .env 文件）..."
if grep -r "sk-[a-zA-Z0-9]\{32,\}" \
    --exclude-dir=venv \
    --exclude-dir=node_modules \
    --exclude-dir=.git \
    --exclude="security_check.sh" \
    --exclude="*.md" \
    --exclude=".env" \
    --exclude="*.env" \
    . 2>/dev/null | grep -v "env.example" | grep -v "\.gitignore" | grep -v "SECURITY.md"; then
    echo "   ❌ 警告：发现可能的硬编码密钥！"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ 未发现硬编码的密钥（.env 文件中的密钥是安全的，因为它们已被忽略）"
fi

# 3. 检查环境变量文件是否被忽略
echo ""
echo "3️⃣ 验证 .gitignore 配置..."
if git check-ignore .env 模型生长树代码/.env 模型生长树代码/pipeline/.env >/dev/null 2>&1; then
    echo "   ✅ .env 文件已被正确忽略"
else
    echo "   ⚠️  警告：某些 .env 文件可能未被忽略"
fi

# 4. 检查是否有其他敏感文件
echo ""
echo "4️⃣ 检查其他敏感文件..."
SENSITIVE_FILES=$(find . -type f \( -name "*secret*" -o -name "*password*" -o -name "*credential*" \) \
    -not -path "*/venv/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -name "*.md" \
    -not -name "security_check.sh" 2>/dev/null)

if [ -n "$SENSITIVE_FILES" ]; then
    echo "   ⚠️  发现可能的敏感文件："
    echo "$SENSITIVE_FILES" | sed 's/^/      /'
    echo "   请确认这些文件不包含敏感信息"
else
    echo "   ✅ 未发现其他敏感文件"
fi

# 5. 检查将要提交的文件
echo ""
echo "5️⃣ 检查暂存区的文件..."
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null)
if [ -n "$STAGED_FILES" ]; then
    SENSITIVE_STAGED=$(echo "$STAGED_FILES" | grep -E "\.env|secret|key|password|credential")
    if [ -n "$SENSITIVE_STAGED" ]; then
        echo "   ❌ 错误：暂存区包含敏感文件！"
        echo "$SENSITIVE_STAGED" | sed 's/^/      /'
        ERRORS=$((ERRORS + 1))
    else
        echo "   ✅ 暂存区文件检查通过"
    fi
else
    echo "   ℹ️  暂存区为空（使用 git add 添加文件后再次检查）"
fi

# 总结
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo "✅ 安全检查通过！可以安全地提交代码。"
    exit 0
else
    echo "❌ 发现 $ERRORS 个安全问题，请修复后再提交！"
    exit 1
fi

