import os
#import sqlite3
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from pytz import timezone
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///covid19_Nam.db")



@app.route("/",methods=["GET", "POST"])
@login_required
def index():
    
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    #date_cases = datetime.strptime('2021-05-18', '%Y-%m-%d').date()
    if request.method == "POST":
        district_list=[]
        temp = db.execute("SELECT DISTINCT district FROM districts")
        for d in temp:
            district_list.append(d['district'])
        district_list.append('unknown') 
        region_list=[]
        temp = db.execute("SELECT DISTINCT region FROM districts")
        for d in temp:
            region_list.append(d['region'])
        region_list.append("unknown")  

        if request.form.get("act_date"):
            try:
                new_date_str=request.form.get("act_date")
                new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
                db.execute("UPDATE active_date SET active_date = :active_date WHERE id = :id", active_date=new_date, id=1)
            except:
                return apology("error with date", 400)
            row = db.execute("SELECT * FROM active_date")
            new_date_str=row[0]['active_date']
            new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        else:
            #new_date=now.date().strftime('%Y-%m-%d')
            new_date=now.date()
            db.execute("UPDATE active_date SET active_date = :active_date WHERE id = :id", active_date=new_date, id=0)

        if request.form.get('cases') == 'New cases':
            db.execute("CREATE TABLE IF NOT EXISTS cases(id INTEGER PRIMARY KEY, cases_date TEXT NOT NULL, district TEXT NOT NULL, new_cases INTEGER, update_date TEXT NOT NULL)")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_cases ON cases (cases_date,district)")   
            rows = db.execute("SELECT * FROM cases JOIN districts ON cases.district = districts.district WHERE cases_date LIKE ? ORDER BY new_cases DESC",new_date)
            return render_template("add_cases.html",new_date=new_date,district_list=district_list,new_cases=rows,now=now)
        
        elif request.form.get('recoveries') == 'New recoveries':
            db.execute("CREATE TABLE IF NOT EXISTS recoveries(id INTEGER PRIMARY KEY, recoveries_date TEXT NOT NULL,region TEXT NOT NULL, new_recoveries INTEGER, update_date TEXT NOT NULL)")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_recoveries ON recoveries (recoveries_date,region)")   
            rows = db.execute("SELECT * FROM recoveries  WHERE recoveries_date LIKE ? ORDER BY new_recoveries DESC",new_date)
            return render_template("add_recoveries.html",new_date=new_date,region_list=region_list,new_recoveries=rows,now=now)

        elif request.form.get('hospital') == 'Hospitalization':
            db.execute("CREATE TABLE IF NOT EXISTS hospitalization(id INTEGER PRIMARY KEY, hospital_date TEXT NOT NULL, region TEXT NOT NULL, hospital_cases INTEGER, icu_cases INTEGER, high_care INTEGER,update_date TEXT NOT NULL)")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_hospital ON hospitalization (hospital_date,region)")   
            #db.execute("ALTER TABLE hospitalization ADD high_care INTEGER")

            rows = db.execute("SELECT * FROM hospitalization WHERE hospital_date LIKE ? ORDER BY hospital_cases DESC",new_date)
            return render_template("add_hospitalization.html",new_date=new_date,region_list=region_list,new_hospitalization=rows,now=now)

        elif request.form.get('deaths') == 'Deaths':
            db.execute("CREATE TABLE IF NOT EXISTS deaths(id INTEGER PRIMARY KEY, publish_date TEXT NOT NULL, district TEXT NOT NULL, sex TEXT NOT NULL, age INTEGER, comorbidities TEXT NOT NULL, death_date TEXT NOT NULL, classification TEXT NOT NULL, update_date TEXT NOT NULL)")
            rows = db.execute("SELECT * FROM deaths WHERE publish_date LIKE ? ORDER BY id",new_date)
            return render_template("add_deaths.html",new_date=new_date,district_list=district_list,new_deaths=rows,now=now)
        
        elif request.form.get('missing') == 'Missing':
            db.execute("CREATE TABLE IF NOT EXISTS missing(id INTEGER PRIMARY KEY, missing_date TEXT NOT NULL, missing_cases INTEGER)")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_missing ON missing (missing_date)")   
            rows = db.execute("SELECT * FROM missing WHERE missing_date <= ?",new_date)
            return render_template("missing_cases.html",new_date=new_date,missing_cases=rows)

        else:
            return redirect ("/")
   
    else:
        row = db.execute("SELECT * FROM active_date")
        act_date_str=row[0]['active_date']
        act_date = datetime.strptime(act_date_str, '%Y-%m-%d').date()
        return render_template("index.html", now=now,act_date=act_date)
           

