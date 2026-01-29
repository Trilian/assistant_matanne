import sys

fp = 'src/domains/cuisine/ui/inventaire.py'
try:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count broken chars
    count = content.count('ðŸ') + content.count('êœ')
    
    if count > 0:
        # Replace all broken sequences
        replacements = [
            ('ðŸ"´', '🔴'),
            ('ðŸ""', '📔'),
            ('ðŸ"…', '📅'),
            ('ðŸŽ¯', '🎯'),
            ('êœ…', '✨'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'FIXED: {fp} ({count} broken chars found)')
    else:
        print('OK')
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
