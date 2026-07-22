import sys
import os
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

log_path = os.path.join(BASE_DIR, "..", "scratch", "api_debug.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

try:
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("Starting test_e2e_local_rag_chat_integration...\n")

    from test_local_rag_api_integration import test_e2e_local_rag_chat_integration
    test_e2e_local_rag_chat_integration()

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\nSUCCESSFUL COMPLETION!\n")

except Exception as e:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\nEXCEPTION: {e}\n")
        f.write(traceback.format_exc())
    sys.exit(1)
