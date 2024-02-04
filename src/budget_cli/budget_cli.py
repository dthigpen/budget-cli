import argparse
import csv
import json
from pathlib import Path
import re
from typing import Iterable


def matches_criteria(text, criteria: str | list[str]) -> bool:
    if isinstance(criteria, str):
        if re.search(criteria, text, flags=re.IGNORECASE):
            return True
    else:
        # TODO handle list[str] case for ANDing multiple
        raise ValueError(f"Unsupported rule value {type(criteria)}")
    return False


def run(budget: dict, transactions: Iterable):
    envelope_assignments = {'Uncategorized': []}
    for row in transactions:
        row_str = ", ".join(row)
        is_match = False
        for envelope in budget["envelopes"]:
            categories = envelope['category']
            if not isinstance(categories, list):
                categories = [categories]
            for category in categories:
                includes = category.get("includes", [])
                excludes = category.get("excludes", [])
                # continue to next category if excluded here
                if any((matches_criteria(row_str, exc) for exc in excludes)):
                    continue
                is_match = any((matches_criteria(row_str, inc) for inc in includes))
                if is_match:
                    break
            if is_match:
                category_name = category.get('name', envelope['name'])
                assigned = envelope_assignments.get(category_name, [])
                assigned.append(row)
                envelope_assignments[category_name] = assigned
                break
        if not is_match:
            envelope_assignments['Uncategorized'].append(row)
    print(json.dumps(envelope_assignments, indent=2))


def existing_file(p: str) -> Path:
    p = Path(p)
    if p.is_file():
        return p
    raise argparse.ArgumentError(f"Path {p} must be an existing file")


def _main():
    parser = argparse.ArgumentParser(
        description="A simple command line tool to manage expenses"
    )
    parser.add_argument("budget", type=existing_file, help="Path to budget json file")
    parser.add_argument(
        "transactions", type=existing_file, help="Path to transactions csv file"
    )
    args = parser.parse_args()
    budget = json.loads(args.budget.read_text())
    with open(args.transactions, newline="") as csvfile:
        transactions_reader = csv.reader(csvfile)
        next(transactions_reader)
        run(budget, transactions_reader)


if __name__ == "__main__":
    _main()
