class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? source;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.source,
  });

  Map<String, dynamic> toMap() {
    return {
      'text': text,
      'isUser': isUser,
      'timestamp': timestamp.toIso8601String(),
      'source': source,
    };
  }

  factory ChatMessage.fromMap(Map<String, dynamic> map) {
    return ChatMessage(
      text: map['text'] ?? '',
      isUser: map['isUser'] ?? false,
      timestamp: DateTime.parse(map['timestamp'] ?? DateTime.now().toIso8601String()),
      source: map['source'],
    );
  }
}
