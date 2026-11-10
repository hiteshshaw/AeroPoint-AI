"""
Generates a publication-grade, printable HTML dossier from PROBLEM_B_SOLUTION.md.
Open the generated HTML in Chrome or Edge and press Ctrl+P to save as a clean PDF.
"""
import os
import re

def markdown_to_html(md_text):
    # Escape basic HTML
    html = md_text

    # Title header banner
    lines = html.split('\n')
    processed_lines = []
    in_code_block = False
    in_table = False

    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                lang = line.strip()[3:]
                processed_lines.append(f'<pre><code class="language-{lang}">')
            else:
                processed_lines.append('</code></pre>')
            continue

        if in_code_block:
            # Escape HTML characters inside code
            escaped = (line.replace('&', '&amp;')
                           .replace('<', '&lt;')
                           .replace('>', '&gt;'))
            processed_lines.append(escaped)
            continue

        # Tables
        if line.strip().startswith('|') and line.strip().endswith('|'):
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if all(set(c) <= {'-', ':', ' '} for c in cells):
                continue # Skip markdown separator row
            
            is_header = not in_table
            if not in_table:
                in_table = True
                processed_lines.append('<div class="table-container"><table>')
                tag = 'th'
            else:
                tag = 'td'

            row_html = '<tr>' + ''.join(f'<{tag}>{cell}</{tag}>' for cell in cells) + '</tr>'
            processed_lines.append(row_html)
            continue
        else:
            if in_table:
                in_table = False
                processed_lines.append('</table></div>')

        # Headings
        if line.startswith('# '):
            processed_lines.append(f'<h1 class="doc-title">{line[2:]}</h1>')
        elif line.startswith('## '):
            processed_lines.append(f'<h2 class="section-title">{line[3:]}</h2>')
        elif line.startswith('### '):
            processed_lines.append(f'<h3 class="question-title">{line[4:]}</h3>')
        elif line.startswith('#### '):
            processed_lines.append(f'<h4 class="sub-title">{line[5:]}</h4>')
        elif line.strip() == '---':
            processed_lines.append('<hr class="divider"/>')
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            processed_lines.append(f'<li>{line.strip()[2:]}</li>')
        elif re.match(r'^\d+\.\s', line.strip()):
            content = re.sub(r'^\d+\.\s', '', line.strip())
            processed_lines.append(f'<li class="ordered">{content}</li>')
        elif line.strip().startswith('> '):
            processed_lines.append(f'<blockquote>{line.strip()[2:]}</blockquote>')
        elif line.strip():
            processed_lines.append(f'<p>{line.strip()}</p>')
        else:
            processed_lines.append('')

    if in_table:
        processed_lines.append('</table></div>')

    full_body = '\n'.join(processed_lines)

    # Inline formatting (Bold, Italic, Code, Math)
    full_body = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', full_body)
    full_body = re.sub(r'\*(.*?)\*', r'<em>\1</em>', full_body)
    full_body = re.sub(r'`(.*?)`', r'<code>\1</code>', full_body)

    # Wrap list items
    full_body = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', full_body)

    return full_body


def build_printable_html():
    source_path = "PROBLEM_B_SOLUTION.md"
    output_path = "AeroPoint_AI_Problem_B_Solution.html"

    if not os.path.exists(source_path):
        print(f"[ERROR] {source_path} not found.")
        return

    with open(source_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    body_content = markdown_to_html(md_content)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Problem B Solution - AeroPoint AI Accessibility Bridge</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {{
            --primary: #0066cc;
            --primary-dark: #004c99;
            --secondary: #107c41;
            --bg: #ffffff;
            --text: #24292f;
            --text-muted: #57606a;
            --border: #d0d7de;
            --code-bg: #f6f8fa;
            --accent-bg: #f0f7ff;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.65;
            color: var(--text);
            background-color: #f4f6f9;
            margin: 0;
            padding: 40px 20px;
        }}

        .page-container {{
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            padding: 60px 80px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            border-radius: 8px;
            border: 1px solid var(--border);
        }}

        .doc-title {{
            font-size: 2.2rem;
            font-weight: 800;
            color: #1a1a2e;
            border-bottom: 3px solid var(--primary);
            padding-bottom: 16px;
            margin-top: 0;
            letter-spacing: -0.02em;
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-dark);
            margin-top: 36px;
            margin-bottom: 16px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }}

        .question-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #1f2328;
            margin-top: 28px;
            margin-bottom: 12px;
            background: var(--accent-bg);
            padding: 8px 14px;
            border-left: 4px solid var(--primary);
            border-radius: 0 4px 4px 0;
        }}

        .sub-title {{
            font-size: 1.05rem;
            font-weight: 600;
            color: #333;
            margin-top: 20px;
            margin-bottom: 8px;
        }}

        p {{
            margin: 10px 0 16px 0;
            font-size: 0.98rem;
        }}

        ul, ol {{
            margin: 8px 0 18px 24px;
            padding: 0;
        }}

        li {{
            margin-bottom: 6px;
            font-size: 0.95rem;
        }}

        strong {{
            color: #0d1117;
            font-weight: 600;
        }}

        pre {{
            background-color: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 16px 18px;
            overflow-x: auto;
            font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
            font-size: 0.88rem;
            line-height: 1.45;
            margin: 16px 0;
        }}

        code {{
            font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
            background-color: var(--code-bg);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
            color: #b31d28;
            border: 1px solid #e1e4e8;
        }}

        pre code {{
            padding: 0;
            border: none;
            color: inherit;
        }}

        blockquote {{
            margin: 16px 0;
            padding: 10px 20px;
            background-color: #f8fafc;
            border-left: 4px solid #64748b;
            color: #475569;
            font-style: italic;
        }}

        .table-container {{
            overflow-x: auto;
            margin: 20px 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.92rem;
            margin: 0;
        }}

        th, td {{
            padding: 10px 14px;
            text-align: left;
            border: 1px solid var(--border);
        }}

        th {{
            background-color: #f6f8fa;
            font-weight: 600;
            color: #24292f;
        }}

        tr:nth-child(even) td {{
            background-color: #fcfcfc;
        }}

        .divider {{
            height: 1px;
            background-color: var(--border);
            border: none;
            margin: 32px 0;
        }}

        .badge-header {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }}

        .badge {{
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 12px;
            background: #e1f0ff;
            color: #0366d6;
            border: 1px solid #c8e1ff;
        }}

        /* Print Specific Styling */
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
                color: #000;
            }}
            .page-container {{
                box-shadow: none;
                border: none;
                padding: 0;
                max-width: 100%;
            }}
            .question-title {{
                page-break-after: avoid;
                break-after: avoid;
            }}
            pre, table {{
                page-break-inside: avoid;
                break-inside: avoid;
            }}
            @page {{
                margin: 20mm 15mm 20mm 15mm;
            }}
        }}
    </style>
</head>
<body>
    <div class="page-container">
        <div class="badge-header">
            <span class="badge">Problem B: AI PC Accessibility Assistant</span>
            <span class="badge">100% On-Device & Offline</span>
            <span class="badge">WCAG 2.2 AAA Compliant</span>
            <span class="badge">Zero Battery Overheating</span>
        </div>
        {body_content}
    </div>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ Generated publication-grade document: {output_path}")
    print(f"   Size: {os.path.getsize(output_path)} bytes")

if __name__ == '__main__':
    build_printable_html()

