#!/usr/bin/env python3
"""
AI CSV Data Cleaner (offline)
Usage:
  python main.py --file dirty.csv
  python main.py --input "col1,col2\nval1,val2\n..."
"""
import argparse, requests, json, sys, os

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = "llama3.2:4b"
TIMEOUT = 600

def run_llama(prompt):
    resp = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()

def build_prompt(csv_text):
    return (
        "You are a helpful data cleaning assistant.\n"
        "1) List the top issues found in the CSV (duplicates, inconsistent date formats, missing values, typos, inconsistent casing).\n"
        "2) Output a 'CLEANED_CSV:' section with a corrected CSV (same columns), using commas and preserving header.\n"
        "If you cannot perfectly fix something, explain the reasoning under 'Notes:'.\n\n"
        f"CSV_INPUT:\n{csv_text}\n\nRespond as plain text."
    )

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", "-f", help="Path to CSV file")
    p.add_argument("--input", "-i", help="CSV text inline")
    args = p.parse_args()
    content = args.input or ""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                content = (content + "\n" if content else "") + fh.read()
        except Exception as e:
            print("Error reading file:", e, file=sys.stderr); sys.exit(1)
    if not content.strip():
        print("Provide --input or --file", file=sys.stderr); sys.exit(1)
    prompt = build_prompt(content)
    print(run_llama(prompt))

if __name__ == "__main__":
    main()
