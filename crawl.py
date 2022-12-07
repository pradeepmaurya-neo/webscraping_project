from flask import Flask, send_file, jsonify, url_for
from flask import redirect, request, session, render_template
import os
from celery import Celery
from celery.states import state, PENDING, SUCCESS
from flask_session import Session
import pandas as pd
from celery.result import AsyncResult
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from login_required_decorator import login_required
import csv
# import mysql.connector
from flask_migrate import Migrate
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import functools
import argparse

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
#celery = Celery(app.name, broker='redis://localhost:6379/0')
celery.conf.update(app.config)
sess = Session()
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345@localhost/scrap'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scrapper.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

"""
Driver
"""
"""
DEBUG_DESCRIPTION='Puts script in a \'debug\' mode where the Chrome GUI is visible'
DEBUG_DISABLED = False
DEBUG_ENABLED = True
MAILTM_DESCRIPTION='Uses mail.tm instead of guerrilla mail by default'
MAILTM_DISABLED = False
MAILTM_ENABLED = True
EPILOG = 'Kellogg bad | Union good | Support strike funds '
SCRIPT_DESCRIPTION=''
printf = functools.partial(print, flush=True)
parser = argparse.ArgumentParser(SCRIPT_DESCRIPTION, epilog=EPILOG)
parser.add_argument('--debug',action='store_true', default=DEBUG_DISABLED,required=False,help=DEBUG_DESCRIPTION,dest='debug')
parser.add_argument('--mailtm',action='store_true', default=MAILTM_DISABLED,required=False,help=MAILTM_DESCRIPTION,dest='mailtm')
args = parser.parse_args()
options = webdriver.ChromeOptions()
if (args.debug == DEBUG_DISABLED):
    options.add_argument('disable-blink-features=AutomationControlled')
    options.headless = True
    driver = webdriver.Chrome(executable_path="C:\Program Files\Google\chromedriver\chromedriver.exe", options=options)
    driver.set_window_size(1440, 900)
elif (args.debug == DEBUG_ENABLED):
    driver = webdriver.Chrome(executable_path="C:\Program Files\Google\chromedriver\chromedriver.exe")
"""


options = webdriver.ChromeOptions()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument("--headless")
# options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
# options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
driver=webdriver.Remote(command_executor='http://chrome:4444/wd/hub',desired_capabilities=DesiredCapabilities.CHROME)
# driver = webdriver.Chrome(executable_path="C:\Program Files\Google\chromedriver\chromedriver.exe", options=options)
# driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())

"""
Dice Crawler
"""
@celery.task(bind=True)
def extract_dice_jobs(self, tech, location, page=1):
    FILE_NAME = 'dice.csv'
    driver.maximize_window()
    time.sleep(3)
    job_titles_list, company_name_list, location_list, job_types_list = [], [], [], []
    job_posted_dates_list, job_descriptions_list = [], []
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    for k in range(1, int(page)):
        URL = f"https://www.dice.com/jobs?q={tech}&location={location}&radius=30&radiusUnit=mi&page={k}&pageSize=20&language=en&eid=S2Q_,bw_1"
        driver.get(URL)
        driver.maximize_window()
        try:
            input = driver.find_element(By.ID, "typeaheadInput")
            input.click()
        except:
            time.sleep(5)

        job_titles = driver.find_elements(By.CLASS_NAME, "card-title-link")
        company_name = driver.find_elements(
            By.XPATH, '//div[@class="card-company"]/a')
        job_locations = driver.find_elements(
            By.CLASS_NAME, "search-result-location")
        job_types = driver.find_elements(
            By.XPATH, '//span[@data-cy="search-result-employment-type"]')
        job_posted_dates = driver.find_elements(By.CLASS_NAME, "posted-date")
        job_descriptions = driver.find_elements(By.CLASS_NAME, "card-description")

        # company_name
        for i in company_name:
            company_name_list.append(i.text)

        # job titles list
        for i in job_titles:
            job_titles_list.append(i.text)

        # #locations
        for i in job_locations:
            location_list.append(i.text)

        # job types
        for i in job_types:
            job_types_list.append(i.text)

        # job posted dates
        for i in job_posted_dates:
            job_posted_dates_list.append(i.text)

        # job_descriptions
        for i in job_descriptions:
            job_descriptions_list.append(i.text)
        #progress_recorder.set_progress(k+1, page,f'on iteration {k}')
        print(len(job_titles_list), len(job_descriptions_list),
              len(job_posted_dates_list), len(job_types_list),
              len(company_name_list), len(location_list))
        df = pd.DataFrame()
        df['Job Title'] = job_titles_list
        df['Company Name'] = company_name_list
        df['description'] = job_descriptions_list
        df['Posted Date'] = job_posted_dates_list
        df['Job Type'] = job_types_list
        df['Location'] = location_list
        df.to_csv(f'./static/{FILE_NAME}', index=False)
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS', meta={'current': k, 'total': page, 'status': message})
    return {'current': 100, 'total': 100, 'status': 'Task completed!'}

