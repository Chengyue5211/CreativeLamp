"""
生成软件著作权登记源代码文档
绘创前程 V1.0

规则：
- 每页50行代码
- 前30页（第1-1500行）+ 后30页（最后1500行）
- 页眉：绘创前程 V1.0  第X页
"""

import os

PROJECT_ROOT = r"D:\CreativeLamp"

# 按指定顺序排列的源代码文件
FILES = [
    "backend/main.py",
    "backend/core/config.py",
    "backend/core/database.py",
    "backend/core/security.py",
    "backend/data/prototypes.py",
    "backend/data/transforms.py",
    "backend/services/auth_service.py",
    "backend/services/training_service.py",
    "backend/services/referral_service.py",
    "backend/routers/auth.py",
    "backend/routers/training.py",
    "backend/routers/works.py",
    "backend/routers/showcase.py",
    "backend/routers/parent.py",
    "backend/routers/merch.py",
    "backend/routers/referral.py",
    "backend/routers/health.py",
    "frontend/static/js/utils.js",
    "frontend/static/js/api.js",
    "frontend/static/js/pages.js",
    "frontend/static/js/actions.js",
    "frontend/static/js/app.js",
    "frontend/static/js/line-svg.js",
    "frontend/static/js/transform-svg.js",
    "frontend/static/js/contour-svg.js",
    "frontend/static/sw.js",
    "frontend/static/css/main.css",
    "frontend/templates/index.html",
]

LINES_PER_PAGE = 50
PAGES = 30
TOTAL_LINES_NEEDED = LINES_PER_PAGE * PAGES  # 1500

SOFTWARE_NAME = "绘创前程"
VERSION = "V1.0"
HEADER_LINE = f"软件名称：{SOFTWARE_NAME}  版本号：{VERSION}"


def read_all_files():
    """读取所有文件并拼接，文件之间用分隔符"""
    all_lines = []
    for rel_path in FILES:
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        # 根据文件类型选择注释符号
        if rel_path.endswith((".py",)):
            separator = f"# ===== 文件: {rel_path} ====="
        elif rel_path.endswith((".css",)):
            separator = f"/* ===== 文件: {rel_path} ===== */"
        elif rel_path.endswith((".html",)):
            separator = f"<!-- ===== 文件: {rel_path} ===== -->"
        else:
            separator = f"// ===== 文件: {rel_path} ====="

        all_lines.append(separator)

        if not os.path.exists(full_path):
            all_lines.append(f"[文件不存在: {rel_path}]")
            print(f"  警告: 文件不存在 - {full_path}")
            continue

        with open(full_path, "r", encoding="utf-8") as f:
            file_lines = f.read().splitlines()
        all_lines.extend(file_lines)
        print(f"  已读取: {rel_path} ({len(file_lines)} 行)")

    return all_lines


def format_pages(lines, start_page=1):
    """将代码行按每页50行格式化，添加页眉"""
    output_parts = []
    page_num = start_page
    for i in range(0, len(lines), LINES_PER_PAGE):
        page_lines = lines[i : i + LINES_PER_PAGE]
        header = f"{SOFTWARE_NAME} {VERSION}  第{page_num}页"
        output_parts.append(header)
        output_parts.append("")  # 页眉后空行
        output_parts.extend(page_lines)
        output_parts.append("")  # 页间空行
        page_num += 1
    return "\n".join(output_parts)


def main():
    print("=" * 60)
    print("  绘创前程 软件著作权源代码文档生成器")
    print("=" * 60)
    print()

    # 1. 读取所有文件
    print("[1/4] 读取源代码文件...")
    all_lines = read_all_files()
    total = len(all_lines)
    print(f"\n  源代码总行数: {total}")
    print(f"  总页数 (每页{LINES_PER_PAGE}行): {(total + LINES_PER_PAGE - 1) // LINES_PER_PAGE}")
    print()

    if total < TOTAL_LINES_NEEDED * 2:
        print(f"  注意: 总行数 {total} 不足 {TOTAL_LINES_NEEDED * 2}，前后部分可能有重叠")

    # 2. 提取前1500行
    print(f"[2/4] 提取前 {TOTAL_LINES_NEEDED} 行 (前{PAGES}页)...")
    first_lines = all_lines[:TOTAL_LINES_NEEDED]

    # 3. 提取后1500行
    print(f"[3/4] 提取后 {TOTAL_LINES_NEEDED} 行 (后{PAGES}页)...")
    last_lines = all_lines[-TOTAL_LINES_NEEDED:]

    # 计算后30页的起始页码
    total_pages = (total + LINES_PER_PAGE - 1) // LINES_PER_PAGE
    last_start_page = total_pages - PAGES + 1

    # 4. 生成输出文件
    print("[4/4] 生成输出文件...")

    output_dir = os.path.join(PROJECT_ROOT, "docs", "legal")
    os.makedirs(output_dir, exist_ok=True)

    # 前30页
    first_output = os.path.join(output_dir, "软著源代码_前30页.txt")
    first_content = HEADER_LINE + "\n\n" + format_pages(first_lines, start_page=1)
    with open(first_output, "w", encoding="utf-8") as f:
        f.write(first_content)
    print(f"  已生成: {first_output}")

    # 后30页
    last_output = os.path.join(output_dir, "软著源代码_后30页.txt")
    last_content = HEADER_LINE + "\n\n" + format_pages(last_lines, start_page=last_start_page)
    with open(last_output, "w", encoding="utf-8") as f:
        f.write(last_content)
    print(f"  已生成: {last_output}")

    print()
    print("=" * 60)
    print("  生成完成!")
    print(f"  前30页: 第1页 ~ 第{PAGES}页")
    print(f"  后30页: 第{last_start_page}页 ~ 第{total_pages}页")
    print("=" * 60)


if __name__ == "__main__":
    main()
