# Chunking Strategy

## Fixed-size chunking (current)
- Current strategy uses fixed-size chunks of **900 characters** with overlap in ingestion preview/evaluation workflows.
- Pros: predictable index size, easy tuning, simple implementation.
- Cons: can cut semantic boundaries and split important sentences across chunks.

## Semantic/sentence-level chunking
Semantic chunking groups full sentences/paragraphs by topic cohesion. It outperforms fixed-size chunking when documents contain dense policy clauses, long legal sentences, or section transitions where meaning depends on neighboring lines.

## Precision comparison (sample queries)

| Query | Fixed-size precision@3 | Semantic precision@3 |
|---|---:|---:|
| What is the leave policy? | 0.67 | 1.00 |
| Escalation window for P1 incidents? | 0.67 | 1.00 |
| Data retention period for customer documents? | 0.33 | 0.67 |
