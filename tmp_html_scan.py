import ast
from pathlib import Path
import re

root = Path('.')
issues = []
for path in root.rglob('*.py'):
    if 'tmp_html_scan.py' in path.name:
        continue
    try:
        src = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        src = path.read_text(encoding='latin-1')
    try:
        tree = ast.parse(src)
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            callee = None
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == 'st':
                callee = func.attr
            elif isinstance(func, ast.Name):
                callee = func.id
            if callee not in {'markdown', 'write', 'text', 'caption', 'code'}:
                continue
            text = ''
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    text += arg.value
                elif isinstance(arg, ast.JoinedStr):
                    for part in arg.values:
                        if isinstance(part, ast.Constant) and isinstance(part.value, str):
                            text += part.value
            if '<' not in text or '>' not in text:
                continue
            source = ast.get_source_segment(src, node) or ''
            unsafe = False
            for kw in node.keywords:
                if kw.arg == 'unsafe_allow_html' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    unsafe = True
            issues.append((path, node.lineno, callee, unsafe, source.strip().replace('\n', ' ')))
for path, lineno, callee, unsafe, source in issues:
    if callee == 'markdown' and not unsafe:
        print(f'{path}:{lineno}: {callee} missing unsafe_allow_html {source}')
    elif callee != 'markdown':
        print(f'{path}:{lineno}: {callee} with HTML content {source}')
print('TOTAL', len(issues))
