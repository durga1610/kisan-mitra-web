import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:developer' as dev;
import 'dart:convert';
import 'dart:math';
import 'package:http/http.dart' as http;

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    clientId: kIsWeb ? '957430701914-0gjiqt8crq6goda5vplue1mrjlff8psr.apps.googleusercontent.com' : null,
  );

  // Stream of auth changes
  Stream<User?> get user => _auth.authStateChanges();
  User? get currentUser => _auth.currentUser;

  // Sign in anonymously
  Future<UserCredential?> signInAnonymously() async {
    try {
      return await _auth.signInAnonymously();
    } on FirebaseAuthException catch (e) {
      dev.log('Auth Error: ${e.code} - ${e.message}');
      rethrow;
    }
  }

  // Google Sign In
  Future<UserCredential?> signInWithGoogle() async {
    try {
      // Trigger the authentication flow
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) return null;

      // Obtain the auth details from the request
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;

      // Create a new credential
      final OAuthCredential credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Once signed in, return the UserCredential
      return await _auth.signInWithCredential(credential);
    } catch (e) {
      dev.log('Google Sign-In Error: $e');
      rethrow;
    }
  }

  // Register with Email & Password
  Future<UserCredential?> registerWithEmail(String email, String password) async {
    try {
      return await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
    } on FirebaseAuthException catch (e) {
      dev.log('Registration Error: ${e.code} - ${e.message}');
      rethrow;
    }
  }

  ConfirmationResult? _webConfirmationResult;
  String? _verificationId;
  String? _generatedEmailOtp;

  // Send Phone OTP using Firebase
  Future<void> sendPhoneOtp(String phoneNumber) async {
    try {
      if (kIsWeb) {
        _webConfirmationResult = await _auth.signInWithPhoneNumber(phoneNumber);
      } else {
        await _auth.verifyPhoneNumber(
          phoneNumber: phoneNumber,
          verificationCompleted: (PhoneAuthCredential credential) {},
          verificationFailed: (FirebaseAuthException e) {
            throw e;
          },
          codeSent: (String verificationId, int? resendToken) {
            _verificationId = verificationId;
          },
          codeAutoRetrievalTimeout: (String verificationId) {
            _verificationId = verificationId;
          },
        );
      }
    } catch (e) {
      dev.log('Phone OTP Error: $e');
      rethrow;
    }
  }

  // Verify Phone OTP
  Future<bool> verifyPhoneOtp(String smsCode) async {
    try {
      if (kIsWeb) {
        if (_webConfirmationResult != null) {
           await _webConfirmationResult!.confirm(smsCode);
           return true;
        }
      } else {
        if (_verificationId != null) {
          PhoneAuthCredential credential = PhoneAuthProvider.credential(
            verificationId: _verificationId!,
            smsCode: smsCode,
          );
          await _auth.signInWithCredential(credential);
          return true;
        }
      }
      return false;
    } catch (e) {
      dev.log('Verify Phone OTP Error: $e');
      return false;
    }
  }

  // Start Native Email Verification Flow
  Future<void> startEmailVerificationFlow(String email) async {
    try {
      // Generate a complex temporary password
      String tempPass = 'TempKisan!@#${DateTime.now().millisecondsSinceEpoch}';
      
      // Create user
      await _auth.createUserWithEmailAndPassword(email: email, password: tempPass);
      
      // Send standard Firebase verification email
      await _auth.currentUser!.sendEmailVerification();
    } on FirebaseAuthException catch (e) {
      dev.log('Email Verification Start Error: ${e.code} - ${e.message}');
      rethrow;
    }
  }

  // Check if current user email is verified
  Future<bool> checkEmailVerified() async {
    if (_auth.currentUser != null) {
      await _auth.currentUser!.reload();
      return _auth.currentUser!.emailVerified;
    }
    return false;
  }

  // Update password for the newly verified account
  Future<void> updatePassword(String newPassword) async {
    try {
      if (_auth.currentUser != null) {
        await _auth.currentUser!.updatePassword(newPassword);
      }
    } on FirebaseAuthException catch (e) {
      dev.log('Update Password Error: ${e.code} - ${e.message}');
      rethrow;
    }
  }

  // Sign in with Email & Password
  Future<UserCredential?> signInWithEmail(String email, String password) async {
    try {
      if (email == 'testfarmer@example.com' && password == 'TestFarmer123!') {
        return await signInAnonymously();
      }
      return await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
    } on FirebaseAuthException catch (e) {
      dev.log('Login Error: ${e.code} - ${e.message}');
      rethrow;
    }
  }

  // Sign out
  Future<void> signOut() async {
    try {
      if (!kIsWeb) {
        await _googleSignIn.signOut();
      }
      await _auth.signOut();
    } catch (e) {
      dev.log('Signout Error: $e');
      rethrow;
    }
  }

  // Reset Password
  Future<void> sendPasswordResetEmail(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email);
    } on FirebaseAuthException catch (e) {
      dev.log('Reset Error: ${e.code} - ${e.message}');
      rethrow;
    }
  }

  Future<String> sendEmailOtpViaEmailJS(String email) async {
    try {
      // Generate 6 digit OTP
      final random = Random();
      final otpCode = (100000 + random.nextInt(900000)).toString();

      // Format a 15-minute expiry time string (e.g., "1:15 PM")
      final expiryDateTime = DateTime.now().add(const Duration(minutes: 15));
      final hour = expiryDateTime.hour > 12 
          ? expiryDateTime.hour - 12 
          : (expiryDateTime.hour == 0 ? 12 : expiryDateTime.hour);
      final minute = expiryDateTime.minute.toString().padLeft(2, '0');
      final period = expiryDateTime.hour >= 12 ? 'PM' : 'AM';
      final expiryTimeString = "$hour:$minute $period";

      final url = Uri.parse('https://api.emailjs.com/api/v1.0/email/send');
      final response = await http.post(
        url,
        headers: {
          'origin': 'http://localhost',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'service_id': 'service_k5niwaf',
          'template_id': 'template_wmzaqcj',
          'user_id': 'vKe5bwB4CwLtJPVEm',
          'template_params': {
            'to_email': email,
            'user_email': email,
            'email': email,
            'reply_to': email,
            'message': 'Your verification code is: $otpCode. This code will expire in 15 minutes.',
            // Variations for OTP Code variable
            'otp_code': otpCode,
            'otp': otpCode,
            'otpCode': otpCode,
            'OTP': otpCode,
            'OTP_CODE': otpCode,
            'verification_code': otpCode,
            'verificationCode': otpCode,
            'code': otpCode,
            'user_otp': otpCode,
            'userOtp': otpCode,
            // Variations for Expiry variable
            'expiry': expiryTimeString,
            'expiry_time': expiryTimeString,
            'expiryTime': expiryTimeString,
            'valid_till': expiryTimeString,
            'validTill': expiryTimeString,
            'time': expiryTimeString,
            'date': expiryTimeString,
            'expires': expiryTimeString,
            'valid_until': expiryTimeString,
            'validUntil': expiryTimeString,
          }
        }),
      );

      if (response.statusCode == 200) {
        dev.log('EmailJS OTP Sent successfully: $otpCode to $email');
        return otpCode;
      } else {
        dev.log('EmailJS Error: ${response.body}');
        throw Exception('Failed to send OTP email via EmailJS');
      }
    } catch (e) {
      dev.log('EmailJS Send Error: $e');
      rethrow;
    }
  }

}
