"""Build a balanced, reproducible evaluation sample from the Jigsaw train.csv.

Usage:
    python src/sample_data.py --input data/train.csv --n 400
Writes data/eval_sample.csv
"""
import argparse
import pandas as pd

LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/train.csv")
    p.add_argument("--n", type=int, default=400, help="total rows (half flagged, half clean)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="data/eval_sample.csv")
    a = p.parse_args()

    df = pd.read_csv(a.input)
    df["any_flag"] = (df[LABELS].sum(axis=1) > 0).astype(int)
    df = df[df["comment_text"].str.len().between(20, 1500)]

    half = a.n // 2
    flagged = df[df.any_flag == 1]
    # Oversample the rare labels so each category has enough cases to score.
    rare = flagged[(flagged.threat == 1) | (flagged.identity_hate == 1) | (flagged.severe_toxic == 1)]
    rare_take = rare.sample(min(len(rare), half // 2), random_state=a.seed)
    rest = flagged.drop(rare_take.index).sample(half - len(rare_take), random_state=a.seed)
    clean = df[df.any_flag == 0].sample(half, random_state=a.seed)

    out = pd.concat([rare_take, rest, clean]).sample(frac=1, random_state=a.seed)
    out[["id", "comment_text"] + LABELS].to_csv(a.out, index=False)
    print(f"Wrote {len(out)} rows to {a.out}")
    print(out[LABELS].sum().to_string())


if __name__ == "__main__":
    main()
