import os
import re
import glob

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find instances of Text('...') and Text("...")
    # but not if it already has .tr(context)
    # also skip if it contains $ (string interpolation)
    
    # We will look for Text('...')
    pattern1 = re.compile(r"Text\('([^'\$]+)'(?!\.tr\()")
    pattern2 = re.compile(r'Text\("([^"\$]+)"(?!\.tr\()')
    
    new_content = pattern1.sub(r"Text('\1'.tr(context)", content)
    new_content = pattern2.sub(r'Text("\1".tr(context)', new_content)
    
    # Check if there are other hardcoded strings in SnackBar(content: Text('...'))
    # actually the above pattern will match those too!
    
    if new_content != content:
        # Check if we need to add the import
        if 'app_translations.dart' not in new_content:
            # find flutter/material.dart import and add it after
            import_statement = "import 'package:kisan_mitra/core/localization/app_translations.dart';\n"
            if "import 'package:flutter/material.dart';" in new_content:
                new_content = new_content.replace(
                    "import 'package:flutter/material.dart';", 
                    "import 'package:flutter/material.dart';\n" + import_statement
                )
            else:
                # just put it at the top
                new_content = import_statement + new_content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for root, _, files in os.walk('lib'):
    for file in files:
        if file.endswith('.dart'):
            process_file(os.path.join(root, file))
