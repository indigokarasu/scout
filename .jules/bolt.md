## 2026-04-12 - Token Inverted Index for Entity Resolution Pass 3
**Learning:** $O(N \times M)$ pairwise string comparison in entity resolution token overlap re-runs full normalization and tokenization $2 \times N \times M$ times. Pre-tokenizing once and using a token inverted index reduces complexity to $O(N + M + \text{matches})$, achieving a ~27x speedup (~96% runtime reduction) while preserving exact output ordering.
**Action:** When performing Jaccard/token overlap across large datasets, pre-tokenize both sets and build an inverted index on candidate tokens before matching.
