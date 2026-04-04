from sqlalchemy  import create_engine
import pandas as pd

engine = create_engine("mysql+pymysql://root:1771@localhost/dash")
con = engine.connect()
print("Connected successfully!")

def run_query(query):

    engine = create_engine("mysql+pymysql://root:1771@localhost/dash")
    con = engine.connect()
    df = pd.read_sql_query(query , con)
    con.close()
    return df

































# Here it is:

# ---

# ## Python + SQL Dashboard — Clean Summary

# ---

# ### Why Python + SQL
# - Data lives in a database, Python connects to it, fetches results, plots charts
# - SQL does the heavy data work (filter, group, aggregate), Python just visualizes
# - Together they simulate how real products are actually built

# ---

# ### How it's Different from CSV

# | CSV | SQL + Python |
# |---|---|
# | Static, fixed file | Live database |
# | Load all 3L rows into memory | Fetch only what you need |
# | Pandas does all the work | SQL does the work, pandas just receives |
# | Stale data | Always current |

# ---

# ### How Real World Works
# - Company data lives in MySQL/PostgreSQL, not CSV files
# - Backend queries the DB on demand
# - Dashboard always reflects current data
# - New record added to DB → dashboard shows it automatically

# ---

# ### Workflow
# ```
# MySQL Workbench → test query → satisfied
# → paste query in app.py inside run_query()
# → plotly chart on that df
# → streamlit renders in browser
# → user changes filter → f-string rebuilds query
# → fresh result → chart updates
# ```

# ---

# ### One Line Summary
# **CSV is a file. DB is a live system. SQL queries it. Python plots it. Streamlit shows it. Filters make it dynamic.**

# ---

# That's everything. Now go build. 🚀
    
