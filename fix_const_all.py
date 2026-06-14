import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find `const Text(...)` where `...` contains `.tr(context)` and remove `const `
    # Text could have other parameters.
    
    # We can match `const Text(` and if `.tr(context)` is inside, replace `const Text` with `Text`
    # Let's just remove `const` if it's followed by something containing .tr(context) on the same line
    
    lines = content.split('\n')
    new_lines = []
    changed = False
    
    for line in lines:
        if 'const Text(' in line and '.tr(context)' in line:
            line = line.replace('const Text(', 'Text(')
            changed = True
        if 'const SnackBar(' in line and '.tr(context)' in line:
            line = line.replace('const SnackBar(', 'SnackBar(')
            changed = True
        # also for children: [Padding(... , child: Text("...".tr(context)))], if there is a const before it, but there isn't one here.
        # Wait, the error: `children: [Padding(padding: EdgeInsets.all(16), child: Text("...".tr(context)))]`
        # Error says "Not a constant expression."
        # This means the parent is probably `const ExpansionTile(` or something similar.
        # Let's just remove ALL `const ` on lines that have `.tr(context)`.
        
        if '.tr(context)' in line:
            if 'const ' in line:
                # remove const 
                line = re.sub(r'\bconst\s+', '', line)
                changed = True
                
        new_lines.append(line)
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print(f"Fixed const in {filepath}")

for root, _, files in os.walk('lib'):
    for file in files:
        if file.endswith('.dart'):
            process_file(os.path.join(root, file))
