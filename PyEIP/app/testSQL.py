import pymssql
from datetime import datetime
import json


conn = pymssql.connect(
    server='117.53.152.155',
    port=1433,
    user='sa',
    password='Enav-DB123Sql456!!!',
    database='VTS',
    as_dict=True
) 

SQL_QUERY = f"""
    SELECT sl.ShipListID, 
    sl.IMO, 
    sl.CallSign, 
    sl.Name, 
    sl.ShipType, 
    sl.Dimension_A, 
    sl.Dimension_B, 
    sl.Dimension_C, 
    sl.Dimension_D, 
    sl.MaxDraught, 
    sl.Destination, 
    sl.ETA, 
    sl.EquipTypeID, 
    sl.ESN, 
    sl.DNID, 
    sl.MemberNumber, 
    ddms.* 
    FROM [VTS].[dbo].[ShipList] sl
    INNER JOIN [VTS].[dbo].[Draught] ddms on ddms.MMSI = sl.MMSI
"""

cursor = conn.cursor()
cursor.execute(
    SQL_QUERY
)

records = cursor.fetchall()
conn.close()

# print(records[0]['RecvTime'].isoformat())

# records[0]['RecvTime'] = records[0]['RecvTime'].isoformat()
# print(json.dumps(records[0]))


for i in range(len(records)):
    if records[i]['ETA'] != None:
        records[i]['ETA'] = records[i]['ETA'].isoformat()

    records[i]['RecvTime'] = records[i]['RecvTime'].isoformat()


print(json.dumps(records))

