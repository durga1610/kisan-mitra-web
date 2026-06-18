import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {
  final apiKey = const String.fromEnvironment('MANDI_API_KEY', defaultValue: 'YOUR_MANDI_API_KEY');
  final url = Uri.parse('https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=' + apiKey + '&format=json&limit=10000&filters%5Bstate.keyword%5D=Andhra%20Pradesh');
  final response = await http.get(url);
  final data = json.decode(response.body);
  final records = data['records'] as List;
  print('Found ' + records.length.toString() + ' records for Andhra Pradesh');
  
  // Count unique crops
  final uniqueCrops = <String>{};
  for (var r in records) {
    uniqueCrops.add(r['commodity'].toString());
  }
  print('Unique crops: ' + uniqueCrops.length.toString());
  print('Crops: ' + uniqueCrops.join(", "));
}
