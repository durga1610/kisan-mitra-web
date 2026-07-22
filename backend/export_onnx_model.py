import os
import sys
import io

# Force UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel

# Base path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "models", "vector_db")
ONNX_MODEL_PATH = os.path.join(VECTOR_DB_DIR, "all-MiniLM-L6-v2.onnx")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class MiniLMONNXWrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask, token_type_ids):
        out = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )
        return out.last_hidden_state


def export_minilm_to_onnx():
    """
    Exports sentence-transformers/all-MiniLM-L6-v2 to ONNX format for ultra-lightweight CPU inference.
    """
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    print(f"[ONNX Exporter] Loading '{MODEL_NAME}' PyTorch model & tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    base_model = AutoModel.from_pretrained(MODEL_NAME)
    base_model.eval()

    # Save tokenizer files locally for offline load
    tokenizer.save_pretrained(VECTOR_DB_DIR)

    wrapper_model = MiniLMONNXWrapper(base_model)
    wrapper_model.eval()

    # Dummy inputs for ONNX export
    dummy_text = "How to grow rice in alluvial soil"
    dummy_inputs = tokenizer(
        [dummy_text],
        padding="max_length",
        truncation=True,
        max_length=128,
        return_tensors="pt"
    )

    input_names = ["input_ids", "attention_mask", "token_type_ids"]
    output_names = ["last_hidden_state"]
    dynamic_axes = {
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        "attention_mask": {0: "batch_size", 1: "sequence_length"},
        "token_type_ids": {0: "batch_size", 1: "sequence_length"},
        "last_hidden_state": {0: "batch_size", 1: "sequence_length"},
    }

    print(f"[ONNX Exporter] Exporting ONNX model to '{ONNX_MODEL_PATH}'...")
    torch.onnx.export(
        wrapper_model,
        (dummy_inputs["input_ids"], dummy_inputs["attention_mask"], dummy_inputs["token_type_ids"]),
        ONNX_MODEL_PATH,
        input_names=input_names,
        output_names=output_names,
        dynamic_axes=dynamic_axes,
        opset_version=14,
        do_constant_folding=True,
        dynamo=False,
    )

    file_size_mb = os.path.getsize(ONNX_MODEL_PATH) / (1024 * 1024)
    print(f"[ONNX Exporter] Successfully exported ONNX model ({file_size_mb:.2f} MB)!")


if __name__ == "__main__":
    try:
        export_minilm_to_onnx()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