@app.route("/add_district", methods=["GET", "POST"])
@login_required
def add_district():
    if request.method == "POST":
        existing_districts=[]
        rows= db.execute("SELECT district FROM districts")
        for d in rows:
            existing_districts.append(d["district"])
            print(d["district"])
        if not request.form.get("district"):
            return apology("must provide district", 400)
        if not request.form.get("region"):
            return apology("must provide region", 400)
        if request.form.get("district") in existing_districts:
            return apology("district already exists", 400)
        else:
            db.execute("INSERT INTO districts(district,region) VALUES (?,?)",
                       request.form.get("district"), request.form.get("region"))
        districts = db.execute("SELECT * FROM districts ORDER BY region,district")
        return render_template("add_district.html",districts=districts)
    else:
        db.execute("CREATE TABLE IF NOT EXISTS districts(id INTEGER PRIMARY KEY, district TEXT NOT NULL, region TEXT NOT NULL)")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_districts ON districts (district)")  
        districts = db.execute("SELECT * FROM districts ORDER BY region,district")
        return render_template("add_district.html",districts=districts)

@app.route("/add_cases", methods=["GET", "POST"])
@login_required
def add_cases():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    #currentdatetime=now.strftime("%A, %d %B %Y %H:%M")
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        
    if request.method == "POST":
        if not request.form.get("district"):
            return apology("must provide district", 400)
        if not request.form.get("new_cases"):
            no_cases=0
        else:
            no_cases=int(request.form.get("new_cases"))
        district = request.form.get("district")
        check=db.execute("SELECT * FROM cases WHERE cases_date LIKE ? AND district LIKE ? ", new_date,district)
        if len(check)== 1:
            return render_template("update_cases.html",new_date=new_date,check=check[0],now=now)

        db.execute("INSERT INTO cases(cases_date,district,new_cases,update_date) VALUES (?,?,?,?)", new_date,district,no_cases,date_now)
        
        district_list=[]
        temp = db.execute("SELECT DISTINCT district FROM districts")
        for d in temp:
            district_list.append(d['district'])
        district_list.append('unknown') 
        rows = db.execute("SELECT * FROM cases JOIN districts ON cases.district = districts.district WHERE cases_date LIKE ? ORDER BY new_cases DESC", new_date)
        return render_template("add_cases.html",new_date=new_date,district_list=district_list,new_cases=rows,now=now)

    else:
        district_list=[]
        temp = db.execute("SELECT DISTINCT district FROM districts")
        for d in temp:
            district_list.append(d['district'])
        district_list.append('unknown') 
        rows = db.execute("SELECT * FROM cases JOIN districts ON cases.district = districts.district WHERE cases_date LIKE ? ORDER BY new_cases DESC", new_date)
        return render_template("add_cases.html",new_date=new_date,district_list=district_list,new_cases=rows,now=now)


@app.route("/add_recoveries", methods=["GET", "POST"])
@login_required
def add_recoveries():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    region_list=[]
    temp = db.execute("SELECT DISTINCT region FROM districts")
    for d in temp:
        region_list.append(d['region'])  
    region_list.append("unknown")

    if request.method == "POST":
        if not request.form.get("region"):
            return apology("must provide region", 400)
        if not request.form.get("new_recoveries"):
            no_recoveries=0
        else:
            no_recoveries=int(request.form.get("new_recoveries"))
        region = request.form.get("region")
 
        check=db.execute("SELECT * FROM recoveries WHERE recoveries_date LIKE ? AND region LIKE ? ", new_date,region)
        
        if len(check)== 1:
            return render_template("update_recoveries.html",new_date=new_date,check=check[0],now=now)

        db.execute("INSERT INTO recoveries(recoveries_date,region,new_recoveries,update_date) VALUES (?,?,?,?)", new_date,region,no_recoveries,date_now)
        
        rows = db.execute("SELECT * FROM recoveries WHERE recoveries_date LIKE ? ORDER BY new_recoveries DESC", new_date)
        return render_template("add_recoveries.html",new_date=new_date,region_list=region_list,new_recoveries=rows,now=now)

    else:
        rows = db.execute("SELECT * FROM recoveries WHERE recoveries_date LIKE ? ORDER BY new_recoveries DESC", new_date)
        return render_template("add_recoveries.html",new_date=new_date,region_list=region_list,new_recoveries=rows,now=now)



