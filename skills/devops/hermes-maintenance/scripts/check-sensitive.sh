#!/bin/bash
# 敏感词检查脚本 - 在 git commit/push 前运行
# 用法: bash check-sensitive.sh [目录]

set -e

REPO_DIR="${1:-.}"
cd "$REPO_DIR"

echo "🔍 检查敏感信息..."
echo "仓库目录: $(pwd)"
echo ""

FOUND=0
FILES_TO_CHECK=$(git ls-files '*.md' '*.json' '*.yaml' '*.yml' '*.py' '*.js' '*.sh' 2>/dev/null || find . -type f \( -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.py" -o -name "*.js" -o -name "*.sh" \) -not -path "./.git/*")

# 检查函数
check_pattern() {
    local name="$1"
    local pattern="$2"
    local example_pattern="${3:-}"  # 示例模式（如果文件只包含示例，则排除）
    
    local matches=$(echo "$FILES_TO_CHECK" | xargs grep -l "$pattern" 2>/dev/null || true)
    
    if [ -n "$matches" ]; then
        local has_real_match=0
        echo "$matches" | while read -r file; do
            # 如果有示例模式，检查文件是否只包含示例
            if [ -n "$example_pattern" ]; then
                # 检查是否有非示例的匹配
                real_matches=$(grep "$pattern" "$file" 2>/dev/null | grep -v "$example_pattern" || true)
                if [ -z "$real_matches" ]; then
                    continue  # 跳过只有示例的文件
                fi
            fi
            
            if [ $has_real_match -eq 0 ]; then
                echo "❌ 发现 $name:"
                has_real_match=1
            fi
            echo "   - $file"
            grep -n "$pattern" "$file" 2>/dev/null | grep -v "$example_pattern" | head -3 | while read -r line; do
                echo "     $line"
            done
        done
        
        # 检查是否有真实的匹配
        if [ -n "$example_pattern" ]; then
            real_count=$(echo "$matches" | xargs grep "$pattern" 2>/dev/null | grep -v "$example_pattern" | wc -l || echo "0")
        else
            real_count=$(echo "$matches" | xargs grep "$pattern" 2>/dev/null | wc -l || echo "0")
        fi
        
        if [ "$real_count" -gt 0 ]; then
            echo ""
            FOUND=$((FOUND + 1))
        fi
    fi
}

# API Key / Token（排除示例格式）
check_pattern "GitHub Token" "ghp_[A-Za-z0-9]\{36\}" "ghp_xx"
check_pattern "OpenAI Key" "sk-[A-Za-z0-9]\{20,\}" "sk-XXX"
check_pattern "AnySearch Key" "as_sk_[A-Za-z0-9]\{20,\}" "as_sk_xxx"
check_pattern "Token Plan" "tp-[A-Za-z0-9]\{20,\}" "tp-xxx"

# 邮箱
check_pattern "Z-Library 主号邮箱" "libing19950105@gmail.com"
check_pattern "Z-Library 备用邮箱" "541812906@qq.com"

# 密码 / 凭证
check_pattern "通用密码" "1472291855"
check_pattern "QQ号/用户名" "541812906"

# 组合模式
check_pattern "SMB凭证" "541812906%1472291855"

# 检查仓库可见性
if command -v gh &> /dev/null; then
    REPO_INFO=$(gh repo view --json isPrivate,visibility 2>/dev/null || echo "")
    if [ -n "$REPO_INFO" ]; then
        IS_PRIVATE=$(echo "$REPO_INFO" | grep -o '"isPrivate":[^,}]*' | cut -d: -f2)
        VISIBILITY=$(echo "$REPO_INFO" | grep -o '"visibility":"[^"]*"' | cut -d: -f2 | tr -d '"')
        
        if [ "$IS_PRIVATE" = "false" ]; then
            echo "⚠️  仓库是公开的 ($VISIBILITY) - 泄露风险更高！"
            echo ""
        fi
    fi
fi

# 总结
if [ $FOUND -eq 0 ]; then
    echo "✅ 未发现敏感信息，可以安全提交/推送"
    exit 0
else
    echo "❌ 发现 $FOUND 类敏感信息，请先清理后再提交/推送"
    echo ""
    echo "清理方法:"
    echo "  1. 用 [REDACTED] 替换敏感信息"
    echo "  2. 如果已在 git 历史中，用 git filter-branch 清理"
    echo "  3. 参考: hermes-maintenance 技能的 sensitive-info-cleanup.md"
    exit 1
fi
