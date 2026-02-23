import os

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

    # 1. 逐行扫描，精准避开代码块内的 YAML 注释
    for line in lines:
        # 检测是否进入或离开代码块
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        
        # 如果不在代码块中，且是以 '# ' 开头的一级标题 -> 触发切割
        if not in_code_block and line.startswith('# '):
            if current_section:
                sections.append(''.join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    
    # 把最后一部分也加进去
    if current_section:
        sections.append(''.join(current_section))

    sidebar_links = []
    
    # 2. 处理切割好的区块并生成文件
    for section_content in sections:
        if not section_content.strip():
            continue
            
        # 提取当前块的标题行
        section_lines = section_content.strip().split('\n')
        title_line = section_lines[0].replace('# ', '').strip()
        
        # 规范化文件名与侧边栏标题
        if "Mihomo 配置从入门到进阶" in title_line:
            filename = "Home"
            sidebar_title = "🏠 首页 (Home)"
        elif "第一阶段" in title_line:
            filename = "第一阶段：小白篇"
            sidebar_title = "🟢 第一阶段：小白篇"
        elif "第二阶段" in title_line:
            filename = "第二阶段：新手篇"
            sidebar_title = "🟡 第二阶段：新手篇"
        elif "第三阶段" in title_line:
            filename = "第三阶段：进阶篇"
            sidebar_title = "🔴 第三阶段：进阶篇"
        else:
            filename = title_line.replace('/', '-').replace(':', '：')
            sidebar_title = title_line

        filepath = os.path.join(WIKI_DIR, f'{filename}.md')
        
        # 写入拆分后的文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(section_content.strip() + '\n')
            
        # 添加到目录链接中
        sidebar_links.append(f"* [{sidebar_title}]({filename.replace(' ', '%20')})")
        
        print(f"✅ 生成页面: {filename}.md")

    # 3. 生成 GitHub Wiki 专用的 _Sidebar.md
    sidebar_content = "## 📖 教程目录\n\n" + "\n".join(sidebar_links)
    with open(os.path.join(WIKI_DIR, '_Sidebar.md'), 'w', encoding='utf-8') as f:
        f.write(sidebar_content)
        
    print("✅ 侧边栏目录 _Sidebar.md 生成完毕！")

if __name__ == '__main__':
    split_markdown()