@app.route("/add_hospitalization", methods=["GET", "POST"])
@login_required
def add_hospitalization():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    region_list=[]
    temp = db.execute("SELECT DISTINCT region FROM districts")
    for d in temp:
        region_list.append(d['region']) 
    region_list.append("unknown")

    if request.method == "POST":
        if not request.form.get("region"):
            return apology("must provide region", 400)
        if not request.form.get("new_hospital_cases"):
            no_hospital_cases=0
        else:
            no_hospital_cases=int(request.form.get("new_hospital_cases"))
        if not request.form.get("new_icu_cases"):
            no_icu_cases=0
        else:
            no_icu_cases=int(request.form.get("new_icu_cases"))
        if not request.form.get("high_care"):
            no_high_care=0
        else:
            no_high_care=int(request.form.get("high_care"))
        region = request.form.get("region")
 
        check=db.execute("SELECT * FROM hospitalization WHERE hospital_date LIKE ? AND region LIKE ? ", new_date,region)
        
        if len(check)== 1:
            return render_template("update_hospitalization.html",new_date=new_date,check=check[0],now=now)

        db.execute("INSERT INTO hospitalization(hospital_date,region,hospital_cases,icu_cases,high_care,update_date) VALUES (?,?,?,?,?,?)", new_date,region,no_hospital_cases,no_icu_cases,no_high_care,date_now)
        
        rows = db.execute("SELECT * FROM hospitalization WHERE hospital_date LIKE ? ORDER BY hospital_cases DESC", new_date)
        return render_template("add_hospitalization.html",new_date=new_date,region_list=region_list,new_hospitalization=rows,now=now)

    else:
        rows = db.execute("SELECT * FROM hospitalization WHERE hospital_date LIKE ? ORDER BY hospital_cases DESC", new_date)
        return render_template("add_hospitalization.html",new_date=new_date,region_list=region_list,new_hospitalization=rows,now=now)

@app.route("/add_deaths", methods=["GET", "POST"])
@login_required
def add_deaths():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    #currentdatetime=now.strftime("%A, %d %B %Y %H:%M")
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    #new_date=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    district_list=[]
    temp = db.execute("SELECT DISTINCT district FROM districts")
    for d in temp:
        district_list.append(d['district'])
    district_list.append('unknown') 

    if request.method == "POST":
        if request.form.get('delete_death') == 'Delete Death':
            rows = db.execute("SELECT * FROM deaths WHERE publish_date LIKE ? ORDER BY id",new_date)
            return render_template("delete_death.html",new_date=new_date,district_list=district_list,new_deaths=rows)
        if request.form.get('add') == 'Add':
            if not request.form.get("district"):
                return apology("must provide district", 400)
            #if not request.form.get("age"):
            #    return apology("must provide age", 400)
            if not request.form.get("death_date"):
                return apology("must provide date of death", 400)
            district = request.form.get("district")
            sex=request.form.get("sex")
            age=request.form.get("age")
            comorbidities=request.form.get("comorbidities")
            death_date=datetime.strptime(request.form.get("death_date"), '%Y-%m-%d').date()
            if death_date > new_date:
                return apology("wrong date", 400)
            classification=request.form.get("classification")
            db.execute("INSERT INTO deaths(publish_date,district,sex,age,comorbidities,death_date,classification,update_date) VALUES (?,?,?,?,?,?,?,?)", new_date,district,sex,age,comorbidities,death_date,classification,date_now)
            rows = db.execute("SELECT * FROM deaths WHERE publish_date LIKE ? ORDER BY id", new_date)
            return render_template("add_deaths.html",new_date=new_date,district_list=district_list,new_deaths=rows,now=now)

    else:
        
        rows = db.execute("SELECT * FROM deaths WHERE publish_date LIKE ? ORDER BY id", new_date)
        return render_template("add_deaths.html",new_date=new_date,district_list=district_list,new_deaths=rows,now=now)



