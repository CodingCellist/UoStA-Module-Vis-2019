# BASED ON A SCRAPER BY ALICE LYNCH
# MODIFIED BY THOMAS E HANSEN

#############################
# WARNING: HERE BE DRAGONS! #
################################################################################
# THIS WAS MEANT TO BE SOMEWHAT SIMPLE, BUT IT TURNED OUT THE WEBSITE WAS      #
# _MUCH_ MORE INCONSISTENT THAN I (THOMAS) THOUGHT. AS A RESULT, THIS ENDED UP #
# HAVING A LOT MORE SPECIAL REGEX CASES, MAGIC STRING SPLITTING, ETC. THAN I   #
# EVER THOUGHT IT WOULD. I DON'T KNOW IF I'D EVEN BE ABLE TO UNDERSTAND IT IF  #
# I WERE TO READ THROUGH IT AGAIN.                                             #
################################################################################

from requests import get
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import argparse
import mysql.connector as mariadb
import sys


# level_1000_to_4000 = re.compile('CS1|CS2|CS3|CS4')
level_1000_to_4000 = re.compile('[A-Z]{2}1|[A-Z]{2}2|[A-Z]{2}3|[A-Z]{2}4')  # generalised (not just CS)

# some undergrad courses have co-reqs (e.g. CS2003), but we don't want to
# assume 4000-level as UG because of PGT dipping down
# level_1000_to_3000 = re.compile('CS1|CS2|CS3')
level_1000_to_3000 = re.compile('[A-Z]{2}1|[A-Z]{2}2|[A-Z]{2}3')    # generalised (not just CS)

ug_name = 'Undergraduate'
ug_upper = 'UG'
ug_camel = 'Ug'
pg_name = 'Postgraduate'
pg_upper = 'PGT'
pg_camel = 'Pgt'

# hacky, but it works
ug_antireqs = []
pg_antireqs = []

# modules with _really_ weird requisites
blacklist = [ 'BL3320'
            , 'BL4225'
            ]

def extract_cnf_from_text(raw_text: str):
    if raw_text is None:
        return None
    requisite_regexp = re.compile('[A-Z]{2}[0-9]{4}')
    if len(requisite_regexp.findall(raw_text)) == 0:
        print('WARNING: No module codes in raw text description\n\t"{}"'
              .format(raw_text), file=sys.stderr)
        return None

    conjunctions = raw_text.split(' and ')
    disjunctions = list(
        map(lambda c: tuple(requisite_regexp.findall(c)), conjunctions))
    return disjunctions


def split_ug_pg(module_code: str, raw_text: str):
    """
    Split when undergraduate requirements come before the postgraduate ones.
    :param module_code:
    :param raw_text:
    :return: (UG, PG)
    """
    # might have ug+pg, ug only, pg only, or none
    # case: Undergraduate [...]
    # if ug_name in raw_text and pg_name in raw_text:
    if ug_name in raw_text:
        # case: Undergraduate [...] Postgraduate
        if pg_name in raw_text:
            raw_split = raw_text.split(pg_name)
            assert ug_name in raw_split[0]      # for sanity
            return raw_split[0], raw_split[-1]  # (UG, PG)
        # case: Undergraduate [...] PGT
        elif pg_upper in raw_text:
            raw_split = raw_text.split(pg_upper)
            assert ug_name in raw_split[0]
            return raw_split[0], raw_split[-1]
        # case: Undergraduate [...] Pgt
        elif pg_camel in raw_text:
            raw_split = raw_text.split(pg_camel)
            assert ug_name in raw_split[0]
            return raw_split[0], raw_split[-1]
    # case: UG [...]
    elif ug_upper in raw_text:
        # case: UG [...] Postgraduate
        if pg_name in raw_text:
            raw_split = raw_text.split(pg_name)
            assert ug_upper in raw_split[0]
            return raw_split[0], raw_split[-1]
        # case: UG [...] PGT
        elif pg_upper in raw_text:
            raw_split = raw_text.split(pg_upper)
            assert ug_upper in raw_split[0]
            return raw_split[0], raw_split[-1]
        # case: UG [...] Pgt
        elif pg_camel in raw_text:
            raw_split = raw_text.split(pg_camel)
            assert ug_upper in raw_split[0]
            return raw_split[0], raw_split[-1]
    # case: Ug [...]
    elif ug_camel in raw_text:
        # case: Ug [...] Postgraduate
        if pg_name in raw_text:
            raw_split = raw_text.split(pg_name)
            assert ug_camel in raw_split[0]
            return raw_split[0], raw_split[-1]
        # case: Ug [...] PGT
        elif pg_upper in raw_text:
            raw_split = raw_text.split(pg_upper)
            assert ug_camel in raw_split[0]
            return raw_split[0], raw_split[-1]
        # case: Ug [...] Pgt
        elif pg_camel in raw_text:
            raw_split = raw_text.split(pg_camel)
            assert ug_camel in raw_split[0]
            return raw_split[0], raw_split[-1]
    # case: ???????
    else:
        assert raw_text is not None
        raise UserWarning('The string "{}" is really weird...'.format(raw_text))


