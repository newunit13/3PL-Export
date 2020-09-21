import TPLC
import pandas as pd
import pyodbc 
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=B4BSQL;'
                      'Database=DynamicsAX_Prod;'
                      'Trusted_Connection=yes;')



# Collect 3PL Data
locations_raw = TPLC.GetLocations(pgsiz=10000, rql="facilityIdentifier.id==2;deactivated==False;name==N*")
locations = {location["name"]: location["hasInventory"] for location in locations_raw}

# Convert 3PL Data into DataFrame
tpl_data = pd.DataFrame.from_dict(locations, orient='index')


# Collect DAX data and convert to DataFrame
cursor = conn.cursor()
sql_query = '''
SELECT
	wms.WMSLOCATIONID					[Location]
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

dax_data = pd.read_sql_query(sql_query, conn, index_col='Location')

# Merge DataFrames on the index
data = pd.merge(tpl_data, dax_data, how='left', on='left_index')
print(data)