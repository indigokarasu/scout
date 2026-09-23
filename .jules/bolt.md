## 2026-04-12 - Token Inverted Index for Entity Resolution Pass 3
**Learning:** $O(N \times M)$ pairwise string comparison in entity resolution token overlap re-runs full normalization and tokenization $2 \times N \times M$ times. Pre-tokenizing once and using a token inverted index reduces complexity to $O(N + M + \text{matches})$, achieving a ~27x speedup (~96% runtime reduction) while preserving exact output ordering.
**Action:** When performing Jaccard/token overlap across large datasets, pre-tokenize both sets and build an inverted index on candidate tokens before matching.

## 2026-04-12 - Binary Search for Nearest Date Distance in Monte Carlo Permutations
**Learning:** In Monte Carlo permutation tests (`timing_analysis.py`), finding nearest date distances via a linear scan over $K$ dates takes $O(K)$ per donation across thousands of iterations ($O(P \times D \times K)$). Sorting the date list once per permutation and using `bisect.bisect_left` reduces distance lookup to $O(\log K)$, speeding up permutation testing by ~5.35x.
**Action:** Always sort numeric/date arrays once in Monte Carlo simulations and use binary search (`bisect`) for distance or boundary lookups.