def split_pg_ug(module_code: str, raw_text: str):
    """
    Split when postgraduate requirements come before the undergraduate.
    :param module_code:
    :param raw_text:
    :return: (UG, PG)
    """
    if pg_name in raw_text:
        if ug_name in raw_text:
            raw_split = raw_text.split(ug_name)
            assert pg_name in raw_split[0]      # for sanity
            return raw_split[-1], raw_split[0]  # (UG, PG)
        elif ug_upper in raw_text:
            raw_split = raw_text.split(ug_upper)
            assert pg_name in raw_split[0]
            return raw_split[-1], raw_split[0]
        elif ug_camel in raw_text:
            raw_split = raw_text.split(ug_camel)
            assert pg_name in raw_split[0]
            return raw_split[-1], raw_split[0]
    elif pg_upper in raw_text:
        if ug_name in raw_text:
            raw_split = raw_text.split(ug_name)
            assert pg_upper in raw_split[0]
            return raw_split[-1], raw_split[0]
        elif ug_upper in raw_text:
            raw_split = raw_text.split(ug_upper)
            assert pg_upper in raw_split[0]
            return raw_split[-1], raw_split[0]
        elif ug_camel in raw_text:
            raw_split = raw_text.split(ug_camel)
            assert pg_upper in raw_split[0]
            return raw_split[-1], raw_split[0]
    elif pg_camel in raw_text:
        if ug_name in raw_text:
            raw_split = raw_text.split(ug_name)
            assert pg_camel in raw_split[0]
            return raw_split[-1], raw_split[0]
        elif ug_upper in raw_text:
            raw_split = raw_text.split(ug_upper)
            assert pg_camel in raw_split[0]
            return raw_split[-1], raw_split[0]
        elif ug_camel in raw_text:
            raw_split = raw_text.split(ug_camel)
            assert pg_camel in raw_split[0]
            return raw_split[-1], raw_split[0]
    else:
        assert raw_text is not None
        raise UserWarning('The string "{}" is really weird...'.format(raw_text))


