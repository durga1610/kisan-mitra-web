import urllib.request
import json

url = "https://raw.githubusercontent.com/sab99r/Indian-States-And-Districts/master/states-and-districts.json"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode())
    
    dart_code = "  static const Map<String, List<String>> districts = {\n"
    states_list = "  static const List<String> states = [\n"
    for state_data in data['states']:
        state_name = state_data['state']
        states_list += f"    '{state_name}',\n"
        districts = state_data['districts']
        dart_code += f"    '{state_name}': [\n"
        for i in range(0, len(districts), 5):
            chunk = districts[i:i+5]
            dart_code += "      " + ", ".join([f"'{d.replace(chr(39), chr(92)+chr(39))}'" for d in chunk]) + ",\n"
        dart_code += "    ],\n"
    dart_code += "  };\n"
    states_list += "  ];\n"
    
    with open("districts_map.dart.txt", "w", encoding="utf-8") as f:
        f.write(states_list + "\n" + dart_code)
    print("Success")
except Exception as e:
    print(e)
