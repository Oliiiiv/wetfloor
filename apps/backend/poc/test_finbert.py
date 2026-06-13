"""
Phase 0 De-risk Script: FinBERT Local Inference
================================================

Goal: Verify FinBERT (ProsusAI/finbert) runs on the local machine with
      acceptable latency for the Smart Homepage's "personalized news"
      use case (PLAN.md §5.3).

Why this matters:
  - On the Smart Homepage we'll classify hundreds of news headlines per
    user per day. If single-headline latency is > ~200 ms on CPU, we
    need GPU or a smaller model.
  - First run downloads ~440 MB; subsequent runs use the HF cache
    (~/.cache/huggingface).

Run (recommended — uv handles the venv for you):

    cd apps/backend
    uv venv
    uv pip install -r poc/requirements-finbert.txt
    uv run python -m poc.test_finbert

Or with plain pip:

    cd apps/backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r poc/requirements-finbert.txt
    python -m poc.test_finbert
"""
from __future__ import annotations

import statistics
import time

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_NAME = "ProsusAI/finbert"

# A spread of headlines designed to hit each FinBERT label (positive,
# negative, neutral) and exercise a few common financial phrasings.
SAMPLE_HEADLINES: list[str] = [
    "Apple beats Q4 earnings expectations, stock soars 8%",
    "Federal Reserve hints at rate cuts amid recession fears",
    "Tesla recalls 2 million vehicles over autopilot safety concerns",
    "NVIDIA announces record-breaking AI chip sales, beating estimates",
    "Oil prices plunge as OPEC+ fails to reach production agreement",
    "Bitcoin surges to new all-time high above $100,000",
    "Microsoft signs $10B AI deal with OpenAI",
    "Amazon announces 10,000 layoffs amid cost-cutting measures",
    "Boeing 737 MAX faces new safety probe after door incident",
    "Walmart raises Q4 outlook on strong holiday sales",
]


def detect_device() -> tuple[str, str]:
    """Pick the fastest available device. On Apple Silicon we use MPS."""
    if torch.backends.mps.is_available():
        return "mps", "Apple Silicon GPU (MPS)"
    if torch.cuda.is_available():
        return "cuda", f"NVIDIA GPU ({torch.cuda.get_device_name(0)})"
    return "cpu", "CPU"


def main() -> int:
    print()
    print("=" * 72)
    print("  CautiousWetfloor — Phase 0 De-risk: FinBERT Local Inference")
    print("=" * 72)

    device, device_desc = detect_device()
    print(f"PyTorch: {torch.__version__}")
    print(f"Device:  {device_desc}")
    print()

    print(f"Loading {MODEL_NAME} ...")
    t0 = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.to(device)
    model.eval()
    t_load = time.perf_counter() - t0
    print(f"  Loaded in {t_load:.1f}s")
    # FinBERT's label mapping comes from the model config.
    id2label = model.config.id2label  # {0: 'positive', 1: 'negative', 2: 'neutral'}
    print(f"  Labels:  {id2label}")
    print()

    # ----------------------------------------------------------------------
    # Single-headline inference: measures the "per item" latency that the
    # Smart Homepage will see when streaming news in real time.
    # ----------------------------------------------------------------------
    print(f"Single-headline inference on {len(SAMPLE_HEADLINES)} samples")
    print("-" * 72)
    print(f"  {'Sentiment':<10s} {'Conf':>5s}   Headline")
    print("-" * 72)

    latencies_ms: list[float] = []
    # Warm-up pass (first inference includes graph compilation / JIT, which
    # would skew the first sample).
    with torch.no_grad():
        _ = model(**{k: v.to(device) for k, v in tokenizer("warmup", return_tensors="pt").items()})

    for headline in SAMPLE_HEADLINES:
        t = time.perf_counter()
        inputs = tokenizer(headline, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        label_idx = int(probs.argmax().item())
        confidence = float(probs[label_idx].item())
        elapsed_ms = (time.perf_counter() - t) * 1000
        latencies_ms.append(elapsed_ms)

        label = id2label.get(label_idx, str(label_idx)).upper()
        display = headline if len(headline) <= 55 else headline[:52] + "..."
        print(f"  {label:<10s} {confidence:>5.2f}   {display}")

    avg_ms = statistics.mean(latencies_ms)
    p50_ms = statistics.median(latencies_ms)
    p95_ms = sorted(latencies_ms)[int(len(latencies_ms) * 0.95)]
    print("-" * 72)
    print()
    print("Single-item latency:")
    print(f"  avg  = {avg_ms:6.1f} ms")
    print(f"  p50  = {p50_ms:6.1f} ms")
    print(f"  p95  = {p95_ms:6.1f} ms")
    print()

    # ----------------------------------------------------------------------
    # Batch inference: measures throughput when the worker catches up on a
    # backlog (e.g. first run of the day pulling overnight news).
    # ----------------------------------------------------------------------
    batch_size = len(SAMPLE_HEADLINES)
    print(f"Batch inference (batch_size = {batch_size})")
    t = time.perf_counter()
    inputs = tokenizer(
        SAMPLE_HEADLINES,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        _ = model(**inputs)
    batch_ms = (time.perf_counter() - t) * 1000
    print(f"  {batch_size} headlines in {batch_ms:.0f} ms")
    print(f"  per-item amortised: {batch_ms / batch_size:.1f} ms")
    print()

    # ----------------------------------------------------------------------
    # Pass / warn / fail
    # ----------------------------------------------------------------------
    print("=" * 72)
    if avg_ms < 200:
        verdict = "[PASS]"
        msg = "FinBERT inference latency is acceptable for real-time use."
    elif avg_ms < 500:
        verdict = "[WARN]"
        msg = "Latency OK for batch use; consider batching for real-time UX."
    else:
        verdict = "[FAIL]"
        msg = "Latency too high — try GPU / MPS, smaller model, or distillation."
    print(f"  {verdict} De-risk Task 2 — {msg}")
    print("=" * 72)
    print()
    print("Next steps:")
    print("  - Record findings (device, load time, latency) in docs/DERISK_LOG.md")
    print("  - Move on to Task 5 (FastAPI + Next.js scaffold)")
    print()
    return 0 if verdict != "[FAIL]" else 1


if __name__ == "__main__":
    raise SystemExit(main())
