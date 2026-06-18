// Mock JS library to allow compiling dart:js calls on mobile platforms.
class MockJsContext {
  dynamic operator [](Object key) => null;
  void operator []=(Object key, dynamic value) {}
  dynamic callMethod(String method, [List? args]) => null;
}

final context = MockJsContext();
