import re

fp = 'src/domains/cuisine/ui/inventaire.py'
with open(fp, 'rb') as f:
    data = f.read()

original_size = len(data)

# Decode and work with text
content = data.decode('utf-8', errors='replace')

# Replace emojis
content = content.replace('ðŸ"´', '🔴')
content = content.replace('ðŸ""', '📔')
content = content.replace('ðŸ', '📚')

# Write back
with open(fp, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'FIXED: {fp}')