"""
Indeed.com crawler
"""

job_detail_links = []
job_posted_dates_list, job_descriptions_list = [], []
description_list, company_name_list, designation_list, salary_list, company_url = [], [], [], [], []
location_list, qualification_list = [], []
BASE_URL = 'https://in.indeed.com'

def get_job_detail_links(tech, location, page):

    for page in range(0, page):
        time.sleep(5)
        URL = f"https://in.indeed.com/jobs?q={tech}&l={location}&start={page * 10}"
        try:
            driver.get(URL)
        except WebDriverException:
            print("page down")

        soup = BeautifulSoup(driver.page_source, 'lxml')

        for outer_artical in soup.findAll(attrs={'class': "css-1m4cuuf e37uo190"}):
            for inner_links in outer_artical.findAll(
                    attrs={'class': "jobTitle jobTitle-newJob css-bdjp2m eu4oa1w0"}):
                job_detail_links.append(
                    f"{BASE_URL}{inner_links.a.get('href')}")


@celery.task(bind=True)
def scrap_details(self, tech, location, page):
    print("___________", "Indeed")
    message = ''
    get_job_detail_links(tech, location, page)
    time.sleep(2)

    for link in range(len(job_detail_links)):
        print("inside job_detail_links")
        time.sleep(5)
        driver.get(job_detail_links[link])
        soup = BeautifulSoup(driver.page_source, 'lxml')
        a = soup.findAll(
            attrs={'class': "jobsearch-InlineCompanyRating-companyHeader"})
        company_name_list.append(a[1].text)
        try:
            company_url.append(a[1].a.get('href'))
        except:
            company_url.append('NA')

        salary = soup.findAll(
            attrs={'class': "jobsearch-JobMetadataHeader-item"})
        if salary:
            for i in salary:
                x = i.find('span')
                if x:
                    salary_list.append(x.text)
                else:
                    salary_list.append('NA')
        else:
            salary_list.append('NA')

        description = soup.findAll(
            attrs={'class': "jobsearch-jobDescriptionText"})

        if description:
            for i in description:
                description_list.append(i.text)
        else:
            description_list.append('NA')

        designation = soup.findAll(
            attrs={'class': 'jobsearch-JobInfoHeader-title-container'})
        if designation:
            designation_list.append(designation[0].text)
        else:
            designation_list.append('NA')
        for Tag in soup.find_all('div', class_="icl-Ratings-count"):
            Tag.decompose()
        for Tag in soup.find_all('div', class_="jobsearch-CompanyReview--heading"):
            Tag.decompose()
        location = soup.findAll(
            attrs={'class': "jobsearch-CompanyInfoWithoutHeaderImage"})
        if location:
            for i in location:
                location_list.append(i.text)
        else:
            location_list.append('NA')

            # Qualification
        qualification = soup.findAll(
            attrs={"class": 'jobsearch-ReqAndQualSection-item--wrapper'})
        if qualification:
            for i in qualification:
                qualification_list.append(i.text)
        else:
            qualification_list.append('NA')


        FILE_NAME = 'indeed.csv'
        df = pd.DataFrame()
        df['Company Name'] = company_name_list
        df['Company_url'] = company_url
        df['salary'] = salary_list
        # df['description_list'] = description_list
        df['designation_list'] = designation_list
        df['location_list'] = location_list
        df['qualification_list'] = qualification_list
        df.to_csv(f'./static/{FILE_NAME}', index=False)
        save_indeed_data_to_db()
        verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
        adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
        noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']

        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                          random.choice(adjective),
                                          random.choice(noun))
        self.update_state(state='PROGRESS', meta={'current': link, 'total': len(job_detail_links), 'status': message})
    return {'current': 100, 'total': 100, 'status': 'Task completed!'}


