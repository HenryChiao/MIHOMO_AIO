import os
import re
import urllib.parse

# 配置路径
SOURCE_FILE = 'doc/mihomo配置从入门到进阶完全教程.md'
WIKI_DIR = 'wiki_output'

def split_markdown():
    if not os.path.exists(WIKI_DIR):
        os.makedirs(WIKI_DIR)

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = []
    current_section = []
    in_code_block = False

    # 1. 逐行扫描，精准识别一级和二级标题，同时避开代码块
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        
        is_h1 = line.startswith('# ')
        is_h2 = line.startswith('## ')
        
        # 不在代码块中，且是一级或二级标题时 -> 触发切割
        if not in_code_block and (is_h1 or is_h2):
            if current_section:
                sections.append(''.join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    
    # 将最后一块收尾
    if current_section:
        sections.append(''.join(current_section))

    sidebar_links = []
    
    # 2. 处理区块、生成文件与目录
    for section_content in sections:
        if not section_content.strip():
            continue
            
        lines = section_content.strip().split('\n')
        title_line = lines[0]
        
        is_h1 = title_line.startswith('# ')
        
        # 提取纯文本标题（去除 # 号）
        raw_title = title_line.replace('# ', '').replace('## ', '').strip()
        
        # 净化文件名：去除系统不允许的特殊字符
        safe_filename = re.sub(r'[\\/:*?"<>|]', '-', raw_title)
        
        # 首页特判
        if "Mihomo 配置从入门到进阶" in raw_title:
            filename = "Home"
            sidebar_title = "🏠 首页 (Home)"
        else:
            filename = safe_filename
            sidebar_title = raw_title

        filepath = os.path.join(WIKI_DIR, f'{filename}.md')
        
        # 写入拆分后的文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(section_content.strip() + '\n')
            
        # URL 编码，确保 GitHub Wiki 侧边栏能正确识别含空格/中文的链接
        url_link = urllib.parse.quote(filename)
        
        # 3. 构建带有层级结构的侧边栏
        if is_h1:
            # 一级标题：加粗顶格，前面留个空行更美观
            sidebar_links.append(f"\n* **[{sidebar_title}]({url_link})**")
        else:
            # 二级标题：缩进两个空格，作为子页面
            sidebar_links.append(f"  * [{sidebar_title}]({url_link})")
        
        print(f"✅ 生成页面: {filename}.md")

    # 4. 写入侧边栏文件
    sidebar_content = "## 📖 教程目录\n" + "\n".join(sidebar_links)
    with open(os.path.join(WIKI_DIR, '_Sidebar.md'), 'w', encoding='utf-8') as f:
        f.write(sidebar_content)
        
    print("\n🎉 拆分完成！带有层级结构的 _Sidebar.md 生成完毕！")

if __name__ == '__main__':
    split_markdown()
