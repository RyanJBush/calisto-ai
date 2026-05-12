# Retrieval Evaluation

Callisto ships with a labeled evaluation set under `data/samples/eval_set.json`
and a script (`scripts/evaluate_retrieval.py`) that scores retrieval quality
against the seeded sample documents.

## What is measured

For each query in the eval set, the script asks the retrieval service for
the top *k* chunks and computes:

| Metric | Definition |
|---|---|
| **Source hit rate** | Fraction of queries where at least one expected source document appears in the top-k results. |
| **Keyword coverage** | Fraction of expected keywords present in the concatenated retrieved chunks. |
| **Mean retrieval latency (ms)** | Wall-clock time per retrieval call, averaged across the eval set. |

These metrics are intentionally simple and reproducible without an LLM judge
or a paid evaluation service. They are useful for catching regressions when
the chunking strategy or embedding function changes.

## Running locally

```bash
# 1. Seed sample documents and start the API
make init
make run-backend &

# 2. From the repo root
python scripts/evaluate_retrieval.py
```

The script prints a summary table and exits non-zero if the source hit rate
drops below the threshold defined at the top of the script.

## Interpreting results

The default embedding implementation is a deterministic hash (see
`backend/app/services/embedding_service.py`), which exists so the demo runs
without external API keys. Under this configuration, the hybrid retriever
relies primarily on the keyword/metadata signals — semantic recall is
limited. Swapping in a real embedding model (e.g.
`sentence-transformers/all-MiniLM-L6-v2`) should materially improve the
source hit rate, and the eval script is the way to verify that.

## Known limitations

- The eval set is small (six queries). It demonstrates the methodology but
  is not a substitute for a production-scale benchmark such as MTEB or BEIR.
- There is no LLM-as-judge step for answer quality. The script only scores
  retrieval, not generation.
- Latency is measured in-process and does not reflect network round trip,
  cold-start, or external embedding-API latency.
