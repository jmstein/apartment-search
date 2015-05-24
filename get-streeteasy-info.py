import re
import sys
import time
from urllib import urlopen
from urllib import quote_plus

INCLUDE_DISTANCES = False

JOEL_WORK = '1 Madison Ave, 10010'
NICOLE_WORK = '55 Washington St, Brooklyn, NY'
OFFICES = [JOEL_WORK, NICOLE_WORK]
TRANSIT_MODES = ['walking', 'transit']
# (1359563400, 1359558000)

def make_full_url(url):
	return "http://streeteasy.com" + url

def get_distance(a, b, mode, departure_time):
	distanceUrl = 'http://maps.google.com/maps/api/directions/xml?origin=' + quote_plus(a) + '&destination=' + quote_plus(b) + '&sensor=false&mode=' + mode + '&departure_time=' + departure_time
	distanceXml = urlopen(distanceUrl).read()
	distanceTag = re.search('</step>\s+<duration>([\s\S]+)</duration>', distanceXml).group(1)
	
	distanceMatcher = re.search('<text>(\d+) mins?</text>', distanceTag)
	if distanceMatcher:
		distance = distanceMatcher.group(1)
	else:
		distanceMatcher = re.search('<text>(\d+) hours? (\d+) mins?</text>', distanceTag)
		distance = str(int(distanceMatcher.group(1)) * 60 + int(distanceMatcher.group(2)))
	time.sleep(1.5) # 1.5 Second rate limit, found empirically
	return distance
	
def get_amenities(type, html):
	amenitiesMatcher = re.search(type + '</b>([\s\S]+)</table>', html)
	if amenitiesMatcher != None:
		matched = amenitiesMatcher.group(1)
		#tooGreedyMatcher = re.search('Amenities.+', matched)
		#if tooGreedyMatcher:
		#	return get_amenities(type, re.search('(.+)' + tooGreedyMatcher.group(0), html).group(1))
		return re.sub('\s+', ' ', re.sub('<[^>]+>', ' ', matched)).strip()
	return ''

for line in sys.stdin.readlines():
	html = urlopen(line).read()
	address = re.sub('\s*\#.*', '', re.search('class="incognito">([^<]+)</a>', html).group(1))
	bedrooms = re.search('(\d\.?5?) bed', html).group(1)
	onMarket = re.search('(\d+) days? on StreetEasy', html).group(1)

	distances = []
	if INCLUDE_DISTANCES:
		for office in OFFICES:
			for mode in TRANSIT_MODES:
				distances += [get_distance(address + ', new york', office, mode, '1359563400')]

	price = re.sub(',', '', re.search('\\$(\d,\d{3})', html).group(1))
	url = line.strip()

	bathsMatcher = re.search('(\d\.?5?) bath', html)
	if bathsMatcher:
		bathrooms = bathsMatcher.group(1)
	else:
		bathrooms = '?'
	sizeMatcher = re.search('(\d+\.?\d?) ft', html)
	if sizeMatcher:
		size = sizeMatcher.group(1)
	else:
		sizeMatcher = re.search('(\d+)\s*[, ]\s*(\d+) ft', html)
		if sizeMatcher:
			size = str(1000 * int(sizeMatcher.group(1)) + sizeMatcher.group(2))
		else:
			size = '?'
	roomsMatcher = re.search('(\d\.?5?) rooms', html)
	if roomsMatcher:
		rooms = roomsMatcher.group(1)
	else:
		rooms = '?'

	if re.search('\\(NO FEE\\)', html) != None:
		fee = '0'
	else:
		fee = price
	emailUrlMatcher = re.search('\s+by\s+<a href="([^"]+)">', html)
	if emailUrlMatcher != None:
		emailUrl = make_full_url(emailUrlMatcher.group(1))
		emailPage = urlopen(emailUrl).read()
		obfMatcher = re.search('linkToEmail\\(\'([^)]+)\'\\)', emailPage)
		if obfMatcher != None:
			obfEmail = obfMatcher.group(1)
			emailArray = obfEmail.split("-")
			emailArray.reverse()
			email = "".join([chr(int(x)) for x in emailArray])
		else:
			email = emailUrl
	else:
		email = '?'

	amenities = get_amenities('Building Amenities', html) 
	#amenities += ' ' + get_amenities('Listing Amenities', html)
	amenities.strip()
	
	print ",".join([address, onMarket, price] + distances + [url, fee, email, bedrooms, bathrooms, size, rooms, amenities])
	sys.stdout.flush()