@app.route("/update_cases", methods=["GET", "POST"])
@login_required
def update_cases():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    
    if request.method == "POST":
        if not request.form.get("district"):
            return apology("must provide district", 400)
        if not request.form.get("new_cases"):
            no_cases=0
        else:
            no_cases=int(request.form.get("new_cases"))
        district= request.form.get("district")
        db.execute("UPDATE cases SET new_cases = :new_cases WHERE district = :district AND cases_date LIKE :cases_date",
                           new_cases=no_cases, district=district, cases_date=new_date)
        rows = db.execute("SELECT * FROM cases JOIN districts ON cases.district = districts.district WHERE cases_date LIKE ? ORDER BY new_cases DESC", new_date)
        district_list=[]
        temp = db.execute("SELECT DISTINCT district FROM districts")
        for d in temp:
            district_list.append(d['district'])
        district_list.append('unknown')
        return render_template("add_cases.html",new_date=new_date,district_list=district_list,new_cases=rows,now=now)
   
    else:
        rows = db.execute("SELECT * FROM cases WHERE cases_date LIKE ?", new_date)
        return render_template("update_cases.html",new_date=new_date,new_cases=rows,now=now)


@app.route("/update_recoveries", methods=["GET", "POST"])
@login_required
def update_recoveries():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()

    if request.method == "POST":
        if not request.form.get("region"):
            return apology("must provide region", 400)
        if not request.form.get("new_recoveries"):
            no_recoveries=0
        else:
            no_recoveries=int(request.form.get("new_recoveries"))
        region= request.form.get("region")
        
        db.execute("UPDATE recoveries SET new_recoveries = :new_recoveries WHERE region = :region AND recoveries_date LIKE :recoveries_date",
                           new_recoveries=no_recoveries, region=region, recoveries_date=new_date)
        rows = db.execute("SELECT * FROM recoveries WHERE recoveries_date LIKE ? ORDER BY new_recoveries DESC", new_date)
        return render_template("add_recoveries.html",new_date=new_date,new_recoveries=rows,now=now)

    else:
        rows = db.execute("SELECT * FROM recoveries WHERE recoveries_date LIKE ?", new_date)
        return render_template("update_recoveries.html",new_date=new_date,new_recoveries=rows,now=now)


@app.route("/update_hospitalization", methods=["GET", "POST"])
@login_required
def update_hospitalization():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    region_list=[]
    temp = db.execute("SELECT DISTINCT region FROM districts")
    for d in temp:
        region_list.append(d['region'])
    region_list.append("unknown")


    if request.method == "POST":
        if not request.form.get("region"):
            return apology("must provide region", 400)
        if not request.form.get("new_hospital_cases"):
            no_hospital_cases=0
        else:
            no_hospital_cases=int(request.form.get("new_hospital_cases"))
        print('here:',no_hospital_cases)
        if not request.form.get("new_icu_cases"):
            no_icu_cases=0
        else:
            no_icu_cases=int(request.form.get("new_icu_cases"))
        if not request.form.get("high_care"):
            no_high_care=0
        else:
            no_high_care=int(request.form.get("high_care"))
        region= request.form.get("region")
        

        #print(region,no_hospital_cases,no_icu_cases)
        db.execute("UPDATE hospitalization SET hospital_cases = :hospital_cases WHERE region = :region AND hospital_date = :hospital_date",
                           hospital_cases=no_hospital_cases, region=region, hospital_date=new_date)
        db.execute("UPDATE hospitalization SET icu_cases = :icu_cases WHERE region = :region AND hospital_date = :hospital_date",
                           icu_cases=no_icu_cases, region=region, hospital_date=new_date)
        db.execute("UPDATE hospitalization SET high_care = :high_care WHERE region = :region AND hospital_date = :hospital_date",
                           high_care=no_high_care, region=region, hospital_date=new_date)
        rows = db.execute("SELECT * FROM hospitalization WHERE hospital_date = ? ORDER BY hospital_cases DESC", new_date)
        print(rows)
        return render_template("add_hospitalization.html",new_date=new_date,region_list=region_list,new_hospitalization=rows,now=now)

    else:
        
        rows = db.execute("SELECT * FROM hospitalization WHERE hospital_date LIKE ?", new_date)
        return render_template("update_hospitalization.html",new_date=new_date,new_hospitalization=rows,now=now)

