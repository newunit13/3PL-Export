import TPLC
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from six.moves import urllib
from datetime import datetime


# Create connection to Production DAX environment
params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=B4BSQL;DATABASE=DynamicsAX_Prod")
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# SQL query that will pull the current inventory values for each location in the Progress warehouse
sql_query = '''
SELECT
	wms.WMSLOCATIONID					          [Location]
	,ISNULL(SUM(ins.PHYSICALINVENT),0)	[Qty]
FROM WMSLOCATION wms
LEFT JOIN INVENTDIM ind ON ind.WMSLOCATIONID = wms.WMSLOCATIONID AND ind.DATAAREAID = wms.DATAAREAID
LEFT JOIN INVENTSUM ins ON ins.INVENTDIMID = ind.INVENTDIMID and ins.DATAAREAID = ind.DATAAREAID
WHERE wms.DATAAREAID = 'ssl'
  AND wms.INVENTLOCATIONID in ('Progress')
  AND LEFT(wms.WMSLOCATIONID, 1) = 'N'
GROUP BY wms.INVENTLOCATIONID, wms.WMSLOCATIONID
ORDER BY wms.INVENTLOCATIONID, wms.WMSLOCATIONID
'''

# Collect DAX data and convert to DataFrame
dax_df = pd.read_sql_query(sql_query, engine, index_col='Location')

# Collect 3PL Data
locations_raw = TPLC.GetLocations(pgsiz=10000, rql="facilityIdentifier.id==2;deactivated==False;name==N*")
locations = {location["name"]: location["hasInventory"] for location in locations_raw}

# Convert 3PL Data into DataFrame
tpl_df = pd.DataFrame.from_dict(locations, orient='index')
tpl_df.index.name = 'Location'

# Create consolidated DataFrame from both TPL and DAX data
df = tpl_df.merge(dax_df, how='left', left_index=True, right_index=True)

# Move index into column
df.reset_index(inplace=True)

# Create True/False column for DAX inventory
df['DAX'] = df[['Qty']].apply(lambda x: x > 0)

# Add columns for aggregation analysis
df['Either'] = np.where(df['TPL'] | df['DAX'], True, False)
df['Both'] = np.where(df['TPL'] & df['DAX'], True, False)
df['Date'] = datetime.today()

# Clean up DataFrame
df.rename(columns={0: 'TPL'}, inplace=True)
df.drop(columns=['Qty'], inplace=True)

# Set up connection to Warehouse database
params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=DAXTEST;DATABASE=Warehouse")
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Write data to fact table in the Warehouse database
df.to_sql('factWarehouseUtilization', engine, if_exists='append', index=False)

print('Complete')