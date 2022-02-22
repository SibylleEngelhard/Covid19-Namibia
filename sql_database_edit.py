import sqlite3
from datetime import datetime
from pytz import timezone
import os


now=datetime.now(timezone("Africa/Johannesburg"))
datenow=datetime.now(timezone("Africa/Johannesburg")).date()
#utcnow=datetime.utcnow()
#currentdatetime=now.strftime("%A, %d %B %Y %H:%M")
#date_isoformat=datetime.now(timezone("Africa/Johannesburg")).date().isoformat()

#print(now)
#print(datenow)
#print(utcnow)
#print(currentdatetime)
#print(date_isoformat)

connection = sqlite3.connect("./covid19_Nam.db")

#sqlite3.connect(":memory:")
cursor = connection.cursor()

#cursor.execute("CREATE TABLE IF NOT EXISTS active_date(id INTEGER PRIMARY KEY, active_date TEXT NOT NULL)")
#cursor.execute("INSERT INTO active_date(active_date) VALUES (?)",(date_isoformat,))   
#rows = cursor.execute("SELECT * FROM active_date").fetchall()
#print(rows)

"""
target_name = "siby6"
cursor.execute("DELETE FROM users WHERE username = ?", (target_name,))
rows = cursor.execute("SELECT * FROM users").fetchall()
#print(rows)
for row in rows:
	print (row[0])
	print (row[1])
	print (row[2])
"""

#cursor.execute("CREATE TABLE IF NOT EXISTS districts (id INTEGER PRIMARY KEY, district TEXT NOT NULL, region TEXT NOT NULL)")
#cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_districts ON districts (district)")   
#cursor.execute("DROP INDEX district")
#cursor.execute("INSERT INTO districts (district,region) VALUES('Okahao', 'Omusati')")

"""
rows = cursor.execute("SELECT * FROM districts").fetchall()
print(rows)
for row in rows:
	print ("id: ",row[0])
	print ("district: ",row[1])
	print ("region: ",row[2])

existing_districts=[]
rows= cursor.execute("SELECT district FROM districts").fetchall()
for row in rows:
	print(row[0])
	existing_districts.append(row[0])
print(existing_districts)
"""
#cursor.execute("CREATE TABLE IF NOT EXISTS districts(id INTEGER PRIMARY KEY, district TEXT NOT NULL, region TEXT NOT NULL)")
#cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_districts ON districts (district)")   
#cursor.execute("CREATE TABLE IF NOT EXISTS deaths2(id INTEGER PRIMARY KEY, publish_date TEXT NOT NULL, district TEXT NOT NULL, sex TEXT NOT NULL, age INTEGER, comorbidities TEXT NOT NULL, death_date TEXT NOT NULL, classification TEXT NOT NULL, update_date TEXT NOT NULL)")
          
#cursor.execute("CREATE TABLE IF NOT EXISTS deaths2(id INTEGER PRIMARY KEY, publish_date TEXT NOT NULL, district TEXT, sex TEXT, age INTEGER, comorbidities TEXT, death_date TEXT NOT NULL, classification TEXT, update_date TEXT NOT NULL)")
#cursor.execute("INSERT INTO deaths2 SELECT * FROM deaths")
#cursor.execute("DROP TABLE deaths")
#cursor.execute("ALTER TABLE deaths2 RENAME TO deaths")         

#cursor.execute("CREATE TABLE IF NOT EXISTS cases(id INTEGER PRIMARY KEY, cases_date TEXT NOT NULL, district TEXT NOT NULL, new_cases INTEGER, update_date TEXT NOT NULL)")
#cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_cases ON cases (cases_date,district)")   

#cursor.execute("DROP TABLE districts")
#row = cursor.execute("SELECT * FROM districts")
#print(row)
#cursor.execute("DROP TABLE cases")
#row = cursor.execute("SELECT * FROM cases")

#cursor.execute("DROP TABLE recoveries")
#row = cursor.execute("SELECT * FROM recoveries")
#print(row)
#cursor.execute("DROP TABLE hospitalization")
#row = cursor.execute("SELECT * FROM hospitalization")
#print(row)
#cursor.execute("DROP TABLE deaths")
#row = cursor.execute("SELECT * FROM deaths")
#print(row)
#cursor.execute("DROP TABLE missing")
#row = cursor.execute("SELECT * FROM missing")
#print(row)


