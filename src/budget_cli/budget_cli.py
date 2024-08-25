import argparse
import csv
from datetime import datetime, date
import json
from pathlib import Path
import re
from typing import Iterable, List


def __transaction_matches_account(transaction: dict, account: dict) -> bool:
    account_on_transaction = str(transaction.get('account',''))
    return bool(re.search(account['name'], account_on_transaction))
        
def __transaction_matches_category(transaction: dict, category: dict) -> bool:
    is_match = False
    if category.get('includes'):
        for inc in category.get('includes'):
            is_inc_match = True
            for col_name, col_pattern in inc.items():
                col_str = str(transaction.get(col_name, ''))
                if not re.search(col_pattern, col_str, re.I):
                    is_inc_match = False
                    break
            if is_inc_match:
                is_match = True
                break
    if is_match and category.get('excludes'):
        for exc in category.get('excludes'):
            for col_name, col_pattern in exc:
                col_str = f'{transaction.get("col_name", "")}'
                if re.match(col_pattern, col_str, re.I):
                    is_match = False
                             
            if not is_match:
                break
    return is_match

def group_by(items: list, key_getter) -> dict:
    groups = {}
    for item in items:
        key = key_getter(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups

def run(budget: dict, transactions: Iterable[dict], output_dir: Path):
    print('Generating reports')
    transactions = list(transactions)
    accounts = budget.get('accounts', [])
    actions = budget.get('actions', [])
    # split/replace should be done before categorization because it adds/removes transactions
    pre_categorization_actions = list(filter(lambda a: a.get('type') in ('split', 'replace'), actions))

    post_categorization_actions = list(filter(lambda a: a.get('type') in ('hide',), actions))
    unhandled_actions = list(filter(lambda a: a not in pre_categorization_actions and a not in post_categorization_actions, actions))
    if unhandled_actions:
        types = ', '.join(map(lambda x: x.get('type'), unhandled_actions))
        raise ValueError(f'Actions with unknown types: {types}')

    # handle negating transactions on accounts of type credit
    if accounts:
        credit_accounts = list(
            filter(
                lambda a: a.get('type').lower() == 'credit',
                accounts
            )
        )
        for acc in credit_accounts:
            matching_transactions = filter(lambda x: __transaction_matches_account(x, acc), transactions)
            for t in matching_transactions:
                t['amount'] = -1 * float(t['amount'])
    
    # handle pre_categorization_actions
    removed_transactions = []
    added_transactions = []
    for action in pre_categorization_actions:

        action_type = action['type']
        if action_type in ('split', 'replace'):
            incs = action.get('includes', [])
            excs = action.get('excludes', [])
            dummy_category = {'name': 'dummy', 'includes': incs, 'excludes': excs}
            matching_transactions = list(filter(lambda x: transaction_matches_category(x, dummy_category)))
            # e.g. replace/with split/into
            replacements = action.get('into', action.get('with', []))
            if not replacements:
                raise ValueError('Replace/split actions must have an "into" or "with" property with replacement transaction details')
                
            removed_transactions.extend(matching_transactions)
            for t in matching_transactions:
                replacement_transactions = []
                orig_amount = t['amount']
                orig_amount_sign = 1 if t['amount'] >= 0 else -1
                orig_amount_abs = abs(orig_amount)
                for repl in replacements:
                    repl_amount = repl.pop('amount', None)
                    repl_transaction = {**json.loads(json.dumps(repl)), **json.loads(json.dumps(repl))}
                    new_amount = None
                    if isinstance(repl_amount, (int, float)):
                        # TODO handle sign
                        new_amount = repl_amount
                    elif isinstance(repl_ammount, str):
                        # TODO implement
                        raise NotImplmentedError(f'Using percentages in replacements has not been implemented yet')
                    else:
                        raise ValueError(f'Invalid replacement amount: {repl_amount}')
                    repl_transaction['amount'] = new_amount
                    if repl_amount is not None:
                        repl_transaction['note'] = f'Generated: Split {replacement_amount} of {orig_amount}'
                    replacement_transactions.append(repl_transaction)
                replacement_transactions_without_amounts = filter(lambda x:'amount' not in x, replacement_replacement_transactions)
                if replacement_transactions:
                    # TODO assign lefover amount evenly
                    raise NotImplementedError(f'Replacements must include exact amount')
                # TODO verify that everything adds up, if not add transaction?
    preprocessed_transactions = [*filter(lambda x: x not in removed_transactions, transactions), *added_transactions]
    preprocessed_transactions = sorted(preprocessed_transactions, key=lambda x: x['date'])

    # categorize transactions
    for transaction in filter(lambda x: not x.get('category'), preprocessed_transactions):
        found_category = False
        matching_categories = []
        for category in budget.get('categories',[]):
            if __transaction_matches_category(transaction, category):
                matching_categories.append(category)
                transaction['category'] = category['name']
                # break
        if len(matching_categories) > 1:
            print(f'Warning: Transaction matches multiple categories. Transaction: {json.dumps(transaction)} Categories: {", ".join(map(lambda c: c["name"], matching_categories))}')
        if not matching_categories:
            transaction['category'] = 'uncategorized'
            # exit()
    hidden_transactions = []
    for action in post_categorization_actions:
        action_type = action['type']
        if action_type == 'hide':
            categories_to_hide = action.get('categories', [])
            incs = action.get('includes', [])
            excs = action.get('excludes', [])
            dummy_category = {'name': 'dummy', 'includes': incs, 'excludes': excs}
            matching_transactions = []
            matching_transactions.extend(filter(lambda x: x['category'] in categories_to_hide, transactions))
            matching_transactions.extend(filter(lambda x: __transaction_matches_category(x, dummy_category), transactions))
            hidden_transactions.extend(matching_transactions)

    transactions_after_post_actions = list(filter(lambda x: x not in hidden_transactions, preprocessed_transactions))
    report = {
        'monthly': [
            # month: 2024-04,
            # categories: []
        ]
    }
    month_groups = group_by(transactions_after_post_actions, lambda t: t['date'][:7])
    group_entries = sorted(month_groups.items(), key=lambda x: x[0])
    for year_month, month_transactions in group_entries:
        month_report = {
            'lastUpdated': datetime.now().isoformat()[:19],
            'month': year_month,
            'summary': {
            },
            'transactions': {
                
            }
        }
        report['monthly'].append(month_report)
        category_groups = group_by(month_transactions, lambda t: t['category'])
        for category_name, category_transactions in category_groups.items():
            category_total = sum(map(lambda t: t['amount'], category_transactions))
            if category_name == 'uncategorized':
                category_type = 'uncategorized'
            else:
                category_type = next((c for c in budget.get('categories', []) if c['name'] == category_name), {'type': 'expense'})['type']
            if category_type == 'uncategorized':
                month_report['summary'][category_type] = round(category_total, 2)
            else:
                if category_type not in month_report['summary']:
                    month_report['summary'][category_type] = { 'categories': {}}
                month_report['summary'][category_type]['categories'][category_name] = round(category_total, 2)
            def without_categories(t):
                t = json.loads(json.dumps(t)) # copy dict
                t.pop('category')
                return t
            if category_type == 'uncategorized':
                month_report['transactions'][category_type] = list(map(without_categories, category_transactions))
            else:
                if category_type not in month_report['transactions']:
                    month_report['transactions'][category_type] = {}
                
                month_report['transactions'][category_type][category_name] = list(map(without_categories, category_transactions))
        # calculate category totals
        for cat_type, cat_type_obj,  in month_report['summary'].items():
            if cat_type == 'uncategorized':
                continue
            total = sum(
                map(float, cat_type_obj['categories'].values())
            )
            cat_type_obj['total'] = round(total, 2)
        # calculate savings
        income_total = month_report['summary'].get('income',{}).get('total',0.0)    
        expense_total = month_report['summary'].get('expense',{}).get('total',0.0)
        if income_total is not None and expense_total is not None:
            # expenses are negative so + is used
            savings_total = income_total + expense_total
            month_report['summary']['savings'] = {
                'total': round(savings_total, 2),
                'rate': round((savings_total/income_total) if income_total != 0.0 else 0.0, 2)
            }
        # reinsert uncategorized so it goes after the other
        if 'uncategorized' in month_report['summary']:
            month_report['summary']['uncategorized'] = month_report['summary'].pop('uncategorized')
        if 'uncategorized' in month_report['transactions']:
            month_report['transactions']['uncategorized'] = month_report['transactions'].pop('uncategorized')
        month_report_file = output_dir / f'{year_month}-report.json'
        print(f'Writing report: {month_report_file}')
        month_report_file.write_text(json.dumps(month_report, indent=2))

def read_transactions(paths: List[Path]):
    for p in paths:
        transactions = json.loads(p.read_text())
        for t in transactions:
            yield t

def parse_budget(budget_path: Path) -> dict:
    DEFAULT_BUDGET = {
        'categories': [],
        'actions': [],
    }
    budget = json.loads(budget_path.read_text())
    budget = {**DEFAULT_BUDGET, **budget}
    return budget

def main():
    def existing_file(p: str) -> Path:
        p = Path(p)
        if p.is_file():
            return p
        raise argparse.ArgumentError(f"Path {p} must be an existing file")

    parser = argparse.ArgumentParser(
        description="A command line tool to generate budgeting reports from transactions"
    )
    parser.add_argument("budget_file", type=existing_file, help="Path to budget json file")
    parser.add_argument(
        "transactions_files", nargs='+', type=existing_file, help="Path to transactions json files"
    )
    parser.add_argument('-o','--output-dir', type=Path, default=Path.cwd(), help='Directory to output reports to')
    args = parser.parse_args()
    budget = parse_budget(args.budget_file)
    transactions= read_transactions(args.transactions_files)
    run(budget, transactions, args.output_dir)
    
    
if __name__ == "__main__":
    main()
