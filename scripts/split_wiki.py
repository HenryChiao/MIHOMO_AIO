import os
import re

# 配置路径
SOURCE_FILE = 'doc/mihomo配置从入门到进阶完全教程.md'
WIKI_DIR = 'wiki_output'

def split_markdown():
    if not os.path.exists(WIKI_DIR):
        os.makedirs(WIKI_DIR)

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则表达式按一级标题拆分（保留标题）
    sections = re.split(r'\n(?=# )', '\n' + content)
    
    sidebar_links = []
    
    for section in sections:
        if not section.strip():
            continue
            
        # 提取标题行作为文件名
        lines = section.strip().split('\n')
        title_line = lines[0].replace('# ', '').strip()
        
        # 规范化文件名：去除特殊字符，处理首页
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
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(section.strip() + '\n')
            
        # 添加到目录链接中
        sidebar_links.append(f"* [{sidebar_title}]({filename.replace(' ', '%20')})")
        
        print(f"✅ 生成页面: {filename}.md")

    # 生成 _Sidebar.md (侧边栏目录)
    sidebar_content = "## 📖 教程目录\n\n" + "\n".join(sidebar_links)
    with open(os.path.join(WIKI_DIR, '_Sidebar.md'), 'w', encoding='utf-8') as f:
        f.write(sidebar_content)
        
    print("✅ 侧边栏目录 _Sidebar.md 生成完毕！")

if __name__ == '__main__':
    split_markdown()
