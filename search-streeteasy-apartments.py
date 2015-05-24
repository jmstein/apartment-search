import re
import sys
from sets import Set
from urllib import urlopen
from urllib import quote_plus

url_set = Set()

def make_full_url(url):
	return "http://streeteasy.com" + url

def search(line):
	html = urlopen(line).read()
	for url in re.findall('<a href=\"(/nyc/rental/[^"]+)/visit_original[^"]*\"', html):
		url_set.add(url)
	next_page_matcher = re.search('<a href=\"([^"]+)">\s*next', html)
	if not next_page_matcher:
		return None
	else:
		return make_full_url(next_page_matcher.group(1))

for line in sys.stdin.readlines():
	next_page = line
	while next_page:
		next_page = search(next_page)

urls = []
for url in url_set:
	urls += [url]

urls.sort()
for url in urls:
	print make_full_url(url)