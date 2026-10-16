# -*- coding: utf-8 -*-
"""qushiyanguan skill 快速校验脚本。
检查项：
1. SKILL.md frontmatter 含 name/description
2. references/methodology.md 与 corrections.md 存在且非空
3. SKILL.md 中规则均标注出处 aweme_id@MM:SS
4. 没有硬编码历史点位（如 3900/4000/4100 这种历史指数点位）
5. 文件 UTF-8 编码
用法: python quick_validate.py
"""
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
errors = []
warnings = []

# 1. SKILL.md 存在且 frontmatter 完整
skill_md = SKILL_DIR / "SKILL.md"
if not skill_md.exists():
    errors.append("SKILL.md 不存在")
else:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append("SKILL.md 缺少 frontmatter 开头 ---")
    else:
        fm_end = text.find("---", 3)
        fm = text[3:fm_end]
        if "name:" not in fm:
            errors.append("frontmatter 缺少 name 字段")
        if "description:" not in fm:
            errors.append("frontmatter 缺少 description 字段")
        if "qushiyanguan" not in fm:
            errors.append("frontmatter name 应为 qushiyanguan")

# 2. references 文件存在
for ref in ["methodology.md", "corrections.md"]:
    p = SKILL_DIR / "references" / ref
    if not p.exists():
        errors.append(f"references/{ref} 不存在")
    elif p.stat().st_size < 500:
        errors.append(f"references/{ref} 过小（{p.stat().st_size} 字节），疑似空文件")

# 3. 规则出处抽查：正文里 aweme_id@MM:SS 标注数应 >= 20
if skill_md.exists():
    cite_count = len(re.findall(r"\b\d{19}@\d{2}:\d{2}", text))
    if cite_count < 20:
        warnings.append(f"SKILL.md 中 aweme_id@MM:SS 出处标注仅 {cite_count} 处，建议 >=20")

# 4. 硬编码历史点位检测：指数历史点位（3000-5000 之间的孤立数字，带"点/整数关口"上下文）
#    注意：形态参数如"20-30%""50%""2倍"是规则参数，不算历史点位
#    只匹配类似"3900 点""4000 点""4100"这种指数点位写法
if skill_md.exists():
    bad_points = re.findall(r"[3-5]\d{3}\s*点", text)
    if bad_points:
        errors.append(f"SKILL.md 中疑似硬编码历史指数点位: {bad_points}（点位必须动态计算，禁止硬编码）")

# 5. UTF-8 编码检查
for f in [skill_md, SKILL_DIR / "references" / "methodology.md", SKILL_DIR / "references" / "corrections.md"]:
    if f.exists():
        try:
            f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{f.name} 不是 UTF-8 编码")

# 输出
print("=" * 60)
print(f"Skill 目录: {SKILL_DIR}")
print("=" * 60)
if errors:
    print(f"❌ 错误 {len(errors)} 条:")
    for e in errors:
        print(f"  - {e}")
else:
    print("✅ 无错误")
if warnings:
    print(f"⚠️  警告 {len(warnings)} 条:")
    for w in warnings:
        print(f"  - {w}")
else:
    print("✅ 无警告")
print("=" * 60)
if errors:
    sys.exit(1)
else:
    print("校验通过 ✅")
    sys.exit(0)