def split_by_level(module_code: str, raw_text: str):
    """
    Returns a tuple of the UG and PG parts of the string, **in that order!**.
    If one is missing, that part of the tuple is None.
    :param raw_text: the string to split
    :return: (UG_part, PG_part)
    """
    # Yay for inconsistent websites...
    ug_first_regex_str = r'.*' \
                         r'(Undergraduate.*Postgraduate' \
                         r'|UG.*PGT' \
                         r'|Ug.*Pgt' \
                         r'|Undergraduate.*PGT' \
                         r'|Undergraduate.*Pgt)'
    ug_first = re.compile(ug_first_regex_str)
    pg_first_regex_str = r'.*' \
                         r'(Postgraduate.*Undergraduate' \
                         r'|PGT.*UG' \
                         r'|Pgt.*Ug' \
                         r'|PGT.*Undergraduate' \
                         r'|Pgt.*Undergraduate)'
    pg_first = re.compile(pg_first_regex_str)

    # case: requisite order is UG PG
    if ug_first.match(raw_text) is not None:
        return split_ug_pg(module_code, raw_text)
    # case: requisite order is PG UG
    elif pg_first.match(raw_text) is not None:
        return split_pg_ug(module_code, raw_text)
    # case: only undergrad requirement ('Undergraduate', 'UG', or 'Ug')
    elif ug_name in raw_text or ug_upper in raw_text or ug_camel in raw_text:
        return raw_text, None
    # case: only postgrad requirement ('Postgraduate', 'PGT', or 'Pgt')
    elif pg_name in raw_text or pg_upper in raw_text or pg_camel in raw_text:
        return None, raw_text
    # elif level_1000_to_4000.match(module_code) is not None \
    #        and 'Co-requisite' not in raw_text:
    # case: no indication what the requirement is, but its 1000-3000 level and
    #       a co-requisite
    elif level_1000_to_3000.match(module_code) is not None \
            and 'Co-requisite' in raw_text:
        # guess the requisite is UG
        return raw_text, None
    # case: not a co-requisite, but it is 1000-4000 level
    elif level_1000_to_4000.match(module_code) is not None \
            and 'Co-requisite' not in raw_text:
        # guess the requisite is UG
        return raw_text, None
    # case: no indication, but the requirement is a co-requisite (which, above
    #       3000-level are usually postgraduate)
    elif 'Co-requisite' in raw_text:
        # co-requisites are usually postgrad, so guess that
        return None, raw_text
    # case: no indication, but the module is 5000-level
    # elif re.match('CS5', module_code) is not None:
    elif re.match('[A-Z]{2}5', module_code) is not None:
        # case: the requisite-text refers to an undergraduate-level module
        # if re.match('.*(CS1|CS2|CS3)', raw_text) is not None:
        if re.match('.*([A-Z]{2}1|[A-Z]{2}2|[A-Z]{2}3)', raw_text) is not None:
            # guess UG requisite
            return raw_text, None
        # if all else fails at 5000-level, assume PGT
        return None, raw_text
    # case: ???????
    else:
        # sanity check
        assert raw_text is not None
        # give up
        raise UserWarning('Okay, seriously, how did this happen? ("{}")'.format(raw_text))


