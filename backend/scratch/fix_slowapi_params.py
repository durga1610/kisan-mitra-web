"""
fix_slowapi_params.py — fix two issues in main.py after security hardening:

1. slowapi requires the starlette Request parameter to be named exactly `request`.
   We renamed it `http_request` and gave `request` to the Pydantic body, causing:
   "parameter `request` must be an instance of starlette.requests.Request"
   Fix: swap names — starlette Request stays `request`, Pydantic body becomes `body`.

2. Pydantic v2 deprecates `strip_whitespace` on Field(); remove it.
"""
import re

with open("main.py", "r", encoding="utf-8") as f:
    src = f.read()

# ── 1. Fix endpoint signatures ────────────────────────────────────────────
# Replace:  (http_request: Request, request: XxxRequest, user: Dict = Depends(verify_token))
# With:     (request: Request, body: XxxRequest, user: Dict = Depends(verify_token))
src = src.replace(
    "def chat_advisory(http_request: Request, request: ChatRequest, user: Dict = Depends(verify_token)):",
    "def chat_advisory(request: Request, body: ChatRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "async def generate_advisory(http_request: Request, request: AdvisoryRequest, user: Dict = Depends(verify_token)):",
    "async def generate_advisory(request: Request, body: AdvisoryRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "async def predict_crop_recommendation(http_request: Request, request: CropRecommendationPredictRequest, user: Dict = Depends(verify_token)):",
    "async def predict_crop_recommendation(request: Request, body: CropRecommendationPredictRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "async def generate_recommendations(http_request: Request, request: RecommendationRequest, user: Dict = Depends(verify_token)):",
    "async def generate_recommendations(request: Request, body: RecommendationRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "async def check_suitability(http_request: Request, request: SuitabilityRequest, user: Dict = Depends(verify_token)):",
    "async def check_suitability(request: Request, body: SuitabilityRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "async def generate_daily_guidance(http_request: Request, request: GuidanceRequest, user: Dict = Depends(verify_token)):",
    "async def generate_daily_guidance(request: Request, body: GuidanceRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "async def generate_reasoning(http_request: Request, request: ReasoningRequest, user: Dict = Depends(verify_token)):",
    "async def generate_reasoning(request: Request, body: ReasoningRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "async def recommend_fertilizer(http_request: Request, request: FertilizerRecommendRequest, user: Dict = Depends(verify_token)):",
    "async def recommend_fertilizer(request: Request, body: FertilizerRecommendRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "async def validate_crop_before_planting(http_request: Request, request: CropValidationRequest, user: Dict = Depends(verify_token)):",
    "async def validate_crop_before_planting(request: Request, body: CropValidationRequest, user: Dict = Depends(verify_token)):"
)
src = src.replace(
    "    http_request: Request,\n    request: AuditLogRequest,\n    user: Dict = Depends(verify_token),\n):",
    "    request: Request,\n    body: AuditLogRequest,\n    user: Dict = Depends(verify_token),\n):"
)

# ── 2. Rename body usages inside each function  ───────────────────────────
# We need to rename `request.X` -> `body.X` ONLY inside the affected function
# bodies. We use a function-boundary approach: split on @app.post blocks and
# fix each affected block individually.

BODY_FIELDS = [
    # chat_advisory
    "request.message", "request.language", "request.farm",
    # generate_advisory
    "request.crop", "request.soil", "request.location", "request.weather",
    # predict_crop_recommendation / generate_recommendations
    "request.availableMarketCrops",
    # check_suitability / suitability
    "request.cropName",
    # generate_daily_guidance
    "request.cropAgeDays", "request.soilType", "request.waterAvailability",
    "request.temperature", "request.humidity", "request.rainfallForecast",
    "request.weatherCondition", "request.plantingDate", "request.state",
    # generate_reasoning
    "request.marketTrend",
    # fertilizer / validation
    "request.farmId", "request.cropId", "request.plantedDate",
    # audit-log
    "request.cropName", "request.suitabilityScore", "request.reasons", "request.ignoredWarning",
]

# Split into @app.post/@app.get blocks and process each that has a `body: Xxx` param
segments = re.split(r'(?=@app\.(?:post|get)\()', src)
fixed_segments = []
for seg in segments:
    # Only rename in blocks where we renamed the signature to use `body:`
    if "body: " in seg and "def " in seg:
        for field in BODY_FIELDS:
            # Replace `request.X` with `body.X` in this segment only
            seg = seg.replace(field, field.replace("request.", "body."))
    fixed_segments.append(seg)

src = "".join(fixed_segments)

# ── 3. Fix Pydantic v2 deprecated strip_whitespace on Field() ─────────────
src = src.replace(
    "Field(..., min_length=1, max_length=2000, strip_whitespace=True)",
    "Field(..., min_length=1, max_length=2000)"
)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(src)

print("main.py: slowapi parameter rename and Pydantic fix applied.")

# ── 4. Fix conftest.py: enable filename bypass + set APP_ENV for tests ────
conftest = open("conftest.py", "r", encoding="utf-8").read()

if "KISAN_ALLOW_FILENAME_BYPASS" not in conftest:
    # Insert env var setup before the main import
    conftest = conftest.replace(
        "from main import app, verify_token",
        (
            "import os\n"
            "# Enable filename bypass so tests that rely on filename-based disease\n"
            "# matching (e.g. apple_scab.jpg) continue to work (F-09 gate is off\n"
            "# by default in production; tests run in development mode).\n"
            "os.environ.setdefault(\"KISAN_ALLOW_FILENAME_BYPASS\", \"1\")\n"
            "os.environ.setdefault(\"APP_ENV\", \"development\")\n"
            "\n"
            "from main import app, verify_token"
        )
    )
    with open("conftest.py", "w", encoding="utf-8") as f:
        f.write(conftest)
    print("conftest.py: added KISAN_ALLOW_FILENAME_BYPASS=1 env setup.")
else:
    print("conftest.py: already has bypass env var, skipping.")
