import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class LocationService {
  Future<Position?> getCurrentPosition() async {
    bool serviceEnabled;
    LocationPermission permission;

    debugPrint('[Weather] Permission check started');
    serviceEnabled = await Geolocator.isLocationServiceEnabled().timeout(const Duration(seconds: 5), onTimeout: () => false);
    if (!serviceEnabled) {
      return null;
    }

    permission = await Geolocator.checkPermission().timeout(const Duration(seconds: 5), onTimeout: () => LocationPermission.denied);
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission().timeout(const Duration(seconds: 15), onTimeout: () => LocationPermission.denied);
      if (permission == LocationPermission.denied) {
        return null;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      return null;
    }
    debugPrint('[Weather] Permission granted');

    try {
      debugPrint('[Weather] Location fetch started');
      
      // Try to get last known position first for instant load
      Position? position;
      if (!kIsWeb) {
        try {
          position = await Geolocator.getLastKnownPosition();
        } catch (_) {}
      }
      
      if (position == null) {
        debugPrint('[Weather] No last known position. Fetching current...');
        position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.low).timeout(
          const Duration(seconds: 15),
          onTimeout: () => throw Exception('Location request timed out after 15 seconds'),
        );
      } else {
        // Warm up GPS in background
        Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.low).catchError((_) => position!);
      }
      
      debugPrint('[Weather] Location received');
      return position;
    } catch (e) {
      debugPrint('[Weather] Error getting location: $e');
      // If we completely failed, we might still have a last known position
      if (!kIsWeb) {
        try {
          final lastPos = await Geolocator.getLastKnownPosition();
          if (lastPos != null) return lastPos;
        } catch (_) {}
      }
      rethrow;
    }
  }

  Future<Map<String, String>> getAddressFromLatLng(Position position) async {
    try {
      List<Placemark> placemarks = [];
      try {
        placemarks = await placemarkFromCoordinates(
          position.latitude,
          position.longitude,
        ).timeout(const Duration(seconds: 3));
      } catch (e) {
        debugPrint('[Weather] Native geocoding failed, falling back to OSM Nominatim');
      }

      if (placemarks.isNotEmpty) {
        Placemark place = placemarks[0];
        if ((place.administrativeArea ?? '').isNotEmpty) {
          return {
            'state': place.administrativeArea ?? '',
            'district': place.subAdministrativeArea ?? place.locality ?? '',
            'village': place.subLocality ?? place.locality ?? '',
          };
        }
      }

      // Fallback for Windows/Web using OpenStreetMap Nominatim API
      final url = Uri.parse('https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.latitude}&lon=${position.longitude}&zoom=18&addressdetails=1');
      final response = await http.get(url, headers: {
        'User-Agent': 'KisanMitraApp/1.0',
      }).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final address = data['address'] as Map<String, dynamic>?;
        if (address != null) {
          return {
            'state': address['state'] ?? '',
            'district': address['state_district'] ?? address['county'] ?? address['city_district'] ?? '',
            'village': address['village'] ?? address['suburb'] ?? address['town'] ?? address['city'] ?? '',
          };
        }
      }
      
      return {'state': '', 'district': '', 'village': ''};
    } catch (e) {
      debugPrint('[Weather] Geocoding error: $e');
      return {'state': '', 'district': '', 'village': ''};
    }
  }

  Future<Map<String, double>?> getLatLngFromAddress(String village, String district, String state) async {
    try {
      final query = [
        if (village.isNotEmpty) village,
        if (district.isNotEmpty) district,
        if (state.isNotEmpty) state,
        'India'
      ].join(', ');
      
      debugPrint('[LocationService] Geocoding query: $query');
      
      // Try native geocoding first
      try {
        List<Location> locations = await locationFromAddress(query).timeout(const Duration(seconds: 3));
        if (locations.isNotEmpty) {
          final loc = locations.first;
          debugPrint('[LocationService] Native geocoding success: ${loc.latitude}, ${loc.longitude}');
          return {
            'latitude': loc.latitude,
            'longitude': loc.longitude,
          };
        }
      } catch (e) {
        debugPrint('[LocationService] Native geocoding failed, trying OSM search');
      }

      // Fallback for Windows/Web using OpenStreetMap Nominatim Search API
      final encodedQuery = Uri.encodeComponent(query);
      final url = Uri.parse('https://nominatim.openstreetmap.org/search?q=$encodedQuery&format=json&limit=1');
      final response = await http.get(url, headers: {
        'User-Agent': 'KisanMitraApp/1.0',
      }).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        if (data.isNotEmpty) {
          final lat = double.tryParse(data[0]['lat']?.toString() ?? '');
          final lon = double.tryParse(data[0]['lon']?.toString() ?? '');
          if (lat != null && lon != null) {
            debugPrint('[LocationService] OSM geocoding success: $lat, $lon');
            return {
              'latitude': lat,
              'longitude': lon,
            };
          }
        }
      }
      
      // Fallback if village-specific search fails, search by district and state
      if (village.isNotEmpty) {
        final fallbackQuery = [
          if (district.isNotEmpty) district,
          if (state.isNotEmpty) state,
          'India'
        ].join(', ');
        
        debugPrint('[LocationService] Fallback geocoding query: $fallbackQuery');
        final encodedFallbackQuery = Uri.encodeComponent(fallbackQuery);
        final fallbackUrl = Uri.parse('https://nominatim.openstreetmap.org/search?q=$encodedFallbackQuery&format=json&limit=1');
        final fallbackResponse = await http.get(fallbackUrl, headers: {
          'User-Agent': 'KisanMitraApp/1.0',
        }).timeout(const Duration(seconds: 5));

        if (fallbackResponse.statusCode == 200) {
          final List<dynamic> data = json.decode(fallbackResponse.body);
          if (data.isNotEmpty) {
            final lat = double.tryParse(data[0]['lat']?.toString() ?? '');
            final lon = double.tryParse(data[0]['lon']?.toString() ?? '');
            if (lat != null && lon != null) {
              debugPrint('[LocationService] Fallback OSM geocoding success: $lat, $lon');
              return {
                'latitude': lat,
                'longitude': lon,
              };
            }
          }
        }
      }
      
      return null;
    } catch (e) {
      debugPrint('[LocationService] Geocoding error: $e');
      return null;
    }
  }
}
