import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_strings.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/utils/app_utils.dart';
import '../../../../core/widgets/km_button.dart';
import '../../../../core/widgets/km_text_field.dart';
import '../../../../config/routes/app_router.dart';
import '../../../../core/services/auth_service.dart';
import '../../../../core/theme/app_theme.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = AuthService();
  
  bool _isLogin = true;
  bool _obscurePassword = true;
  bool _isLoading = false;
  int _registerStep = 0;
  bool _isPhoneRegistration = false;
  String? _generatedEmailOtp;
  Timer? _verificationTimer;

  final _otpController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnim = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeIn),
    );
    _slideAnim =
        Tween<Offset>(begin: const Offset(0, 0.1), end: Offset.zero).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeOutCubic),
    );
    _animController.forward();
    _passwordController.addListener(_onPasswordChanged);
  }

  void _onPasswordChanged() {
    if (!_isLogin && _registerStep == 2) {
      setState(() {});
    }
  }

  @override
  void dispose() {
    _verificationTimer?.cancel();
    _animController.dispose();
    _passwordController.removeListener(_onPasswordChanged);
    _emailController.dispose();
    _passwordController.dispose();
    _otpController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _startEmailVerificationTimer() {
    _verificationTimer?.cancel();
    _verificationTimer = Timer.periodic(const Duration(seconds: 3), (timer) async {
      bool isVerified = await _authService.checkEmailVerified();
      if (isVerified) {
        timer.cancel();
        if (mounted) {
          setState(() {
            _registerStep = 2;
            _isLoading = false;
          });
          AppUtils.showSnackBar(context, 'Email verified successfully!');
        }
      }
    });
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    try {
      String email = _emailController.text.trim();

      if (!_isLogin && _registerStep == 0) {
        _isPhoneRegistration = false;
        _generatedEmailOtp = await _authService.sendEmailOtpViaEmailJS(email);
        AppUtils.showSnackBar(context, 'Real 6-digit OTP sent to $email');
        if (mounted) {
          setState(() => _registerStep = 1);
        }
        return;
      }
      
      if (!_isLogin && _registerStep == 1) {
        String otp = _otpController.text.trim();
        if (_generatedEmailOtp != null && otp == _generatedEmailOtp) {
           if (mounted) setState(() => _registerStep = 2);
        } else {
           AppUtils.showSnackBar(context, 'Invalid OTP. Please try again.', isError: true);
        }
        return;
      }

      if (_isLogin) {
        await _authService.signInWithEmail(
          email,
          _passwordController.text.trim(),
        );
        if (mounted) await _proceedToHome();

      } else {
        // Register the user with Firebase now that OTP is verified
        await _authService.registerWithEmail(
          email,
          _passwordController.text.trim(),
        );
        if (mounted) {
          AppUtils.showSnackBar(context, 'Account created successfully!');
          context.go(AppRouter.profileSetup);
        }
      }
    } on FirebaseAuthException catch (e) {
      if (mounted) {
        String message = e.message ?? 'An error occurred. Please try again.';
        if (e.code == 'user-not-found') {
          message = 'No user found for that email.';
        } else if (e.code == 'wrong-password') {
          message = 'Wrong password provided.';
        } else if (e.code == 'email-already-in-use') {
          message = 'The account already exists.';
        } else if (e.code == 'weak-password') {
          message = 'The password provided is too weak.';
        } else if (e.code == 'invalid-verification-code') {
          message = 'Invalid SMS OTP.';
        }
        
        AppUtils.showSnackBar(context, message, isError: true);
      }
    } catch (e) {
      if (mounted) AppUtils.showSnackBar(context, 'Unexpected error: $e', isError: true);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _handleGoogleSignIn() async {
    setState(() => _isLoading = true);
    try {
      final userCreds = await _authService.signInWithGoogle();
      if (userCreds != null && mounted) {
        await _proceedToHome();
      }
    } catch (e) {
      if (mounted) AppUtils.showSnackBar(context, 'Google Sign-In failed: $e', isError: true);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _proceedToHome() async {
    if (mounted) {
      context.go(AppRouter.home);
    }
  }

  Future<void> _handleForgotPassword() async {
    final email = _emailController.text.trim();
    if (email.isEmpty || !email.contains('@')) {
      AppUtils.showSnackBar(context, 'Please enter your registered email address in the Email field first.', isError: true);
      return;
    }

    setState(() => _isLoading = true);
    try {
      await _authService.sendPasswordResetEmail(email);
      if (mounted) {
        AppUtils.showSnackBar(context, 'Password reset link sent to $email. Please check your inbox.');
      }
    } catch (e) {
      if (mounted) {
        AppUtils.showSnackBar(context, 'Failed to send reset link. Ensure this email is registered.', isError: true);
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.dark);
    final size = MediaQuery.of(context).size;

    return Scaffold(
      
      body: SingleChildScrollView(
        child: SizedBox(
          height: size.height,
          child: Column(
            children: [
              _buildHeader(size),
              Expanded(
                child: FadeTransition(
                  opacity: _fadeAnim,
                  child: SlideTransition(
                    position: _slideAnim,
                    child: Theme(
                      data: AppTheme.lightTheme,
                      child: Container(
                        width: double.infinity,
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
                        ),
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.fromLTRB(24, 32, 24, 24),
                        child: Form(
                          key: _formKey,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _isLogin ? AppStrings.welcomeBack : (_registerStep == 0 ? 'Create Account' : (_registerStep == 1 ? 'Verify OTP' : 'Set Password')),
                                style: GoogleFonts.poppins(
                                  fontSize: 26,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                _isLogin ? AppStrings.loginSubtitle : 'Join our community of modern farmers',
                                style: GoogleFonts.poppins(
                                  fontSize: 13,
                                  color: AppColors.textSecondary,
                                ),
                              ),
                              const SizedBox(height: 32),

                              if (_isLogin || (!_isLogin && _registerStep == 0))
                                KMTextField(
                                  label: 'Email',
                                  hint: 'name@example.com',
                                  controller: _emailController,
                                  prefixIcon: Icons.email_outlined,
                                  keyboardType: TextInputType.emailAddress,
                                  validator: (val) {
                                    if (val == null || val.trim().isEmpty) {
                                      return 'Email is required';
                                    }
                                    final input = val.trim();
                                    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
                                    if (!emailRegex.hasMatch(input)) {
                                      return 'Enter a valid email address';
                                    }
                                    return null;
                                  },
                                ),

                              if (!_isLogin && _registerStep == 1)
                                KMTextField(
                                  label: 'Enter Email OTP',
                                  hint: '123456',
                                  controller: _otpController,
                                  prefixIcon: Icons.mark_email_read_outlined,
                                  keyboardType: TextInputType.number,
                                  validator: (val) {
                                    if (val == null || val.isEmpty) return 'OTP is required';
                                    return null;
                                  },
                                ),

                              if (_isLogin || (!_isLogin && _registerStep == 2)) ...[
                                if (_isLogin) const SizedBox(height: 20),
                                KMTextField(
                                  label: _isLogin ? AppStrings.password : 'Create Password',
                                  hint: AppStrings.passwordHint,
                                  controller: _passwordController,
                                  prefixIcon: Icons.lock_outline_rounded,
                                  obscureText: _obscurePassword,
                                  textInputAction: _isLogin ? TextInputAction.done : TextInputAction.next,
                                  suffixIcon: IconButton(
                                    icon: Icon(
                                      _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                                      size: AppDimensions.iconSM,
                                    ),
                                    onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                                  ),
                                  validator: (val) {
                                    if (val == null || val.isEmpty) return AppStrings.passwordRequired;
                                    if (!_isLogin) {
                                      if (val.length < 8) return 'Password must be at least 8 characters';
                                      if (!val.contains(RegExp(r'[A-Z]')) || !val.contains(RegExp(r'[a-z]'))) {
                                        return 'Must contain both uppercase & lowercase letters';
                                      }
                                      if (!val.contains(RegExp(r'[0-9]'))) {
                                        return 'Must contain at least one number';
                                      }
                                      if (!val.contains(RegExp(r'[!@#\$&*~%]'))) {
                                        return 'Must contain at least one special character (!@#\$&*~%)';
                                      }
                                    } else {
                                      if (val.length < 6) return 'Password must be at least 6 characters';
                                    }
                                    return null;
                                  },
                                  onSubmitted: _isLogin ? (_) => _handleSubmit() : null,
                                ),
                                if (!_isLogin && _registerStep == 2)
                                  _buildPasswordCriteria(_passwordController.text),
                              ],

                              if (!_isLogin && _registerStep == 2) ...[
                                const SizedBox(height: 20),
                                KMTextField(
                                  label: 'Confirm Password',
                                  hint: 'Re-enter your password',
                                  controller: _confirmPasswordController,
                                  prefixIcon: Icons.lock_outline_rounded,
                                  obscureText: _obscurePassword,
                                  textInputAction: TextInputAction.done,
                                  validator: (val) {
                                    if (val == null || val.isEmpty) return 'Please confirm password';
                                    if (val != _passwordController.text) return 'Passwords do not match';
                                    return null;
                                  },
                                  onSubmitted: (_) => _handleSubmit(),
                                ),
                              ],
                              
                              if (_isLogin) ...[
                                const SizedBox(height: 12),
                                Align(
                                  alignment: Alignment.centerRight,
                                  child: TextButton(
                                    onPressed: _isLoading ? null : _handleForgotPassword,
                                    child: Text(
                                      AppStrings.forgotPassword,
                                      style: GoogleFonts.poppins(
                                        fontSize: 13,
                                        color: AppColors.primary,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                              
                              const SizedBox(height: 28),

                              KMButton(
                                label: _isLogin 
                                    ? AppStrings.login 
                                    : (_registerStep == 0 
                                        ? 'Verify' 
                                        : (_registerStep == 1 
                                            ? 'Check Status' 
                                            : 'Sign Up')),
                                onPressed: _handleSubmit,
                                isLoading: _isLoading,
                              ),
                              const SizedBox(height: 28),

                              if (_registerStep == 0 || _isLogin) ...[
                                Row(
                                  children: [
                                    const Expanded(child: Divider()),
                                    Padding(
                                      padding: const EdgeInsets.symmetric(horizontal: 16),
                                      child: Text(
                                        'Or continue with',
                                        style: GoogleFonts.poppins(fontSize: 13, color: AppColors.textSecondary),
                                      ),
                                    ),
                                    const Expanded(child: Divider()),
                                  ],
                                ),
                                const SizedBox(height: 24),
                                OutlinedButton(
                                  onPressed: _isLoading ? null : _handleGoogleSignIn,
                                  style: OutlinedButton.styleFrom(
                                    padding: const EdgeInsets.symmetric(vertical: 14),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                    side: BorderSide(color: Colors.grey.shade300),
                                  ),
                                  child: Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Image.network(
                                        'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/120px-Google_%22G%22_logo.svg.png',
                                        height: 24,
                                        errorBuilder: (context, error, stackTrace) => 
                                            const Icon(Icons.g_mobiledata, size: 32, color: Colors.blue),
                                      ),
                                      const SizedBox(width: 12),
                                      Text(
                                        'Google',
                                        style: GoogleFonts.poppins(
                                          fontSize: 15,
                                          fontWeight: FontWeight.w600,
                                          color: AppColors.textPrimary,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(height: 24),
                              ],

                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    _isLogin ? AppStrings.dontHaveAccount : 'Already have an account? ',
                                    style: GoogleFonts.poppins(fontSize: 13, color: AppColors.textSecondary),
                                  ),
                                  TextButton(
                                    onPressed: () => setState(() {
                                      _isLogin = !_isLogin;
                                      _registerStep = 0;
                                    }),
                                    style: TextButton.styleFrom(
                                      padding: EdgeInsets.zero,
                                      minimumSize: const Size(50, 30),
                                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                    ),
                                    child: Text(
                                      _isLogin ? AppStrings.register : 'Login',
                                      style: GoogleFonts.poppins(
                                        fontSize: 13,
                                        color: AppColors.primary,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPasswordCriteria(String password) {
    final hasMinLength = password.length >= 8;
    final hasUpperLower = password.contains(RegExp(r'[A-Z]')) && password.contains(RegExp(r'[a-z]'));
    final hasNumber = password.contains(RegExp(r'[0-9]'));
    final hasSpecial = password.contains(RegExp(r'[!@#\$&*~%]'));

    Widget criteriaRow(String label, bool isValid) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 2),
        child: Row(
          children: [
            Icon(
              isValid ? Icons.check_circle_rounded : Icons.cancel_rounded,
              color: isValid ? Colors.green.shade600 : Colors.grey.shade400,
              size: 16,
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: GoogleFonts.poppins(
                fontSize: 12,
                color: isValid ? Colors.green.shade800 : AppColors.textSecondary,
                fontWeight: isValid ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      margin: const EdgeInsets.only(top: 8, bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Password Requirements:',
            style: GoogleFonts.poppins(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 6),
          criteriaRow('At least 8 characters', hasMinLength),
          criteriaRow('Both uppercase & lowercase letters', hasUpperLower),
          criteriaRow('At least one number (0-9)', hasNumber),
          criteriaRow('At least one special character (!@#\$&*~%)', hasSpecial),
        ],
      ),
    );
  }

  Widget _buildHeader(Size size) {
    return Container(
      width: double.infinity,
      height: size.height * 0.28,
      decoration: const BoxDecoration(gradient: AppColors.splashGradient),
      child: Stack(
        children: [
          SafeArea(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 72,
                    height: 72,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.15),
                          blurRadius: 20,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: const Icon(Icons.eco_rounded, size: 40, color: AppColors.primary),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    AppStrings.appName,
                    style: GoogleFonts.poppins(
                      fontSize: 24,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

}
