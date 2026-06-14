with open('lib/features/profile_setup/data/profile_setup_data.dart', 'r', encoding='utf-8') as f:
    content = f.read()

with open('districts_map.dart.txt', 'r', encoding='utf-8') as f:
    new_data = f.read()

# Instead of regex, let's just split by known markers
marker_start = "  // ── Indian States ──────────────────────────────────────────────────────────"
marker_end = "  /// Returns districts for a given state, or an empty list."

part1 = content.split(marker_start)[0]
part2 = content.split(marker_end)[1]

new_content = part1 + marker_start + "\n" + new_data + "\n  /// Returns districts for a given state, or an empty list." + part2

with open('lib/features/profile_setup/data/profile_setup_data.dart', 'w', encoding='utf-8') as f:
    f.write(new_content)
    
print("Successfully patched")