#cursor.execute("INSERT INTO cases (cases_date,district,new_cases,update_date) VALUES(?,?,?,?,?)",(date_cases,),('Swakopmund',),(80,),(datenow_isoformat,))
#cursor.execute("INSERT INTO districts (district,region) VALUES('Okahao', 'Omusati')")
#cursor.execute("INSERT INTO cases (cases_date,district,new_cases,update_date) VALUES(?,?,?,?)",(date_cases,'Windhoek',135,datenow))
#new_date = datetime.strptime('2021-01-26', '%Y-%m-%d').date()
date1 = datetime.strptime('2022-02-05', '%Y-%m-%d').date()
#cursor.execute("UPDATE deaths SET publish_date = ? WHERE publish_date = ?",(new_date, date1,))
 
cursor.execute("DELETE FROM missing WHERE missing_date = ?", (date1,))
#cursor.execute("UPDATE districts SET district = ? WHERE district = ?", ('Walvis Bay','Walvisbay',))

#target_name="Kavango East"
#cursor.execute("DELETE FROM cases WHERE district = ?", (target_name,))
#text1="unkonwn"
#text2="unknown"

#cursor.execute("DELETE FROM districts WHERE district = ?", (target_name,))

#cursor.execute("DELETE FROM deaths WHERE district = ? AND publish_date = ?", (target_name,date1,))
#cursor.execute("DELETE FROM hospitalization WHERE hospital_date = ? AND region = ?", (date1,target_name,))
#cursor.execute("DELETE FROM recoveries WHERE recoveries_date = ? ", (date1,))
#cursor.execute("DELETE FROM deaths WHERE publish_date = ?", (date1,))
#cursor.execute("UPDATE recoveries SET region = ? WHERE region = ? ", (text2,text1))
#print(rows)

"""
"""

"""
target_name = "Mariental"
cursor.execute("DELETE FROM cases WHERE district = ?", (target_name,))
"""
#new_cases = cursor.execute("SELECT * FROM cases WHERE cases_date =?",("2021-05-18",)).fetchall()

"""       
#print(new_cases)
display_date = datetime.strptime('2020-09-17', '%Y-%m-%d').date()
update_list=[]
daily_all_cases=cursor.execute("SELECT region,SUM(new_cases) FROM cases JOIN districts ON cases.district = districts.district WHERE cases_date <= ? GROUP BY region", (display_date,)).fetchall()
print(daily_all_cases)
print("")
daily_all_cases=cursor.execute("SELECT region,SUM(new_recoveries) FROM recoveries WHERE recoveries_date <= ? GROUP BY region", (display_date,)).fetchall()
print(daily_all_cases)
print("")
daily_all_cases=cursor.execute("SELECT region,COUNT(age) FROM deaths JOIN districts ON deaths.district = districts.district WHERE publish_date <= ? GROUP BY region", (display_date,)).fetchall()
print(daily_all_cases)
"""


"""
update_list.append(daily_all_cases[0]['SUM(new_cases)'])
        
        daily_all_recoveries=db.execute("SELECT SUM(new_recoveries) FROM recoveries WHERE recoveries_date <= ? ", display_date)
        update_list.append(daily_all_recoveries[0]['SUM(new_recoveries)'])
        
        daily_all_deaths=db.execute("SELECT COUNT(*) FROM deaths WHERE publish_date <= ? ", display_date)
       
        if daily_all_recoveries:
            daily_active_cases=daily_all_cases[0]['SUM(new_cases)']-daily_all_recoveries[0]['SUM(new_recoveries)']
            if daily_all_deaths:
                daily_active_cases=daily_active_cases-daily_all_deaths[0]['COUNT(*)']
            update_list.append(daily_active_cases)
        else:
           update_list.append(daily_all_cases[0]['SUM(new_cases)'])

        daily_all_deaths=db.execute("SELECT COUNT(*) FROM deaths WHERE publish_date <= ? ", display_date)
        update_list.append(daily_all_deaths[0]['COUNT(*)'])


"""
"""

rows = cursor.execute("SELECT * FROM cases").fetchall()
print(rows)
for row in rows:
	print (row[0])
	print (row[1])
	print (row[2]) 
	print (row[3]) 
	print (row[4])   
"""

"""
target_name = "Swakopmund"
cursor.execute("DELETE FROM districts WHERE district = ?", (target_name,))
rows = cursor.execute("SELECT district, region FROM districts").fetchall()
print(rows)
"""


"""
new_tank_number = 2
moved_fish_name = "Sammy"
cursor.execute(
    "UPDATE fish SET tank_number = ? WHERE name = ?",
    (new_tank_number, moved_fish_name)
)
"""
connection.commit()
connection.close()
