# Personal finance analizer

SETUP:
1. add your extracts to `data/00_raw`
2. run notebooks from 1 to 3
3. see the magic with notebook 10.

Workflow:
each month you will ask for the extract in `nubank` account. place it in `data/00_raw`.
then, you perform automatic cleaning, semi-automatic categorization and reconciliation.
when your data is prepared, `10_analyzer.ipynb` will build the dashboards for you.

details:
**categorizer**
you will need to manually add descriptions to `category_lookup.json`. this is your starting point for transaction categorization.
don't worry, the amount of manual work decreases with time. as you construct your database with categorized transactions, machine learning will start to do it for you.

**reconcilator**
also, you will need to check in your bank what is the balance for each month. this ensures that your data is correct.

**MORE DASHBOARD AND ANALYZING FEATURES TO COME**


