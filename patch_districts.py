import re

with open('lib/features/profile_setup/data/profile_setup_data.dart', 'r', encoding='utf-8') as f:
    content = f.read()

with open('districts_map.dart.txt', 'r', encoding='utf-8') as f:
    new_data = f.read()

# Replace states and districts
pattern = re.compile(r'static const List<String> states = \[.*?\];\s*static const Map<String, List<String>> districts = \{.*?\};', re.DOTALL)
new_content = pattern.sub(new_data, content)

with open('lib/features/profile_setup/data/profile_setup_data.dart', 'w', encoding='utf-8') as f:
    f.write(new_content)
    
print("Successfully patched")
