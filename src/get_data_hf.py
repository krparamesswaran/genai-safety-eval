"""Alternative to Kaggle: download human-labeled toxicity data from Hugging Face
(Google's Civil Comments, from the same Jigsaw research team) and save it in the
same format the rest of the project expects (data/train.csv).

Usage:
    pip install datasets
    python src/get_data_hf.py --rows 100000
"""
import argparse

import pandas as pd
from datasets import load_dataset

# Civil Comments label -> project label. Scores are the share of human raters
# who applied the label; 0.5 or higher counts as a positive label.
MAP = {
    "toxicity": "toxic",
    "severe_toxicity": "severe_toxic",
    "obscene": "obscene",
    "threat": "threat",
    "insult": "insult",
    "identity_attack": "identity_hate",
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, default=100000)
    p.add_argument("--out", default="data/train.csv")
    a = p.parse_args()

    stream = load_dataset("google/civil_comments", split="train", streaming=True)
    rows = []
    for i, r in enumerate(stream):
        if i >= a.rows:
            break
        row = {"id": f"cc{i}", "comment_text": r["text"]}
        for src, dst in MAP.items():
            row[dst] = int(r[src] >= 0.5)
        rows.append(row)
        if i and i % 20000 == 0:
            print(f"{i} rows read")

    df = pd.DataFrame(rows)
    df.to_csv(a.out, index=False)
    print(f"Wrote {len(df)} rows to {a.out}")
    print(df[list(MAP.values())].sum().to_string())


if __name__ == "__main__":
    main()