def scrape(school_code="CS", limit=None):
    url = "https://portal.st-andrews.ac.uk/catalogue/search?searchTerm=" + school_code
    response = get(url)
    page = BeautifulSoup(response.text, 'html.parser')
    rows = page.find_all("tr", role="row")
    rows = rows[1:]
    links = page.findAll("a", href=re.compile(r"^/catalogue/View"), limit=limit)
    requisites = []

    for link, row in tqdm(list(zip(links, rows))):
    # for link, row in list(zip(links, rows)):
        link = link['href']
        module = BeautifulSoup(
            get("https://portal.st-andrews.ac.uk" + link).text,
            'html.parser')  # module page
        raw_academic_years = module.find("p",
                                         class_="lead").text  # academic year text
        page_title = " ".join(module.findAll("h2")[
                                  2].text.split())  # remove excess whitespace from page title
        module_code = page_title[:6]
        module_title = page_title[7:]
        p_tags = module.findAll(
            "p")  # get all relevant p tags (rather than doing multiple times)
        # NB: p_tag based fetching is fragile - if the uni updates their page format the scraper will break.
        if 'Planned timetable:' not in p_tags[6].text.strip():
            description = p_tags[6].text.strip()
        else:
            description = p_tags[7].text.strip()
        pre_reqs_raw, co_reqs_raw, anti_reqs_raw, semester_number, \
        assessment_pattern_raw, credit_worth, re_assessable = None, None, None, \
                                                              None, None, None, \
                                                              '0'  # `re_assessable` default False
        for p in p_tags:
            if "Pre-requisite(s):" in p.text:
                pre_reqs_raw = p.text
            elif "Anti-requisite(s):" in p.text:
                anti_reqs_raw = p.text
            elif "Co-requisite(s):" in p.text:
                co_reqs_raw = p.text
            # elif "As used by St Andrews" in p.text:
            #     assessment_pattern_raw = p.text

            # new way of doing semesters
            sem_details = row.findAll("td")[-1].text
            if 'Full Year' in sem_details:
                semester_number = '4'
            elif 'Summer' in sem_details:
                semester_number = '3'
            else:
                semester_number = sem_details[-1]

        # setup of variables
        ug_pre_reqs_raw, ug_anti_reqs_raw, ug_co_reqs_raw = None, None, None
        ug_pre_reqs, ug_anti_reqs, ug_co_reqs = None, None, None
        pgt_pre_reqs_raw, pgt_anti_reqs_raw, pgt_co_reqs_raw = None, None, None
        pgt_pre_reqs, pgt_anti_reqs, pgt_co_reqs = None, None, None

        ##################
        # PRE-REQUISITES #
        ##################
        if pre_reqs_raw is not None:
            if 'must pass' in pre_reqs_raw:
                # print(module_code, ':')
                # print(pre_reqs_raw)
                # pre_reqs = extract_cnf_from_text(pre_reqs_raw)
                ug_pre_reqs_raw, pgt_pre_reqs_raw = split_by_level(module_code,
                                                                   pre_reqs_raw)
                ug_pre_reqs = extract_cnf_from_text(ug_pre_reqs_raw)
                pgt_pre_reqs = extract_cnf_from_text(pgt_pre_reqs_raw)
                # if ug_pre_reqs is not None:
                #     print('ug-pre:', ug_pre_reqs)
                # if pgt_pre_reqs is not None:
                #     print('pg-pre:', pgt_pre_reqs)
            else:
                pass
                # print('pre-reqs: custom', file=sys.stderr)
        # sys.stdout.flush()
        # sys.stderr.flush()

        ###################
        # ANTI-REQUISITES #
        ###################
        if anti_reqs_raw is not None:
            # print(module_code, ':')
            # print(anti_reqs_raw)
            # anti_reqs = extract_cnf_from_text(anti_reqs_raw)
            ug_anti_reqs_raw, pgt_anti_reqs_raw = split_by_level(module_code,
                                                                 anti_reqs_raw)
            ug_anti_reqs = extract_cnf_from_text(ug_anti_reqs_raw)
            pgt_anti_reqs = extract_cnf_from_text(pgt_anti_reqs_raw)
            # if ug_anti_reqs is not None:
            #     print('ug-anti:', ug_anti_reqs)
            # if pgt_anti_reqs is not None:
            #     print('pg-anti:', pgt_anti_reqs)
        # sys.stdout.flush()
        # sys.stderr.flush()

        #################
        # CO-REQUISITES #
        #################
        if co_reqs_raw is not None:
            # print(module_code, ':')
            # print(co_reqs_raw)
            # co_reqs = extract_cnf_from_text(co_reqs_raw)
            ug_co_reqs_raw, pgt_co_reqs_raw = split_by_level(module_code,
                                                             co_reqs_raw)
            ug_co_reqs = extract_cnf_from_text(ug_co_reqs_raw)
            pgt_co_reqs = extract_cnf_from_text(pgt_co_reqs_raw)
            # if ug_co_reqs is not None:
            #     print('ug-co:', ug_co_reqs)
            # if pgt_co_reqs is not None:
            #     print('pg-co:', pgt_co_reqs)
        # sys.stdout.flush()
        # sys.stderr.flush()
        # see `biology-edge-cases`
        if module_code not in blacklist:
            requisites.append(
                (module_code, raw_academic_years[18:], semester_number,
                 ug_pre_reqs, pgt_pre_reqs,
                 ug_co_reqs, pgt_co_reqs,
                 ug_anti_reqs, pgt_anti_reqs)
            )
    return requisites


