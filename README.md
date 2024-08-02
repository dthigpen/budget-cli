# Budget CLI

A command line tool to manage generate personal finance expense reports.

## Examples

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

- Show warning when multiple categories match same tranaction
- Handle various actions
  - split/replace transaction