@app.route("/delete_death", methods=["GET", "POST"])
@login_required
def delete_death():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()

    if request.method == "POST":
        if not request.form.get("id"):
            return apology("must provide id", 400)
        id_to_delete= request.form.get("id")

        district_list=[]
        temp = db.execute("SELECT DISTINCT district FROM districts")
        for d in temp:
            district_list.append(d['district'])
        district_list.append('unknown')
        db.execute("DELETE FROM deaths WHERE id = :id AND publish_date = :publish_date",
                            id=id_to_delete, publish_date=new_date)
        rows = db.execute("SELECT * FROM deaths WHERE publish_date LIKE ? ORDER BY id", new_date)
        return render_template("add_deaths.html",new_date=new_date,district_list=district_list,new_deaths=rows,now=now)
    else:
        rows = db.execute("SELECT * FROM deaths WHERE publish_date LIKE ? ORDER BY id", new_date)
        return render_template("delete_death.html",new_date=new_date,new_deaths=rows)


@app.route("/summary", methods=["GET", "POST"])
@login_required
def summary():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    row=db.execute("SELECT MAX(cases_date) FROM cases")
    last_date_str=row[0]['MAX(cases_date)']
    last_date=datetime.strptime(last_date_str, '%Y-%m-%d').date() 
    print(type(last_date))
    if request.method == "POST":
        if request.form.get("display_date"):
            try:
                display_date_str=request.form.get("display_date")
                display_date = datetime.strptime(display_date_str, '%Y-%m-%d').date()
            except:
                return apology("error with date", 400)
            if display_date>last_date:
                return apology("no update available for that day", 400)
        else: display_date=last_date
        daily_list=[]
        daily_new_cases=db.execute("SELECT SUM(new_cases) FROM cases WHERE cases_date LIKE ? ", display_date)
        daily_list.append(daily_new_cases[0]['SUM(new_cases)'])
        
        daily_new_recoveries=db.execute("SELECT SUM(new_recoveries) FROM recoveries WHERE recoveries_date LIKE ? ", display_date)
        daily_list.append(daily_new_recoveries[0]['SUM(new_recoveries)'])
        
        daily_new_deaths=db.execute("SELECT COUNT(*) FROM deaths WHERE publish_date LIKE ? ", display_date)
        daily_list.append(daily_new_deaths[0]['COUNT(*)'])
       
        update_list=[]
        daily_all_cases=db.execute("SELECT SUM(new_cases) FROM cases WHERE cases_date <= ? ", display_date)
        update_list.append(daily_all_cases[0]['SUM(new_cases)'])
        
        daily_all_recoveries=db.execute("SELECT SUM(new_recoveries) FROM recoveries WHERE recoveries_date <= ? ", display_date)
        update_list.append(daily_all_recoveries[0]['SUM(new_recoveries)'])
        
        daily_all_deaths=db.execute("SELECT COUNT(*) FROM deaths WHERE publish_date <= ? ", display_date)
       
        missing_cases=db.execute("SELECT SUM(missing_cases) FROM missing WHERE missing_date <= ? ", display_date)

        if daily_all_recoveries:
            daily_active_cases=daily_all_cases[0]['SUM(new_cases)']-daily_all_recoveries[0]['SUM(new_recoveries)']
            if daily_all_deaths:
                daily_active_cases=daily_active_cases-daily_all_deaths[0]['COUNT(*)']
            if missing_cases:
                daily_active_cases=daily_active_cases-missing_cases[0]['SUM(missing_cases)']
            update_list.append(daily_active_cases)
        else:
           update_list.append(daily_all_cases[0]['SUM(new_cases)'])

        daily_all_deaths=db.execute("SELECT COUNT(*) FROM deaths WHERE publish_date <= ? ", display_date)
        update_list.append(daily_all_deaths[0]['COUNT(*)'])

        return render_template("summary.html",last_date=last_date,display_date=display_date,daily_list=daily_list,update_list=update_list,now=now)

    else:
        
        row = db.execute("SELECT * FROM active_date")
        act_date_str=row[0]['active_date']
        act_date = datetime.strptime(act_date_str, '%Y-%m-%d').date()
        display_date=act_date

        #display_date=last_date

        daily_list=[]
        daily_new_cases=db.execute("SELECT SUM(new_cases) FROM cases WHERE cases_date LIKE ? ", display_date)
        daily_list.append(daily_new_cases[0]['SUM(new_cases)'])
        
        daily_new_recoveries=db.execute("SELECT SUM(new_recoveries) FROM recoveries WHERE recoveries_date LIKE ? ", display_date)
        daily_list.append(daily_new_recoveries[0]['SUM(new_recoveries)'])
        
        daily_new_deaths=db.execute("SELECT COUNT(*) FROM deaths WHERE publish_date LIKE ? ", display_date)
        daily_list.append(daily_new_deaths[0]['COUNT(*)'])

        update_list=[]
        daily_all_cases=db.execute("SELECT SUM(new_cases) FROM cases WHERE cases_date <= ? ", display_date)
        update_list.append(daily_all_cases[0]['SUM(new_cases)'])
        
        daily_all_recoveries=db.execute("SELECT SUM(new_recoveries) FROM recoveries WHERE recoveries_date <= ? ", display_date)
        update_list.append(daily_all_recoveries[0]['SUM(new_recoveries)'])

        daily_all_deaths=db.execute("SELECT COUNT(*) FROM deaths WHERE publish_date <= ? ", display_date)
   
        missing_cases=db.execute("SELECT SUM(missing_cases) FROM missing WHERE missing_date <= ? ", display_date)

        if daily_all_recoveries:
            daily_active_cases=daily_all_cases[0]['SUM(new_cases)']-daily_all_recoveries[0]['SUM(new_recoveries)']
            if daily_all_deaths:
                daily_active_cases=daily_active_cases-daily_all_deaths[0]['COUNT(*)']
            if missing_cases:
                daily_active_cases=daily_active_cases-missing_cases[0]['SUM(missing_cases)']
            update_list.append(daily_active_cases)
        else:
           update_list.append(daily_all_cases[0]['SUM(new_cases)'])

        daily_all_deaths=db.execute("SELECT COUNT(*) FROM deaths WHERE publish_date <= ? ", display_date)
        update_list.append(daily_all_deaths[0]['COUNT(*)'])


        #daily_list=[5,3,56,45]
        return render_template("summary.html",last_date=last_date,display_date=display_date,daily_list=daily_list,update_list=update_list,now=now)