def sqlize_pre_reqs(database, cursor, persist,
                    source_module_code,
                    academic_year, semester_number,
                    ug_pre_reqs, pg_pre_reqs):
    # ARGUMENTS:
    # 1. source_module_code
    # 2. target_module_code
    # 3. academic_level_concerned
    # 4. academic_year_concerned
    # 5. semester_concerned
    new_pre_req_query =\
        'CALL {}.create_pre_requisite(%s, %s, %s, %s, %s);'\
        .format(database)

    # ARGUMENTS:
    # 1. source_module_code
    # 2. existing_target_module_code
    # 3. existing_target_academic_level
    # 4. existing_target_academic_year
    # 5. existing_target_semester_number
    # 6. new_alternative_target_module_code
    alt_pre_req_query =\
        'CALL {}.add_alt_pre_req_by_existing_pre_req(%s, %s, %s, %s, %s, %s);'\
        .format(database)

    if ug_pre_reqs is not None:
        for ug_pre_tuple in ug_pre_reqs:
            first = True
            for req_code in ug_pre_tuple:
                if first:
                    param_tuple = (source_module_code, req_code,
                                   'UG', academic_year, semester_number)
                    print(new_pre_req_query % param_tuple)
                    if persist:
                        cursor.execute(
                            new_pre_req_query,
                            param_tuple
                        )
                    first = False
                else:
                    param_tuple = (source_module_code, ug_pre_tuple[0],
                                   'UG', academic_year, semester_number, req_code)
                    print(alt_pre_req_query % param_tuple)
                    if persist:
                        cursor.execute(
                            alt_pre_req_query,
                            param_tuple
                        )
    if pg_pre_reqs is not None:
        for pg_pre_tuple in pg_pre_reqs:
            first = True
            for req_code in pg_pre_tuple:
                if first:
                    param_tuple = (source_module_code, req_code,
                                   'PGT', academic_year, semester_number)
                    print(new_pre_req_query % param_tuple)
                    if persist:
                        cursor.execute(
                            new_pre_req_query,
                            param_tuple
                        )
                    first = False
                else:
                    param_tuple = (source_module_code, pg_pre_tuple[0],
                                   'PGT', academic_year, semester_number,
                                   req_code)
                    print(alt_pre_req_query % param_tuple)
                    if persist:
                        cursor.execute(
                            alt_pre_req_query,
                            param_tuple
                        )


def sqlize_co_reqs(database, cursor, persist,
                    source_module_code,
                    academic_year, semester_number,
                    ug_co_reqs, pg_co_reqs):
    # ARGUMENTS:
    # 1. source_module_code
    # 2. target_module_code
    # 3. academic_level_concerned
    # 4. academic_year_concerned
    # 5. semester_concerned
    new_co_req_query = \
        'CALL {}.create_co_requisite(%s, %s, %s, %s, %s);'\
            .format(database)

    # ARGUMENTS:
    # 1. source_module_code
    # 2. existing_target_module_code
    # 3. existing_target_academic_level
    # 4. existing_target_academic_year
    # 5. existing_target_semester_number
    # 6. new_alternative_target_module_code
    alt_co_req_query = \
        'CALL {}.add_alt_co_req_by_existing_co_req(%s, %s, %s, %s, %s, %s)'\
            .format(database)

    if ug_co_reqs is not None:
        for ug_co_tuple in ug_co_reqs:
            first = True
            for req_code in ug_co_tuple:
                if first:
                    param_tuple = (source_module_code, req_code,
                                   'UG', academic_year, semester_number)
                    print(new_co_req_query % param_tuple)
                    if persist:
                        cursor.execute(
                            new_co_req_query,
                            param_tuple
                        )
                    first = False
                else:
                    param_tuple = (source_module_code, ug_co_tuple[0],
                                   'UG', academic_year, semester_number,
                                   req_code)
                    print(alt_co_req_query % param_tuple)
                    if persist:
                        cursor.execute(
                            alt_co_req_query,
                            param_tuple
                        )
    if pg_co_reqs is not None:
        for pg_co_tuple in pg_co_reqs:
            first = True
            for req_code in pg_co_tuple:
                if first:
                    param_tuple = (source_module_code, req_code,
                                   'PGT', academic_year, semester_number)
                    print(new_co_req_query % param_tuple)
                    if persist:
                        cursor.execute(
                            new_co_req_query,
                            param_tuple
                        )
                    first = False
                else:
                    param_tuple = (source_module_code, pg_co_tuple[0],
                                   'PGT', academic_year, semester_number,
                                   req_code)
                    print(alt_co_req_query % param_tuple)
                    if persist:
                        cursor.execute(
                            alt_co_req_query,
                            param_tuple
                        )


