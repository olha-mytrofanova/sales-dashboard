# Sales & Marketing Dashboard

Interactive sales and marketing dashboard built with Python and Plotly Dash.

## What it does
- Filters data by category and region
- Tracks key KPIs: revenue, units sold, ROAS, ad spend
- Visualises revenue by region and monthly trend
- Compares revenue vs ad spend by category
- Shows correlation between ad spend and revenue with trendline
- Ranks top performers by region and category

## Tech stack
- Python 3
- Plotly Dash — interactive dashboard framework
- Pandas — data processing
- Statsmodels — trendline calculation

## How to run

```bash
pip3 install dash plotly pandas statsmodels
python3 app.py
```

Open http://127.0.0.1:8050/ in your browser.

## Sample insight
Electronics drives the highest absolute revenue but Clothing shows competitive ROAS at lower ad spend,suggesting room to scale Clothing investment.
