import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:provider/provider.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/services/gemini_service.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../../../core/providers/language_provider.dart';
import '../../data/models/chat_message.dart';
import 'package:firebase_auth/firebase_auth.dart';

class AIAdvisoryScreen extends StatefulWidget {
  const AIAdvisoryScreen({super.key});

  @override
  State<AIAdvisoryScreen> createState() => _AIAdvisoryScreenState();
}

class _AIAdvisoryScreenState extends State<AIAdvisoryScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  late GeminiService _geminiService;
  final List<ChatMessage> _messages = [];
  bool _isTyping = false;
  bool _isInitialized = false;
  String? _lastFarmId;
  
  List<Map<String, dynamic>> _sessions = [];
  String? _currentSessionId;

  @override
  void initState() {
    super.initState();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final farmProvider = Provider.of<FarmProvider>(context);
    final farmId = farmProvider.selectedFarm?.id;
    if (!_isInitialized || _lastFarmId != farmId) {
      _isInitialized = true;
      _lastFarmId = farmId;
      final lang = Provider.of<LanguageProvider>(context, listen: false).currentLanguage;
      _geminiService = GeminiService(selectedFarm: farmProvider.selectedFarm, languageCode: lang);
      _loadChatHistory();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  String get _sessionsKey {
    final farmProvider = Provider.of<FarmProvider>(context, listen: false);
    final userId = FirebaseAuth.instance.currentUser?.uid ?? 'guest';
    final farmId = farmProvider.selectedFarm?.id ?? 'default';
    return 'ai_chat_sessions_${userId}_$farmId';
  }

  String get _historyKey {
    final farmProvider = Provider.of<FarmProvider>(context, listen: false);
    final userId = FirebaseAuth.instance.currentUser?.uid ?? 'guest';
    final farmId = farmProvider.selectedFarm?.id ?? 'default';
    return 'ai_chat_history_${userId}_${farmId}_${_currentSessionId ?? "default"}';
  }

  Future<void> _loadChatHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Load sessions first
      final sessionsJson = prefs.getString(_sessionsKey);
      if (sessionsJson != null) {
        final List<dynamic> decoded = jsonDecode(sessionsJson);
        _sessions = List<Map<String, dynamic>>.from(decoded);
      }

      if (_sessions.isEmpty) {
        // Create a default first session
        _currentSessionId = DateTime.now().millisecondsSinceEpoch.toString();
        _sessions.add({
          'id': _currentSessionId,
          'title': 'New Chat',
          'timestamp': DateTime.now().toIso8601String(),
        });
        await _saveSessions();
      } else {
        _currentSessionId = _sessions.first['id'];
      }

      // Load messages for current session
      _messages.clear();
      final historyJson = prefs.getString(_historyKey);
      if (historyJson != null) {
        final List<dynamic> decoded = jsonDecode(historyJson);
        setState(() {
          _messages.addAll(decoded.map((m) => ChatMessage.fromMap(m)).toList());
        });
        _scrollToBottom();
      } else {
        setState(() {
          _messages.add(ChatMessage(
            text: 'Hello! I am Kisan Mitra AI. How can I help you with your farming today?',
            isUser: false,
            timestamp: DateTime.now(),
          ));
        });
        await _saveChatHistory();
      }
    } catch (e) {
      debugPrint('Error loading chat history: $e');
    }
  }

  Future<void> _saveChatHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = jsonEncode(_messages.map((m) => m.toMap()).toList());
      await prefs.setString(_historyKey, historyJson);
    } catch (e) {
      debugPrint('Error saving chat history: $e');
    }
  }

  Future<void> _saveSessions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_sessionsKey, jsonEncode(_sessions));
    } catch (e) {
      debugPrint('Error saving chat sessions: $e');
    }
  }

  Future<void> _switchSession(String sessionId) async {
    if (_currentSessionId == sessionId) return;
    setState(() {
      _currentSessionId = sessionId;
      _messages.clear();
      _isTyping = false;
    });

    final prefs = await SharedPreferences.getInstance();
    final historyJson = prefs.getString(_historyKey);
    if (historyJson != null) {
      final List<dynamic> decoded = jsonDecode(historyJson);
      setState(() {
        _messages.addAll(decoded.map((m) => ChatMessage.fromMap(m)).toList());
      });
      _scrollToBottom();
    } else {
      setState(() {
        _messages.add(ChatMessage(
          text: 'Hello! I am Kisan Mitra AI. How can I help you with your farming today?',
          isUser: false,
          timestamp: DateTime.now(),
        ));
      });
      await _saveChatHistory();
    }
  }

  Future<void> _createNewChat() async {
    final newSessionId = DateTime.now().millisecondsSinceEpoch.toString();
    setState(() {
      _sessions.insert(0, {
        'id': newSessionId,
        'title': 'New Chat',
        'timestamp': DateTime.now().toIso8601String(),
      });
      _currentSessionId = newSessionId;
      _messages.clear();
      _messages.add(ChatMessage(
        text: 'Hello! I am Kisan Mitra AI. How can I help you with your farming today?',
        isUser: false,
        timestamp: DateTime.now(),
      ));
      _isTyping = false;
    });
    await _saveSessions();
    await _saveChatHistory();
    _scrollToBottom();
  }

  Future<void> _deleteSession(String sessionId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Delete Chat'.tr(context)),
        content: Text('Are you sure you want to delete this chat session?'.tr(context)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text('Cancel'.tr(context))),
          TextButton(onPressed: () => Navigator.pop(context, true), child: Text('Delete'.tr(context), style: const TextStyle(color: Colors.red))),
        ],
      ),
    );

    if (confirmed == true) {
      final prefs = await SharedPreferences.getInstance();
      
      final farmProvider = Provider.of<FarmProvider>(context, listen: false);
      final userId = FirebaseAuth.instance.currentUser?.uid ?? 'guest';
      final farmId = farmProvider.selectedFarm?.id ?? 'default';
      final histKey = 'ai_chat_history_${userId}_${farmId}_$sessionId';
      await prefs.remove(histKey);

      setState(() {
        _sessions.removeWhere((s) => s['id'] == sessionId);
      });
      await _saveSessions();

      if (_currentSessionId == sessionId) {
        if (_sessions.isNotEmpty) {
          await _switchSession(_sessions.first['id']!);
        } else {
          await _createNewChat();
        }
      }
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _handleSendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    _controller.clear();
    setState(() {
      _messages.add(ChatMessage(
        text: text,
        isUser: true,
        timestamp: DateTime.now(),
      ));
      _isTyping = true;
    });
    _scrollToBottom();

    // Auto-update title if it's default "New Chat"
    final currentSession = _sessions.firstWhere((s) => s['id'] == _currentSessionId);
    if (currentSession['title'] == 'New Chat' || currentSession['title'] == 'नया चैट') {
      setState(() {
        currentSession['title'] = text.length > 25 ? '${text.substring(0, 22)}...' : text;
      });
      await _saveSessions();
    }

    try {
      final response = await _geminiService.getResponse(text);
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            text: response,
            isUser: false,
            timestamp: DateTime.now(),
          ));
          _isTyping = false;
        });
        _scrollToBottom();
        _saveChatHistory();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            text: 'I am sorry, something went wrong. Please check your internet connection.',
            isUser: false,
            timestamp: DateTime.now(),
          ));
          _isTyping = false;
        });
        _scrollToBottom();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      appBar: _buildAppBar(),
      drawer: _buildChatHistoryDrawer(isDarkMode),
      body: Column(
        children: [
          Expanded(
            child: Column(
              children: [
                Expanded(
                  child: _messages.isEmpty
                      ? _buildEmptyState()
                      : ListView.builder(
                          controller: _scrollController,
                          padding: const EdgeInsets.all(16),
                          itemCount: _messages.length,
                          itemBuilder: (context, index) {
                            return _buildChatBubble(_messages[index]);
                          },
                        ),
                ),
                if (_messages.length < 5) _buildSuggestionChips(),
              ],
            ),
          ),
          if (_isTyping) _buildTypingIndicator(),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildChatHistoryDrawer(bool isDarkMode) {
    return Drawer(
      child: Container(
        color: isDarkMode ? const Color(0xFF1E1E1E) : Colors.white,
        child: Column(
          children: [
            UserAccountsDrawerHeader(
              decoration: const BoxDecoration(
                gradient: AppColors.primaryGradient,
              ),
              currentAccountPicture: const CircleAvatar(
                backgroundColor: Colors.white24,
                child: Icon(Icons.auto_awesome, color: Colors.white, size: 36),
              ),
              accountName: Text(
                'AI Advisory History'.tr(context),
                style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 16),
              ),
              accountEmail: const SizedBox.shrink(),
            ),
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(context); // close drawer
                  _createNewChat();
                },
                icon: const Icon(Icons.add_rounded, color: Colors.white),
                label: Text('New Chat'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.white)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  minimumSize: const Size(double.infinity, 50),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const Divider(),
            Expanded(
              child: _sessions.isEmpty
                  ? Center(
                      child: Text(
                        'No chat history yet'.tr(context),
                        style: GoogleFonts.poppins(color: AppColors.textHint),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      itemCount: _sessions.length,
                      itemBuilder: (context, index) {
                        final session = _sessions[index];
                        final isSelected = session['id'] == _currentSessionId;
                        return Container(
                          margin: const EdgeInsets.symmetric(vertical: 4),
                          decoration: BoxDecoration(
                            color: isSelected 
                                ? (isDarkMode ? Colors.white10 : AppColors.primary.withOpacity(0.1))
                                : Colors.transparent,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: ListTile(
                            onTap: () {
                              Navigator.pop(context); // close drawer
                              _switchSession(session['id']!);
                            },
                            leading: Icon(
                              Icons.chat_bubble_outline_rounded,
                              color: isSelected ? AppColors.primary : AppColors.textHint,
                              size: 20,
                            ),
                            title: Text(
                              session['title'] ?? 'Chat',
                              style: GoogleFonts.poppins(
                                fontSize: 13.5,
                                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                                color: isSelected 
                                    ? AppColors.primary 
                                    : (isDarkMode ? Colors.white70 : AppColors.textPrimary),
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete_outline_rounded, size: 18, color: Colors.redAccent),
                              onPressed: () => _deleteSession(session['id']!),
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionChips() {
    final suggestions = [
      'Pest Control',
      'Irrigation Tips',
      'Fertilizer Advice',
      'Crop Rotation',
    ];
    return Container(
      height: 50,
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: suggestions.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ActionChip(
              label: Text(suggestions[index], style: GoogleFonts.poppins(fontSize: 12)),
              
              onPressed: _isTyping ? null : () {
                _controller.text = 'Tell me about ${suggestions[index]} for my farm.';
                _handleSendMessage();
              },
            ),
          );
        },
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      leading: Builder(
        builder: (context) => IconButton(
          icon: const Icon(Icons.menu_rounded, color: Colors.white),
          onPressed: () => Scaffold.of(context).openDrawer(),
        ),
      ),
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Kisan Mitra AI'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 18)),
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(color: Colors.green, shape: BoxShape.circle),
              ),
              const SizedBox(width: 4),
              Text('Online Assistant'.tr(context), style: GoogleFonts.poppins(fontSize: 11, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
            ],
          ),
        ],
      ),
      elevation: 1,
      actions: const [],
    );
  }

  Widget _buildChatBubble(ChatMessage message) {
    final isUser = message.isUser;
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            Container(
              margin: const EdgeInsets.only(bottom: 4),
              child: CircleAvatar(
                radius: 14,
                backgroundColor: AppColors.primary.withValues(alpha: 0.15),
                child: const Icon(Icons.auto_awesome, size: 14, color: AppColors.primary),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.85),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
              decoration: BoxDecoration(
                gradient: isUser ? AppColors.primaryGradient : null,
                color: isUser ? null : Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(22),
                  topRight: const Radius.circular(22),
                  bottomLeft: Radius.circular(isUser ? 22 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 22),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: isUser
                  ? Text(
                      message.text,
                      style: GoogleFonts.poppins(
                        color: Colors.white,
                        fontSize: 14,
                        height: 1.5,
                        fontWeight: FontWeight.w500,
                      ),
                    )
                  : MarkdownBody(
                      data: message.text,
                      styleSheet: MarkdownStyleSheet(
                        p: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface, fontSize: 14, height: 1.5),
                        h1: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface, fontSize: 18, fontWeight: FontWeight.bold),
                        h2: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface, fontSize: 16, fontWeight: FontWeight.bold),
                        h3: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface, fontSize: 15, fontWeight: FontWeight.bold),
                        listBullet: GoogleFonts.poppins(color: Theme.of(context).colorScheme.primary, fontSize: 16),
                        strong: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface, fontWeight: FontWeight.bold),
                      ),
                    ),
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            Container(
              margin: const EdgeInsets.only(bottom: 4),
              child: CircleAvatar(
                radius: 14,
                backgroundColor: Theme.of(context).cardColor,
                child: Icon(Icons.person, size: 14, color: Theme.of(context).colorScheme.primary),
              ),
            ),
          ],
        ],
      ),
    ).animate().fadeIn(duration: 400.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(color: Colors.black.withValues(alpha: 0.02), blurRadius: 5),
              ],
            ),
            child: Row(
              children: [
                Text(
                  'Kisan Mitra AI is thinking',
                  style: GoogleFonts.poppins(
                    fontSize: 12,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(width: 12),
                const SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn();
  }

  Widget _buildInputArea() {
    return Container(
      padding: EdgeInsets.fromLTRB(16, 12, 16, 12 + MediaQuery.of(context).padding.bottom),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.08),
            blurRadius: 20,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: AppColors.divider.withValues(alpha: 0.5)),
              ),
              child: TextField(
                controller: _controller,
                enabled: !_isTyping,
                style: GoogleFonts.poppins(fontSize: 14),
                decoration: InputDecoration(
                  hintText: _isTyping ? 'Waiting for response...' : 'Ask anything about your crops...',
                  hintStyle: TextStyle(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(vertical: 14),
                ),
                onSubmitted: _isTyping ? null : (_) => _handleSendMessage(),
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _isTyping ? null : _handleSendMessage,
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                gradient: _isTyping ? null : AppColors.primaryGradient,
                color: _isTyping ? Colors.grey[400] : null,
                shape: BoxShape.circle,
                boxShadow: _isTyping ? null : [
                  BoxShadow(
                    color: Theme.of(context).cardColor.withValues(alpha: 0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Icon(
                _isTyping ? Icons.hourglass_empty_rounded : Icons.send_rounded,
                color: Colors.white,
                size: 22,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.auto_awesome, size: 64, color: Colors.white),
          const SizedBox(height: 16),
          Text(
            'Kisan Mitra AI Assistant',
            style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Text(
              'Ask me about crops, fertilizers, pest control, or weather-based farming tips.',
              textAlign: TextAlign.center,
              style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
            ),
          ),
        ],
      ),
    );
  }
}
