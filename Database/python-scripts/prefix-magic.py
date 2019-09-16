# BASED ON A SCRAPER BY ALICE LYNCH
# MODIFIED BY THOMAS E HANSEN

from requests import get
from bs4 import BeautifulSoup
import sys
import argparse
import mysql.connector as mariadb


def scrape(persist=False):
    SCHOOL_CODE = "BOTH"    # search for both UG and PGT things
    url = "https://portal.st-andrews.ac.uk/catalogue/search?searchTerm=" + SCHOOL_CODE
    response = get(url)
    page = BeautifulSoup(response.text, 'html.parser')
    rows = page.findAll("tr", role="row")
    rows = rows[1:]
    module_codes = {}
    for row in rows:
        code = row.find("a").text[:2]
        school = row.findAll("td")[3].text
        if code not in module_codes and code != 'ID':
            if school != '':
                module_codes[code] = school
            else:
                print('WARNING: {} has no associated department'.format(code), file=sys.stderr)

    print(module_codes)
    host = 'teh6.host.cs.st-andrews.ac.uk'
    user = 'teh6'
    password = 'GwF53QLc8mQ.g5'
    database = 'teh6_2019_summer_project'
    PROCEDURE = 'CALL {}.create_prefix_association(%s, %s);'.format(database)
    for (k, v) in module_codes.items():
        print(PROCEDURE % (k, v))

    if not persist:
        exit(0)
    else:
        connection = mariadb.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database,
                                     get_warnings=True)
        if not connection.is_connected():
            print('ERROR: Failed to connect to the database.', file=sys.stderr)
            exit(1)
        cursor = connection.cursor(prepared=True)
        for (prefix_code, school_name) in module_codes.items():
            try:
                cursor.execute(PROCEDURE, (prefix_code, school_name))
            except mariadb.Error as error:
                print('ERROR: When executing `{}` the error "{}" occurred.'
                      .format((PROCEDURE % (prefix_code, school_name)), error),
                      file=sys.stderr)
                connection.rollback()
                connection.close()
                exit(2)
        confirm = input('You are about to persist the above statements. Are you sure? (Y/n): ')
        if confirm != 'Y':
            connection.rollback()
        else:
            connection.commit()
        connection.close()
        exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--persist', required=False, action='store_true',
                        help='Persist the resulting SQL-commands to the database. Default is dry-run.')
    args = parser.parse_args()
    scrape(persist=args.persist)
