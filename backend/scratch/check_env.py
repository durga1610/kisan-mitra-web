import os
import json

keys = sorted(list(os.environ.keys()))
print("Available Environment Variable Keys:")
for key in keys:
    # Mask values for security
    val = os.environ[key]
    masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "..."
    print(f"- {key}: {masked}")
