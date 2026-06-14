class UserModel {
  final String uid;
  final String name;
  final String phone;
  final String? email;
  final String? location;
  final bool setupCompleted;
  final String? profileImageUrl;
  final DateTime updatedAt;

  UserModel({
    required this.uid,
    required this.name,
    required this.phone,
    this.email,
    this.location,
    this.setupCompleted = false,
    this.profileImageUrl,
    required this.updatedAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'uid': uid,
      'name': name,
      'phone': phone,
      'email': email,
      'location': location,
      'setupCompleted': setupCompleted,
      'profileImageUrl': profileImageUrl,
      'updatedAt': updatedAt.toIso8601String(),
    };
  }

  factory UserModel.fromMap(Map<String, dynamic> map) {
    return UserModel(
      uid: map['uid'] ?? '',
      name: map['name'] ?? '',
      phone: map['phone'] ?? '',
      email: map['email'],
      location: map['location'],
      setupCompleted: map['setupCompleted'] ?? false,
      profileImageUrl: map['profileImageUrl'],
      updatedAt: DateTime.parse(map['updatedAt'] ?? DateTime.now().toIso8601String()),
    );
  }
}
