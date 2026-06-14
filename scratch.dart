import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {
  final url = Uri.parse('https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd0000017c7ccd02bac445d36a5a228846357fa2&format=json&limit=5&filters[state.keyword]=Andhra%20Pradesh');
  final response = await http.get(url);
  print(response.body);
}