"""
Naukari.com Crawler
"""
BASE_URL_naukari = 'https://www.naukri.com/'
job_detail_links_naukari = []
description_list_naukari, company_name_list_naukari, designation_list_naukari, salary_list_naukari, company_url_naukari = [], [], [], [], []
location_list_naukari, qualification_list_naukari = [], []
FILE_NAME = 'naukri.csv'
def get_job_detail_links_naukari(tech, location, page):

    for page_no in range(0, page):
        print("-----------------in job link")
        URL = f"https://www.naukri.com/python-jobs-in-{location}-{page_no}?k={tech}&l={location}"
        driver.get(URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        for outer_artical in soup.findAll(attrs={'class': "jobTuple bgWhite br4 mb-8"}):
            for inner_links in outer_artical.find(attrs={'class': "jobTupleHeader"}).findAll(
                    attrs={'class': "title fw500 ellipsis"}):
                job_detail_links_naukari.append(inner_links.get('href'))


@celery.task(bind=True)
def scrap_naukari(self, tech, location, page):
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    print("-----------------above job link")
    get_job_detail_links_naukari(tech, location, page)
    print("-----------------below job link")
    designation_list_naukari, company_name_list_naukari, experience_list, salary_list__naukari = [], [], [], []
    location_list__naukari, job_description_list, role_list, industry_type_list = [], [], [], []
    functional_area_list, employment_type_list, role_category_list, education_list = [], [], [], []
    key_skill_list, about_company_list, address_list, post_by_list = [], [], [], []
    post_date_list, website_list, url_list = [], [], []

    for link in range(len(job_detail_links_naukari)):
        time.sleep(5)
        driver.get(job_detail_links_naukari[link])
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find(attrs={'class': "salary"}) == None or soup.find(attrs={'class': 'loc'}) == "Remote":
            continue
        else:
            company_name_list_naukari.append("NA" if soup.find(attrs={'class': "jd-header-comp-name"}) == None else soup.find(
                attrs={'class': "jd-header-comp-name"}).text)
            experience_list.append(
                "NA" if soup.find(attrs={'class': "exp"}) == None else soup.find(attrs={'class': "exp"}).text)
            salary_list_naukari.append(
                "NA" if soup.find(attrs={'class': "salary"}) == None else soup.find(attrs={'class': "salary"}).text)
            loca = []
            location = (
                "NA" if soup.find(attrs={'class': 'loc'}) == None else soup.find(attrs={'class': 'loc'}).findAll('a'))
            for i in location:
                try:
                    loca.append(i.text)
                except AttributeError:
                    loca.append(i)
                except:
                    loca.append(i)

            location_list_naukari.append(",".join(loca))

            designation_list_naukari.append("NA" if soup.find(attrs={'class': "jd-header-title"}) == None else soup.find(
                attrs={'class': "jd-header-title"}).text)
            job_description_list.append(
                "NA" if soup.find(attrs={'class': "job-desc"}) == None else soup.find(attrs={'class': "job-desc"}).text)
            post_date_list.append(["NA"] if soup.find(attrs={'class': "jd-stats"}) == None else
                                  [i for i in soup.find(attrs={'class': "jd-stats"})][0].text.split(':')[1])
            try:
                website_list.append(
                    "NA" if soup.find(attrs={'class': "jd-header-comp-name"}).contents[0]['href'] == None else
                    soup.find(attrs={'class': "jd-header-comp-name"}).contents[0]['href'])
            except KeyError or ValueError:
                website_list.append("NA")
            except:
                website_list.append("NA")
            try:
                url_list.append(
                    "NA" if soup.find(attrs={'class': "jd-header-comp-name"}).contents[0]['href'] == None else
                    soup.find(attrs={'class': "jd-header-comp-name"}).contents[0]['href'])
            except KeyError or ValueError:
                website_list.append("NA")
            except:
                website_list.append("NA")

            details = []
            try:
                for i in soup.find(attrs={'class': "other-details"}).findAll(attrs={'class': "details"}):
                    details.append(i.text)
                role_list.append(details[0].replace('Role', ''))
                industry_type_list.append(details[1].replace('Industry Type', ''))
                functional_area_list.append(details[2].replace('Functional Area', ''))
                employment_type_list.append(details[3].replace('Employment Type', ''))
                role_category_list.append(details[4].replace('Role Category', ''))

                qual = []
                for i in soup.find(attrs={'class': "education"}).findAll(attrs={'class': 'details'}):
                    qual.append(i.text)
                education_list.append(qual)

                sk = []
                for i in soup.find(attrs={'class': "key-skill"}).findAll('a'):
                    sk.append(i.text)
                key_skill_list.append(",".join(sk))

                if soup.find(attrs={'class': "name-designation"}) == None:
                    post_by_list.append("NA")
                else:
                    post_by_list.append(soup.find(attrs={'class': "name-designation"}).text)

                if soup.find(attrs={'class': "about-company"}) == None:
                    about_company_list.append("NA")
                else:
                    address_list.append("NA" if soup.find(attrs={'class': "about-company"}).find(
                        attrs={'class': "comp-info-detail"}) == None else soup.find(
                        attrs={'class': "about-company"}).find(attrs={'class': "comp-info-detail"}).text)
                    about_company_list.append(soup.find(attrs={'class': "about-company"}).find(
                        attrs={'class': "detail dang-inner-html"}).text)
            except:
                pass
            if not message or random.random() < 0.25:
                message = '{0} {1} {2}...'.format(random.choice(verb),
                                                  random.choice(adjective),
                                                  random.choice(noun))
            self.update_state(state='PROGRESS',
                              meta={'current': link, 'total': len(job_detail_links_naukari), 'status': message})

    df = pd.DataFrame()
    df['Designation'] = designation_list_naukari
    df['Company Name'] = company_name_list_naukari
    df['Salary'] = salary_list_naukari
    df['Experience'] = experience_list
    df['Location'] = location_list_naukari
    df['Role'] = role_list
    df['Skills'] = key_skill_list
    df['Qualification'] = education_list
    df['Industry Type'] = industry_type_list
    df['Functional Area'] = functional_area_list
    df['Employment Type'] = employment_type_list
    df['Role Category'] = role_category_list
    df['Address'] = address_list
    df['Post By'] = post_by_list
    df['Post Date'] = post_date_list
    df['Website'] = website_list
    df['Url'] = url_list
    df['Job Description'] = job_description_list
    df['About Company'] = about_company_list
    df.to_csv(f'./static/{FILE_NAME}', index=False)
    save_naukri_data_to_db()
    driver.close()


class User(db.Model):
    id = db.Column('User_id', db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=True, nullable=False)


class Dicedata(db.Model):
    id = db.Column( db.Integer, primary_key=True)
    Job_Title = db.Column(db.String(500), unique=False, nullable=False)
    Company_Name = db.Column(db.String(500), unique=False, nullable=False)
    description = db.Column(db.String(1000), unique=False, nullable=False)
    Posted_Date = db.Column(db.String(100), unique=False, nullable=False)
    Job_Type = db.Column(db.String(300), unique=False, nullable=False)
    Location = db.Column(db.String(300), unique=False, nullable=False)


class Indeeddata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Company_Name = db.Column(db.String(500), unique=False, nullable=False)
    Company_url = db.Column(db.String(500), unique=False, nullable=False)
    salary = db.Column(db.String(1000), unique=False, nullable=False)
    designation = db.Column(db.String(100), unique=False, nullable=False)
    location = db.Column(db.String(300), unique=False, nullable=False)
    qualification = db.Column(db.String(300), unique=False, nullable=False)


class Naukridata(db.Model):
    id = db.Column( db.Integer, primary_key=True)
    Designation = db.Column(db.String(500), unique=False, nullable=False)
    Company_Name = db.Column(db.String(500), unique=False, nullable=False)
    salary = db.Column(db.String(1000), unique=False, nullable=False)
    Experience = db.Column(db.String(300), unique=False, nullable=False)
    Location = db.Column(db.String(300), unique=False, nullable=False)
    Role = db.Column(db.String(300), unique=False, nullable=False)
    Skills = db.Column(db.String(300), unique=False, nullable=False)
    Qualification = db.Column(db.String(300), unique=False, nullable=False)
    Industry_Type = db.Column(db.String(300), unique=False, nullable=False)
    Functional_Area = db.Column(db.String(300), unique=False, nullable=False)
    Employment_Type = db.Column(db.String(300), unique=False, nullable=False)
    Role_Category = db.Column(db.String(300), unique=False, nullable=False)
    Address = db.Column(db.String(300), unique=False, nullable=False)
    Post_By = db.Column(db.String(300), unique=False, nullable=False)
    Post_Date = db.Column(db.String(300), unique=False, nullable=False)
    Website = db.Column(db.String(300), unique=False, nullable=False)
    Url = db.Column(db.String(300), unique=False, nullable=False)
    Job_Description = db.Column(db.String(3000), unique=False, nullable=False)
    About_Company = db.Column(db.String(3000), unique=False, nullable=False)


def save_naukri_data_to_db():
    data = []
    c = mysql.connector.connect(host='localhost', user='root', database='scrap', password='12345',
                                auth_plugin='mysql_native_password')
    c_obj = c.cursor()
    with open("./static/naukri.csv", 'r', encoding="latin-1") as f:
        r = csv.reader(f)
        for row in r:
            data.append(row)

    data_csv = "insert into Naukridata(Designation,Company_Name,salary,Experience,Location,Role,Skills,Qualification,Industry_Type,Functional_Area,Employment_Type,Role_Category,Address,Post_By,Post_Date,Website,Url,Job_Description,About_Company) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    c_obj.executemany(data_csv, data)
    c.commit()
    c_obj.close()


def save_dice_data_to_db():
    data = []
    c = mysql.connector.connect(host='localhost', user='root', database='scrap', password='12345',
                                auth_plugin='mysql_native_password')
    c_obj = c.cursor()
    with open("./static/indeed.csv", 'r', encoding="latin-1") as f:
        r = csv.reader(f)
        for row in r:
            data.append(row)

    data_csv = "insert into dicedata(Job_Title,Company_Name,description,Posted_Date,Job_Type,Location) values(%s,%s,%s,%s,%s,%s)"
    c_obj.executemany(data_csv, data)
    c.commit()
    c_obj.close()


def save_indeed_data_to_db():
    data = []
    c = mysql.connector.connect(host='localhost', user='root', database='scrap', password='12345',
                                auth_plugin='mysql_native_password')
    c_obj = c.cursor()
    with open("./static/indeed.csv", 'r', encoding="latin-1") as f:
        r = csv.reader(f)
        for row in r:
            data.append(row)

    data_csv = "insert into indeeddata(Company_Name,Company_url,salary,designation,location,qualification) values(%s,%s,%s,%s,%s,%s)"
    c_obj.executemany(data_csv, data)
    c.commit()
    c_obj.close()

with app.app_context():
    db.create_all()


@app.route("/", endpoint="1")
@login_required
def home():
    return render_template("home.html")


@app.route("/signup", methods=('GET', 'POST'))
def signup():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_exits = User.query.filter_by(email=email).first()
        if user_exits:
            message = "Email if is already Taken !!!"
            return render_template("signup.html", name="signup", message=message)

        else:
            hashed_password = generate_password_hash(
                password=password, method='sha256')
            new_user = User(username=username,
                            email=email,
                            password=hashed_password)

            db.session.add(new_user)
            db.session.commit()
            message = "New User Registerd"

            print("new user created")
    return render_template("signup.html", name="signup", message=message)


@app.route("/login", methods=('GET', 'POST'))
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                print("User Logged In")
                session['user'] = User
                print(session.get('user'))
                return redirect('/')
            else:
                error = "Wrong password"
                return render_template("login.html", name="login", error=error)
        else:
            error = "Email id not matched"
            return render_template("login.html", name="login", error=error)
    else:
        return render_template("login.html", name="login")


@login_required
@app.route("/logout", endpoint='2')
def logout():
    session.clear()
    return redirect('/login')


@app.route("/search", endpoint="3", methods=['GET', 'POST'])
@login_required
def search():
    web = request.args.get("web")
    session["web"] = request.args.get("web")
    tech = request.args.get("tech", "python")
    page = request.args.get("pages", "1")
    location = request.args.get("location", "india")
    df = None
    name = None
    task_id = None
    if page == None:
        page = 5
    page = int(page)
    print(web, tech, location, page)
    if web == None or tech == None:
        return redirect("/")
    if web == "indeed":
        #c = celery.send_task("tasks.scrap_details", args=[tech, location], kwargs={ "page": page})
        task = scrap_details.apply_async([tech, location, page])
        session['task_id'] = task.id
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}
    if web == "dice":
        task = extract_dice_jobs.apply_async([tech, location, page])
        session['task_id'] = task.id
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}
    if web == "naukri":
        #c = celery.send_task("tasks.scrap_naukari", args=[tech], kwargs={"page": page})
        task = scrap_naukari.apply_async([tech, location, page])
        session['task_id'] = task.id
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}
    #return render_template("task.html", task_id=task_id)


