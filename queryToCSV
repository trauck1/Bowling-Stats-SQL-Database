import mysql.connector
from bs4 import BeautifulSoup
import requests
import csv


#example query
#"select date,name, (avg(spares)/avg(spareOs)) as \"Spare Percent\", (avg(strikes)/avg(strikeOs)) as \"Strike Percent\" from games group by date, name;"

if __name__ == "__main__":
    
    mydb = mysql.connector.connect(host = "host", 
                                user = "user", 
                                passwd="password",
                                database="urDatabase")

    cursor = mydb.cursor()
    query = "any query"
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Get column names
    column_names = [desc[0] for desc in cursor.description]

    # Write to CSV
    with open("averagesOverTime.csv", "w", newline="") as file:
        writer = csv.writer(file)
    
        # Write header
        writer.writerow(column_names)
    
        # Write data
        writer.writerows(rows)

    print("CSV written successfully!")
    # Cleanup
    cursor.close()
    mydb.close()
