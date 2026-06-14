import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find `const Text('something'.tr(context))` and remove `const `
    new_content = re.sub(r"const\s+Text\((['\"].+?['\"]\s*\.tr\(context\))\)", r"Text(\1)", content)
    
    # Also find `const SnackBar(content: Text('something'.tr(context)))` and remove `const `
    new_content = re.sub(r"const\s+SnackBar\(content:\s*Text\((['\"].+?['\"]\s*\.tr\(context\))\)", r"SnackBar(content: Text(\1)", new_content)

    # Some SnackBars might have other params
    new_content = re.sub(r"const\s+SnackBar\(", r"SnackBar(", new_content)
    
    # Any other `const` that precedes something that contains `.tr(context)`
    # Let's just remove `const` before `Text` if `.tr` is inside.
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed const in {filepath}")

for root, _, files in os.walk('lib'):
    for file in files:
        if file.endswith('.dart'):
            process_file(os.path.join(root, file))
