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

class AIAdvisoryScreen extends StatefulWidget {
  const AIAdvisoryScreen({super.key});

  @override
  State<AIAdvisoryScreen> createState() => _AIAdvisoryScreenState();
}

class _AIAdvisoryScreenState extends State<AIAdvisoryScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  late final GeminiService _geminiService;
  final List<ChatMessage> _messages = [];
  bool _isTyping = false;

  @override
  void initState() {
    super.initState();
    final farmProvider = Provider.of<FarmProvider>(context, listen: false);
    final lang = Provider.of<LanguageProvider>(context, listen: false).currentLanguage;
    _geminiService = GeminiService(selectedFarm: farmProvider.selectedFarm, languageCode: lang);
    _loadChatHistory();
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadChatHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getString('ai_chat_history');
      if (historyJson != null) {
        final List<dynamic> decoded = jsonDecode(historyJson);
        setState(() {
          _messages.addAll(decoded.map((m) => ChatMessage.fromMap(m)).toList());
        });
        _scrollToBottom();
      } else {
        // Add welcome message
        setState(() {
          _messages.add(ChatMessage(
            text: 'Hello! I am Kisan Mitra AI. How can I help you with your farming today?',
            isUser: false,
            timestamp: DateTime.now(),
          ));
        });
      }
    } catch (e) {
      debugPrint('Error loading chat history: $e');
    }
  }

  Future<void> _saveChatHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = jsonEncode(_messages.map((m) => m.toMap()).toList());
      await prefs.setString('ai_chat_history', historyJson);
    } catch (e) {
      debugPrint('Error saving chat history: $e');
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
            text: 'I am sorry, something went wrong. Please check your internet connection and API key.',
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
    return Scaffold(
      
      appBar: _buildAppBar(),
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
              
              onPressed: () {
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
      actions: [
        IconButton(
          icon: const Icon(Icons.delete_sweep_outlined, color: AppColors.error),
          onPressed: () async {
            final confirmed = await showDialog<bool>(
              context: context,
              builder: (context) => AlertDialog(
                title: Text('Clear Chat'.tr(context)),
                content: Text('Are you sure you want to clear all chat history?'.tr(context)),
                actions: [
                  TextButton(onPressed: () => Navigator.pop(context, false), child: Text('Cancel'.tr(context))),
                  TextButton(onPressed: () => Navigator.pop(context, true), child: Text('Clear'.tr(context), style: TextStyle(color: Colors.red))),
                ],
              ),
            );
            if (confirmed == true) {
              final prefs = await SharedPreferences.getInstance();
              await prefs.remove('ai_chat_history');
              setState(() {
                _messages.clear();
                _messages.add(ChatMessage(
                  text: 'History cleared. How can I help you today?',
                  isUser: false,
                  timestamp: DateTime.now(),
                ));
              });
            }
          },
        ),
      ],
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
                style: GoogleFonts.poppins(fontSize: 14),
                decoration: InputDecoration(
                  hintText: 'Ask anything about your crops...',
                  hintStyle: TextStyle(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(vertical: 14),
                ),
                onSubmitted: (_) => _handleSendMessage(),
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _handleSendMessage,
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                gradient: AppColors.primaryGradient,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Theme.of(context).cardColor.withValues(alpha: 0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Icon(Icons.send_rounded, color: Colors.white, size: 22),
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
