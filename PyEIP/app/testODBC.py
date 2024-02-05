import pyodbc

# Connect to SQL Server using pyodbc
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};" 
                        "server=117.53.152.155;" 
                        "port=1433;" 
                        "user=sa;" 
                        "password=Enav-DB123Sql456!!!;" 
                        "database=VTS" 
                      "Trusted_Connection=yes;")

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

# Create a cursor object
cursor = cnxn.cursor()

# Execute a query
cursor.execute(SQL_QUERY)

# Fetch and print the results
for row in cursor:
    print(row)