import re
with open(r'D:\08_tmp\02_media\media-arcitles\2\2.20260426.md', 'r', encoding='utf-8') as f:
    content = f.read()

text = re.sub(r'!\[.*?\]\(.*?\)', '', content)
text = re.sub(r'#{1,6}\s', '', text)
text = re.sub(r'\*\*|\*|>|`|~~', '', text)
text = re.sub(r'\|.*?\|', '', text)
text = re.sub(r'-{2,}', '', text)
text = re.sub(r'\n\s*\n+', '\n', text).strip()

parts = text.split('寓意')
story = parts[0].strip() if len(parts) > 1 else text

print(f'Total chars: {len(text)}')
print(f'Story chars (before analysis): {len(story)}')
print(f'Total lines: {len(text.splitlines())}')
