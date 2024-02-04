import argparse
import csv
from datetime import datetime, date
import json
from pathlib import Path
import re
from typing import Iterable
from dataclasses import dataclass

@dataclass
class Transaction:
    date_occurred: datetime
    amount: float
    name: str
    row: list = None

def matches_criteria(text, criteria: str | list[str]) -> bool:
    if isinstance(criteria, str):
        if re.search(criteria, text, flags=re.IGNORECASE):
            return True
    else:
        # TODO handle list[str] case for ANDing multiple
        raise ValueError(f"Unsupported rule value {type(criteria)}")
    return False

def run(budget: dict, transactions: Iterable[Transaction], start=None, end=None):
    envelope_assignments = {'Uncategorized': []}
    for t in transactions:
        # print(t)
        row_str = ", ".join(t.row)
        is_match = False
        for category in budget['categories']:
            includes = category.get("includes", [])
            excludes = category.get("excludes", [])
            # continue to next category if excluded here
            if any((matches_criteria(row_str, exc) for exc in excludes)):
                continue
            if any((matches_criteria(row_str, inc) for inc in includes)):
                is_match = True
                break
        if is_match:
            category_name = category.get('name')
            assigned = envelope_assignments.get(category_name, [])
            assigned.append(row_str)
            envelope_assignments[category_name] = assigned
        else:
            envelope_assignments['Uncategorized'].append(row_str)
    print(json.dumps(envelope_assignments, indent=2))


def existing_file(p: str) -> Path:
    p = Path(p)
    if p.is_file():
        return p
    raise argparse.ArgumentError(f"Path {p} must be an existing file")


def parse_date_str(date_str: str) -> date:
    if date_str == "now":
        return datetime.today().date()
    return date.fromisoformat(date_str)
    
def parse_datetime_str(datetime: str) -> datetime:
    return date.fromisoformat(datetime)
    
def _main():
    parser = argparse.ArgumentParser(
        description="A simple command line tool to manage expenses"
    )
    parser.add_argument("budget", type=existing_file, help="Path to budget json file")
    parser.add_argument(
        "transactions", nargs='+', type=existing_file, help="Path to transactions csv file"
    )
    parser.add_argument("--date-col", type=int, default=0, help="column index of the date of the transaction")
    parser.add_argument("--amount-col", type=int, default=1, help="column index of the amount of the transaction")
    parser.add_argument("--name-col", type=str, default=2, help="column index of the name of the transaction")
    parser.add_argument("--start", type=parse_date_str, help="start date of transaction history in YYYY-MM-DD format")
    parser.add_argument("--end", type=parse_date_str, help="end date of transaction history in YYYY-MM-DD format")

    args = parser.parse_args()
    budget = json.loads(args.budget.read_text())
    # read in and sort all transactions
    all_transaction_rows = []
    for t in args.transactions:
        with open(t, newline="") as csvfile:
            transactions_reader = csv.reader(csvfile)
            next(transactions_reader)
            file_transactions = list(transactions_reader)
            if args.start and args.end:
                file_transactions = filter(lambda r: args.start <= parse_datetime_str(r[args.date_col]) <= args.end, file_transactions)
            all_transaction_rows.extend(file_transactions)
    all_transaction_rows.sort(key=lambda r: parse_datetime_str(r[args.date_col]))
    all_transaction = map(lambda r: Transaction(parse_datetime_str(r[args.date_col]), float(r[args.amount_col]), r[args.name_col], row=r), all_transaction_rows)
    run(budget, all_transaction)


if __name__ == "__main__":
    _main()
