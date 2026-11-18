"""Score predictions against the human labels.

Usage:
    python src/evaluate.py --policy-version v1
Writes results/metrics_<version>.csv, results/false_negatives_<version>.csv,
results/false_positives_<version>.csv and prints a summary.
"""
import argparse
import json

import pandas as pd

LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]


def scores(y, p):
    tp = int(((y == 1) & (p == 1)).sum())
    fp = int(((y == 0) & (p == 1)).sum())
    fn = int(((y == 1) & (p == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"support": int((y == 1).sum()), "tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/eval_sample.csv")
    p.add_argument("--policy-version", default="v1")
    a = p.parse_args()

    truth = pd.read_csv(a.input).set_index("id")
    rows = [json.loads(l) for l in open(f"results/predictions_{a.policy_version}.jsonl")]
    pred = pd.DataFrame([{"id": r["id"], **{f"pred_{k}": r["labels"][k] for k in LABELS},
                          "needs_review": r["needs_review"], "reason": r["reason"]} for r in rows]
                        ).set_index("id")
    df = truth.join(pred, how="inner")

    metrics = {k: scores(df[k], df[f"pred_{k}"]) for k in LABELS}
    df["any_true"] = (df[LABELS].sum(axis=1) > 0).astype(int)
    df["any_pred"] = (df[[f"pred_{k}" for k in LABELS]].sum(axis=1) > 0).astype(int)
    metrics["ANY_VIOLATION"] = scores(df["any_true"], df["any_pred"])
    m = pd.DataFrame(metrics).T
    m.to_csv(f"results/metrics_{a.policy_version}.csv")

    fn = df[(df.any_true == 1) & (df.any_pred == 0)]
    fp = df[(df.any_true == 0) & (df.any_pred == 1)]
    fn.to_csv(f"results/false_negatives_{a.policy_version}.csv")
    fp.to_csv(f"results/false_positives_{a.policy_version}.csv")

    review_rate = df["needs_review"].mean()
    print(m.to_string())
    print(f"\nScored rows: {len(df)}")
    print(f"Missed violations (false negatives): {len(fn)}")
    print(f"Over-flagged clean messages (false positives): {len(fp)}")
    print(f"Sent to human review: {review_rate:.1%}")


if __name__ == "__main__":
    main()