def sqlize_anti_reqs(database, cursor, persist,
                    source_module_code,
                    academic_year, semester_number,
                    ug_anti_reqs, pg_anti_reqs):
    # TODO: keep record of anti-requisites; the bi-directionality means duplicates can occur

    # Arguments:
    # 1. source_module_code
    # 2. target_module_code
    # 3. academic_level_concerned
    # 4. academic_year_concerned
    # 5. semester_concerned
    new_anti_req_query =\
        'CALL {}.create_anti_requisite(%s, %s, %s, %s, %s);'\
        .format(database)

    if ug_anti_reqs is not None:
        for ug_anti_tuple in ug_anti_reqs:
            if len(ug_anti_reqs) > 1:
                raise UserWarning(str(ug_anti_reqs) +
                                  ': What did you just bring upon this cursed land??')
            param_tuple = (source_module_code, ug_anti_tuple[0],
                           'UG', academic_year, semester_number)
            reverse_tuple = (ug_anti_tuple[0], source_module_code,
                             'UG', academic_year, semester_number)
            # if we have already added the anti-requisite by adding it one way,
            # we don't need to do it again (since anti-reqs are bi-directional)
            if param_tuple in ug_antireqs or reverse_tuple in ug_antireqs:
                continue
            ug_antireqs.append(param_tuple)
            ug_antireqs.append(reverse_tuple)
            print(new_anti_req_query % param_tuple)
            if persist:
                cursor.execute(
                    new_anti_req_query,
                    param_tuple
                )
    if pg_anti_reqs is not None:
        for pg_anti_tuple in pg_anti_reqs:
            if len(pg_anti_reqs) > 1:
                raise UserWarning(str(pg_anti_reqs) +
                                  ': What did you just bring upon this cursed land??')
            param_tuple = (source_module_code, pg_anti_tuple[0],
                           'PGT', academic_year, semester_number)
            reverse_tuple = (pg_anti_tuple[0], source_module_code,
                             'PGT', academic_year, semester_number)
            # if we have already added the anti-requisite by adding it one way,
            # we don't need to do it again (since anti-reqs are bi-directional)
            if param_tuple in pg_antireqs or reverse_tuple in pg_antireqs:
                continue
            pg_antireqs.append(param_tuple)
            pg_antireqs.append(reverse_tuple)
            print(new_anti_req_query % param_tuple)
            if persist:
                cursor.execute(
                    new_anti_req_query,
                    param_tuple
                )


def sqlize(requisites, persist=False):
    host = 'teh6.host.cs.st-andrews.ac.uk'
    user = 'teh6'
    password = 'GwF53QLc8mQ.g5'
    database = 'teh6_2019_summer_project'

    # connect
    connection = mariadb.connect(host=host,
                                 user=user,
                                 password=password,
                                 database=database,
                                 get_warnings=True)
    if not connection.is_connected():
        print('ERROR: Failed to establish connection to the database.',
              file=sys.stderr)
        exit(1)
    cursor = connection.cursor(prepared=True)

    try:
        for (code, academic_year, semester_number, ug_pre, pg_pre, ug_co, pg_co, ug_anti, pg_anti) in requisites:
            # print(code, academic_year, semester_number, ug_pre, pg_pre, ug_co, pg_co, ug_anti, pg_anti)
            if code == 'CS3050':    # skip the manually input test-module
                continue
            sqlize_pre_reqs(database, cursor, persist,
                            code, academic_year, semester_number, ug_pre, pg_pre)
            sqlize_co_reqs(database, cursor, persist,
                           code, academic_year, semester_number, ug_co, pg_co)
            sqlize_anti_reqs(database, cursor, persist,
                             code, academic_year, semester_number, ug_anti, pg_anti)
        if persist:
            confirm = input(
                'You have asked to persist these statements. Are you sure? (Y/n): ')
            if confirm == 'Y':
                print('Committing...')
                connection.commit()
            else:
                print('Rolling back...')
                connection.rollback()
        print('Closing db-connection...')
        connection.close()
        print('Done.')
        exit(0)
    except mariadb.Error as e:
        print('ERROR: A query failed due to the error "{}"'.format(e),
              file=sys.stderr)
        print('Rolling back and exiting...', file=sys.stderr)
        connection.rollback()
        connection.close()
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('school_code', type=str,
                        help='The school code to scrape.')
    parser.add_argument('-l', '--limit', type=int, required=False, default=None,
                        help='Maximum number of modules to retrieve (omit for all).')
    parser.add_argument('--persist', required=False, action='store_true',
                        help='Persist the resulting SQL-commands to the database. Default is dry-run.')
    args = parser.parse_args()
    requisites = scrape(school_code=args.school_code, limit=args.limit)
    sqlize(requisites, persist=args.persist)
