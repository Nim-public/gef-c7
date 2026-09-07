# BLEU by Hand — N-gram Precision, Brevity Penalty, Clipping

**What you'll learn:** implement BLEU from the paper, including the two
mechanisms that make it non-trivial (clipping and the brevity penalty), and
name exactly when BLEU lies.

## 1. The definition, mechanically

For candidate caption C against N references S₁…S_N:

- **pₙ** = modified n-gram precision: clipped matches over candidate n-grams.
- **BP** = brevity penalty: `1 if c > r else exp(1 − r/c)` where c = candidate
  length, r = *effective* reference length.
- **BLEU** = `BP · exp(Σ wₙ log pₙ)`, wₙ = 1/4 for n = 1..4.

"Effective reference length" for multiple references: the reference whose
length is closest to c (tie → shorter), summed per sentence.

## 2. Clipping — the part hand-rolls get wrong

```python
from collections import Counter

def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

def clipped_precision(cand: list[str], refs: list[list[str]], n: int) -> float:
    cand_n = Counter(ngrams(cand, n))
    if not cand_n:
        return 0.0
    # union of max counts across references (multi-reference clipping)
    ref_n = Counter()
    for r in refs:
        for g, c in Counter(ngrams(r, n)).items():
            ref_n[g] = max(ref_n[g], c)
    match = sum(min(c, ref_n[g]) for g, c in cand_n.items())   # the clip
    total = sum(cand_n.values())
    return match / total
```

Why clipping exists: without it, the candidate "the the the the the the"
scores p₁ = 6/6 against a reference containing two "the"s. Clipping caps
each n-gram's credit at its reference count — 2/6 here.

## 3. Full implementation

```python
import math

def sentence_bleu(cand: list[str], refs: list[list[str]],
                  max_n: int = 4) -> float:
    c, rs = len(cand), [len(r) for r in refs]
    # effective reference length (closest, tie -> shorter)
    r_eff = min(rs, key=lambda r: (abs(r - c), r))
    log_sum = 0.0
    for n in range(1, max_n + 1):
        p = clipped_precision(cand, refs, n)
        if p == 0:
            return 0.0                       # any zero n-gram precision -> 0
        log_sum += math.log(p) / max_n
    bp = 1.0 if c > r_eff else math.exp(1 - r_eff / max(c, 1))
    return bp * math.exp(log_sum)

# paper's canonical sanity check:
cand = "the cat is on the mat".split()
refs = [["there is a cat on the mat"], ["a cat sits on the mat"]]
print(round(sentence_bleu(cand, refs), 4))   # ≈ 0.5046 with these refs
```

## 4. Where BLEU lies (memorize this table)

| Failure | Example | Effect |
|---|---|---|
| Synonym swap | "couch" vs "sofa" | 0 credit — semantically fine, scored 0 |
| Word order | "on the mat the cat" | only 2-gram credit drops; BLEU barely notices |
| Short confident caption | "a cat." | BP punishes length, but 1-gram credit is high |
| One reference only | single ground truth | clipping max = that ref; variance explodes |
| Segmenting differently | "cannot" vs "can not" | tokenization changes the score, not the meaning |

The last row generalizes: **BLEU is a function of your tokenizer.** Any BLEU
comparison across papers/repos requires the same tokenization — a fact that
silently invalidates half the table-screenshot comparisons on the internet.

## 5. Corpus BLEU vs mean sentence BLEU

Two aggregation conventions, different numbers:

```python
def corpus_bleu(cands: list[list[str]], refs_list: list[list[list[str]]]) -> float:
    # sums matches and totals ACROSS the corpus per n, then one BP + one exp.
    tot = [0, 0, 0, 0]; match = [0, 0, 0, 0]
    c_len = r_eff_sum = 0
    for cand, refs in zip(cands, refs_list):
        c, rs = len(cand), [len(r) for r in refs]
        c_len += c
        r_eff_sum += min(rs, key=lambda r: (abs(r - c), r))
        for n in range(1, 5):
            cn = Counter(ngrams(cand, n))
            ref_n = Counter()
            for r in refs:
                for g, cnt in Counter(ngrams(r, n)).items():
                    ref_n[g] = max(ref_n[g], cnt)
            match[n - 1] += sum(min(cnt, ref_n[g]) for g, cnt in cn.items())
            tot[n - 1] += max(sum(cn.values()), 0)
    ps = [m / t if t else 0 for m, t in zip(match, tot)]
    if 0 in ps:
        return 0.0
    bp = 1.0 if c_len > r_eff_sum else math.exp(1 - r_eff_sum / max(c_len, 1))
    return bp * math.exp(sum(math.log(p) / 4 for p in ps))
```

Corpus BLEU is the official COCO convention; mean sentence BLEU is what you
get from a naive loop. They differ by several points — always name which one
you report.

## Exercises

1. Verify clipping: score "the the the" against "the cat" — p₁ must be 1/3.
2. Break BP: a perfect 3-word caption against a 20-word reference — compute
   the penalty by hand, then with the code.
3. Reproduce the corpus-vs-sentence gap: 10 candidate/reference pairs where
   candidate lengths vary; report both numbers and explain the delta.

## Pitfalls

- Using `nltk.translate.bleu_score` without `smoothing` — zero counts zero out everything; but smoothing also *changes* the metric; name it.
- Comparing your BLEU to a paper's without matching tokenization and aggregation — meaningless number.
-Reporting BLEU alone for captions — it cannot see semantics; pair with CLIPScore (file 02).

## Resources

- Papineni et al. 2002, "BLEU: a Method for Automatic Evaluation…" §5 (clipping).
- NLTK `bleu_score` docs (for cross-checking your implementation, not replacing it).