@app.route("/missing_cases", methods=["GET", "POST"])
@login_required
def missing_cases():
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    
    if request.method == "POST":
        if request.form.get("missing_cases"):
            no_cases=int(request.form.get("missing_cases"))
        else:
            no_cases=0   

        db.execute("INSERT INTO missing(missing_date,missing_cases) VALUES (?,?)", new_date,no_cases)
        rows = db.execute("SELECT * FROM missing WHERE missing_date <= ?",new_date)
        return render_template("missing_cases.html",new_date=new_date,missing_cases=rows)
    else:
        rows = db.execute("SELECT * FROM missing WHERE missing_date <= ?",new_date)
        return render_template("missing_cases.html",new_date=new_date,missing_cases=rows)




@app.route("/temp_cases")
@login_required
def temp_cases():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    #currentdatetime=now.strftime("%A, %d %B %Y %H:%M")
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        
    rows = db.execute("SELECT * FROM cases ORDER BY cases_date")
    return render_template("temp_cases.html",all_cases=rows,now=now)


@app.route("/temp_recoveries")
@login_required
def temp_recoveries():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    #currentdatetime=now.strftime("%A, %d %B %Y %H:%M")
    row = db.execute("SELECT * FROM active_date")
    new_date_str=row[0]['active_date']
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    
    rows = db.execute("SELECT * FROM recoveries ORDER BY recoveries_date")
    return render_template("temp_recoveries.html",all_recoveries=rows,now=now)


@app.route("/temp_deaths")
@login_required
def temp_deaths():
    now=datetime.now(timezone("Africa/Johannesburg"))
    date_now=now.date()
    #currentdatetime=now.strftime("%A, %d %B %Y %H:%M")
    
    rows = db.execute("SELECT * FROM deaths ORDER BY publish_date")
    return render_template("temp_deaths.html",all_deaths=rows,now=now)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        #   Ensure username doesn't exist
        if len(rows) == 1:
            return apology("username already exists", 400)

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure username doesn't exist
        elif len(rows) == 1:
            return apology("username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure confirmation was submitted
        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("password and confirmation don't match", 400)

        # add user to users
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"),
                   generate_password_hash(request.form.get("password")))

        return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
