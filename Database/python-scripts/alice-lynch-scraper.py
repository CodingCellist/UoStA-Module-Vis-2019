from requests import get
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import argparse


def scrape(school_code="CS", limit=None):
	url = "https://portal.st-andrews.ac.uk/catalogue/search?searchTerm=" + school_code
	response = get(url)
	page = BeautifulSoup(response.text, 'html.parser')
	links = page.findAll("a", href=re.compile(r"^/catalogue/View"), limit=limit)
	modules = []
	for link in tqdm(links):
		link = link['href']
		module = BeautifulSoup(get("https://portal.st-andrews.ac.uk"+link).text, 'html.parser') #module page
		raw_academic_years = module.find("p", class_="lead").text # academic year text
		page_title = " ".join(module.findAll("h2")[2].text.split()) # remove excess whitespace from page title
		module_code = page_title[:6]
		module_title = page_title[7:]
		p_tags = module.findAll("p", limit=9) # get all relevant p-tags (rather than doing multiple times)
		#NB: p_tag based fetching is fragile - if the uni updates their page format the scraper will break.
		semester_number=p_tags[4].text[-1:]
		description=p_tags[6].text.strip()
		credit_worth = p_tags[1].text[-2:]  #(change to 2 for ECTS credits)
		pre_reqs_raw = module.findAll("p")[7].text
		anti_reqs_raw = module.findAll("p")[8].text
		#TODO: extract pre-reqs and anti-reqs from raw text
		pre_reqs = pre_reqs_raw
		anti_reqs = anti_reqs_raw
		academic_years = raw_academic_years[18:]
		module_data = [module_code, module_title, semester_number, description, credit_worth, pre_reqs, anti_reqs, academic_years]
		modules.append(module_data)

	print(modules)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('school_code', type=str, help='The school code to scrape.')
	parser.add_argument('-l', '--limit', type=int, required=False, default=None, help='Maximum number of modules to retrieve (omit for all).')
	args = parser.parse_args()
	scrape(school_code=args.school_code, limit=args.limit)
