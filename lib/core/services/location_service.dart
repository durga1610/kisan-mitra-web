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
}
