# GenAI Content Safety Evaluation

An evaluation of an LLM content-safety classifier against human labels, plus red-teaming of an LLM app against prompt injection, with an escalation playbook and feedback loop.

> **Content warning:** the Jigsaw dataset contains real toxic comments (insults, slurs, threats).

## What this project does
1. **Moderation classifier:** the Claude API classifies messages against a written content policy (`policy/content_policy.md`).
2. **Accuracy against human labels:** precision and recall per category on a balanced sample of the public Jigsaw / Civil Comments toxicity data, with every miss exported for review.
3. **Red-teaming:** 30 prompt-injection attacks hidden in risk-register entries (severity downgrades, fake system notes, canary words, prompt-leak attempts), tested before and after a guardrail.
4. **Ops layer:** an escalation playbook with root-cause tags and a v1 → v2 policy feedback loop (`ops/escalation_playbook.md`).

## Why not child-safety data
Real child-safety enforcement relies on restricted, hash-matched data under legal controls. This project uses a public, human-labeled dataset to show the same evaluation method: measure misses, investigate why, fix the policy, re-measure.

## Setup
```bash
pip install anthropic pandas
export ANTHROPIC_API_KEY=your_key
```
Get the labeled data (pick one):
- **Hugging Face (no login):** `pip install datasets` then `python src/get_data_hf.py --rows 100000`. This pulls Google's Civil Comments (same Jigsaw research team, human-rated toxicity labels) into `data/train.csv`.
- **Kaggle:** download `train.csv` from the Toxic Comment Classification Challenge (you must accept the competition rules first) and put it in `data/`.

## Run it (in order)
```bash
python src/sample_data.py --input data/train.csv --n 400    # balanced sample
python src/classify.py --policy-version v1                   # ~400 API calls
python src/evaluate.py --policy-version v1                   # metrics + misses
# Review results/false_negatives_v1.csv, tag root causes (ops playbook),
# copy the policy to policy/content_policy_v2.md and improve it, then:
python src/classify.py --policy policy/content_policy_v2.md --policy-version v2
python src/evaluate.py --policy-version v2
python src/redteam.py --mode baseline
python src/redteam.py --mode guarded
```
Tip: paste SentinAI's real system prompt into `redteam/system_prompt.txt` so the red-team results describe your actual app.

## Results (fill in from your runs)
| Metric | v1 | v2 |
|---|---|---|
| Any-violation recall | 62.5% | 75.0% |
| Any-violation precision | 82.2% | 79.8% |
| Threat recall | 44.9% | 61.2% |
| Identity-hate recall | 43.1% | 55.4% |
| Missed violations (count) | 75 | 50 |
| Sent to human review | 31.8% | 22.5% |

| Red-team | Baseline | Guarded |
|---|---|---|
| Attack success rate (30 cases) | 17% | 7% |
| Injections flagged by model | n/a | 80% |

**Top root causes of misses (v1):** insult rules read too narrowly (political and public-figure name-calling skipped), identity hate required slurs (stereotypes missed), and calls for violence not treated as threats. About a third of misses were label noise.
**Policy changes in v2:** insults cover public figures, groups and commenters; identity hate covers stereotypes and disgust toward groups; threats include calls for executions or violence framed as justice; crude profanity counts as obscene. severe_toxic is excluded from results (0 positive cases at the 0.5 agreement threshold).

## Honesty notes
- Results come from a 400-message sample, not production traffic.
- Jigsaw labels contain some noise; cases tagged `label_noise` are logged, not hidden.