@app.route("/result/<task_id>", endpoint="4")
@login_required
def show_result(task_id):
    web = session.get("web")
    status = AsyncResult(task_id, app=celery)
    df = None
    name = None
    if status.ready():
        if web == "indeed":
            try:
                df = pd.read_csv("./static/indeed.csv")
            except:
                "NO DATA"
        elif web == "dice":
            try:
                df = pd.read_csv("./static/dice.csv")
            except:
                "NO DATA"
        elif web == "naukri":
            try:
                df = pd.read_csv("./static/naukri.csv")
            except:
                "NO DATA"
    else:
        return render_template("pending.html", task_id=task_id, state=status.state, stage=status.result)
    return render_template("search.html", tables=[df.to_html(classes='data', justify='center')], titles=df.columns.values, name=name)


@app.route('/status/<task_id>')
def taskstatus(task_id):
    print("-------------status")
    web = session.get("web")
    task = None
    if web == 'indeed':
        print('inside naukri')
        task = scrap_details.AsyncResult(task_id)
        print(task.id)
    elif web == 'dice':
        task = extract_dice_jobs.AsyncResult(task_id)
    elif web == 'naukri':
        task = scrap_naukari.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@app.route("/export")
def export():
    web = session.get("web")
    csv_dir = "./static"
    if web == "indeed":
        csv_file = 'indeed.csv'
        csv_path = os.path.join(csv_dir, csv_file)
        return send_file(csv_path, as_attachment=True)
    elif web == "dice":
        csv_file = 'dice.csv'
        csv_path = os.path.join(csv_dir, csv_file)
        return send_file(csv_path, as_attachment=True)
    elif web == "naukri":
        csv_file = 'naukri.csv'
        csv_path = os.path.join(csv_dir, csv_file)
        return send_file(csv_path, as_attachment=True)
    else:
        return redirect("/")


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    app.run(debug=True, host="0.0.0.0")
