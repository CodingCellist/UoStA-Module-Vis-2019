# BASED ON A SCRAPER BY ALICE LYNCH
# MODIFIED BY THOMAS E HANSEN

from requests import get
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import argparse
import mysql.connector as mariadb
import sys


def scrape(school_code="CS", limit=None):
    url = "https://portal.st-andrews.ac.uk/catalogue/search?searchTerm=" + school_code
    response = get(url)
    page = BeautifulSoup(response.text, 'html.parser')
    rows = page.find_all("tr", role="row")
    rows = rows[1:]
    # for row in rows:
    # 	sem = row.findAll("td")[-1].text
    # 	print(sem)
    links = page.findAll("a", href=re.compile(r"^/catalogue/View"), limit=limit)
    modules = []
    for link, row in tqdm(list(zip(links, rows))):
    # for link, row in list(zip(links, rows)):
        link = link['href']
        module = BeautifulSoup(get("https://portal.st-andrews.ac.uk"+link).text, 'html.parser') #module page
        raw_academic_years = module.find("p", class_="lead").text # academic year text
        page_title = " ".join(module.findAll("h2")[2].text.split()) # remove excess whitespace from page title
        module_code = page_title[:6]
        module_title = page_title[7:]
        p_tags = module.findAll("p") # get all relevant p tags (rather than doing multiple times)
        # NB: p_tag based fetching is fragile - if the uni updates their page format the scraper will break.
        if 'Planned timetable:' not in p_tags[6].text.strip():
            description = p_tags[6].text.strip()
        else:
            description = p_tags[7].text.strip()
        pre_reqs_raw, co_reqs_raw, anti_reqs_raw, semester_number, \
        assessment_pattern_raw, credit_worth, re_assessable = None, None, None, \
                                                              None, None, None, \
                                                              '0'	# `re_assessable` default False
        for p in p_tags:
            if "SCOTCAT credits :" in p.text:
                credit_worth = p.text[-2:]
            elif "Pre-requisite(s):" in p.text:
                pre_reqs_raw = p.text
            elif "Anti-requisite(s):" in p.text:
                anti_reqs_raw = p.text
            elif "Co-requisite(s):" in p.text:
                co_reqs_raw = p.text
            elif "Re-assessment:" in p.text:
                re_assessable = str(int('No Re-assessment available' not in p.text))
            elif "As used by St Andrews" in p.text:
                assessment_pattern_raw = p.text    # could be used, but currently isn't

            # new way of doing semesters: find them from tr instead of catalogue
            sem_details = row.findAll("td")[-1].text
            if 'Full Year' in sem_details:
                semester_number = '4'
            elif 'Summer' in sem_details:
                semester_number = '3'
            else:
                semester_number = sem_details[-1]
        academic_years = raw_academic_years[18:]
        module = {
            'code': module_code,
            'name': module_title,
            'semester': semester_number,
            'description': description,
            'SCOTCAT_credits': credit_worth,
            'academic_year': academic_years,
            're_assessable': re_assessable
        }

        module_data = [module_code, module_title, semester_number, description,
                       credit_worth, academic_years, re_assessable]
        if 'ID' not in module_code[:2] and 'BL4232' not in module_code:
            modules.append(module)

    print(modules)
    return modules


def sqlize(modules, persist=False):
    host = 'teh6.host.cs.st-andrews.ac.uk'
    user = 'teh6'
    password = 'GwF53QLc8mQ.g5'
    database = 'teh6_2019_summer_project'

    parameter_list = []
    create_catalogue_entry_sql = "CALL {}.create_catalogue_entry('%s', '%s', '%s', %s, %s, '%s', %s)" \
        .format(database)
    create_id_module_sql = "CALL {}.create_id_module('%s', %s, '%s', '%s', %s, %s, '%s' %s)" \
        .format(database)
    for module in modules:
        module_code     = module['code']
        module_name     = module['name']
        academic_year   = module['academic_year']
        scotcat_credits = module['SCOTCAT_credits']
        semester_number = module['semester']
        module_desc     = module['description']
        is_reassessable = module['re_assessable']
        param_tuple = (module_code, module_name, academic_year, scotcat_credits,
                       semester_number, module_desc, is_reassessable)
        print(create_catalogue_entry_sql % param_tuple)
        parameter_list.append(param_tuple)
    # print(statements)
    if not persist:
        exit(0)
    else:
        try:
            connection = mariadb.connect(host=host,
                                         user=user,
                                         password=password,
                                         database=database,
                                         get_warnings=True)
            if not connection.is_connected():
                print('ERROR: Failed to connect to the database.')
                exit(1)
            cursor = connection.cursor(prepared=True)  # use prepared statements
            # cursor = connection.cursor(cursor_class=MySQLCursorPrepared)  # use prepared statements
            create_catalogue_entry_sql = create_catalogue_entry_sql.replace("'", "")  # don't ask, mysql-connector is stupid...
            create_id_module_sql = create_id_module_sql.replace("'", "")
            for param_tuple in tqdm(parameter_list):
                cursor.execute(create_catalogue_entry_sql, param_tuple)
            if cursor.fetchwarnings() is not None:
                for warning in cursor.fetchwarnings():
                    print('WARNING: {}'.format(warning[-1]), file=sys.stderr)
            confirm = input('You have asked to persist these statements. Are you sure? (Y/n): ')
            if confirm == 'Y':
                connection.commit()
            else:
                connection.rollback()
            exit(0)
        except mariadb.Error as error:
            connection.rollback()
            print('ERROR: Query failed due to: {}'.format(error))
            exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('school_code', type=str, help='The school code to scrape.')
    parser.add_argument('-l', '--limit', type=int, required=False, default=None,
                        help='Maximum number of modules to retrieve (omit for all).')
    parser.add_argument('--persist', required=False, action='store_true',
                        help='Persist the resulting SQL-commands to the database. Default is dry-run.')
    args = parser.parse_args()
    modules = scrape(school_code=args.school_code, limit=args.limit)
    sqlize(modules, persist=args.persist)
