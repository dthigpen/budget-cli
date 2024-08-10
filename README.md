# Budget CLI
Manage your personal finances and generate expense reports of your spending, all without sending sensitive bank information to third-parties!
 - Get summaries of monthly spending by category
 - Identify uncategorized transactions
 - Savings rate
## Usage

### Create a budget

Budgets are defined in JSON. Create categories to group transactions.
```json
{
    "categories": [
        {
            "name": "Job",
            "type": "income",
            "includes": [
                {
                    "description": "MY COMPANY DEPOSIT"
                },
                {
                    "description": "SIDE GIG"
                }
            ]
        },
        {
            "Entertainment",
            "type": "expense",
            "includes": [
                {
                    "date": "2024-04",
                    "description": "STARBUCKS"
                },
                {
                    "description": "HARKINS"
                }
            ]
        }
    ]
}
```
A transaction must match at least one of the entries in the `includes` in order to be assigned this category. Each entry is composed of keys and values in the transaction to (regex) match against. By default these regex matches are case insensitive and match anywhere within the value. (e.g. `"description": "foo.*bar"` would match `"description": "SOME FOO #123 BAR"`)

Credit type accounts can also be declared so that their transaction amounts are inverted.
```json
{
  "accounts": [
      {
             "name": "Credit Card",
             "type": "credit"
      }
  ],
  "categories": [
  ]
```
### Running `budget-cli`
```
$ budget-cli budget.json ~/transactions/*.json
Writing report: 2024-05-report.json
Writing report: 2024-07-report.json
```
```json
{
  "lastUpdated": "2024-08-04T11:13:18",
  "month": "2024-05",
  "summary": {
    "expense": {
      "categories": {
        "HOA": "105.00",
        "Travel": "512.43",
        "Internet": "60.43",
        "Entertainment": "112.12",
        "Groceries": "198.02",
        "Water": "44.75"
      }
    },
    "uncategorized": "36.07"
  },
  "transactions": {
    "expense": {
      "HOA": [
        {
          "date": "2024-05-01",
          "description": "COMMUNITY HOA",
          "amount": 105.0,
          "account": "Some Credit Card"
        }
      ],
      "Travel": [
        {
          "date": "2024-05-02",
          "description": "SOUTHWEST AIRLINES",
          "amount": 512.43,
          "account": "Some Credit Card"
        }
      ],
      "Internet": [
        {
          "date": "2024-05-08",
          "description": "COMCASTCABLECOMM 800-COMCAST CO",
          "amount": 60.43,
          "account": "Some Credit Card"
        }
      ]
    }
  }
}
```

## TODO

- Handle various actions
  - split transactions
  - regex replace on transactions
