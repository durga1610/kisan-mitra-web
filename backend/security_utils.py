"""
security_utils.py
-----------------
Shared security helpers for the Kisan Mitra backend.

Provides safe_pickle_load() which computes a SHA-256 digest of a model file
before deserializing it. This defends against supply-chain attacks where an
attacker gains write access to the models/ directory and replaces a legitimate
.pkl with a malicious one containing __reduce__ RCE payloads (CWE-502 / F-05).

Usage
-----
# Warn-only (empty hash table — suitable for first run / development):
obj = safe_pickle_load("/path/to/model.pkl")

# Enforcing mode (add known digests after first trusted build):
obj = safe_pickle_load("/path/to/model.pkl", known_hashes=KNOWN_MODEL_HASHES)
"""

import hashlib
import logging
import os
import pickle

logger = logging.getLogger(__name__)

# ── Known SHA-256 digests for model files ──────────────────────────────────
# Populate these after your first trusted build by running:
#   python -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" models/farming_domain_classifier.pkl
#
# Leave a value as "" to run in warn-only mode for that file.
KNOWN_MODEL_HASHES: dict[str, str] = {
    "farming_domain_classifier.pkl": "b37c27dd024bdb94c682e429e91c5710415628e72d2afe228d61af141a77511a",
    "crop_recommendation_model.pkl": "12ddc2eea2f41ed101aaf5753a8a4604c4019b49e09a30453ea17a387b4483ff",
    "crop_recommendation_preprocessors.pkl": "36ce952582ca52883e271b6f24e0fbaa7e45f8e899c71cb754fa268d24b750a0",
    "crop_suitability_preprocessors.pkl": "78cf54a45ac38ff251e102e6be70cacaf44f1c449cd936659aba242f90b1782b",
    "crop_suitability_model.pkl": "02284c5fa7c4e1304ea51154ee710cd2a42b4f8a4456e7050b25906d8395532f",
}


def safe_pickle_load(path: str, known_hashes: dict[str, str] | None = None) -> object:
    """
    Load a pickle file after verifying its SHA-256 digest.

    Parameters
    ----------
    path : str
        Absolute or relative path to the .pkl file.
    known_hashes : dict, optional
        Mapping of basename → expected SHA-256 hex digest.
        Defaults to the module-level KNOWN_MODEL_HASHES.
        If the expected digest for a file is "" or absent, a warning is logged
        but loading proceeds (warn-only mode).
        If the digest is non-empty and does NOT match, a RuntimeError is raised.

    Returns
    -------
    object
        The deserialized Python object.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    RuntimeError
        If the file's digest does not match the expected hash (enforcing mode).
    """
    if known_hashes is None:
        known_hashes = KNOWN_MODEL_HASHES

    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")

    fname = os.path.basename(path)

    with open(path, "rb") as f:
        data = f.read()

    actual_digest = hashlib.sha256(data).hexdigest()
    expected_digest = known_hashes.get(fname, "")

    if expected_digest:
        if actual_digest != expected_digest:
            raise RuntimeError(
                f"[SECURITY] Integrity check FAILED for '{fname}'. "
                f"Expected sha256={expected_digest}, got sha256={actual_digest}. "
                "The model file may have been tampered with — refusing to load."
            )
        logger.info("Integrity check PASSED for '%s' (sha256=%s)", fname, actual_digest)
    else:
        logger.warning(
            "Integrity check SKIPPED for '%s' (no known hash configured). "
            "Add sha256=%s to KNOWN_MODEL_HASHES to enable enforcing mode.",
            fname,
            actual_digest,
        )

    return pickle.loads(data)  # noqa: S301 — integrity checked above
