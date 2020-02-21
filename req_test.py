import requests
import feedparser
import datetime
from datetime import timedelta, date
import string
from pytz import timezone
from pytz import all_timezones
import xlsxwriter

sources = ["https://www.cnbc.com", "https://www.bloomberg.com", "https://www.reuters.com", "https://www.cnn.com", "https://money.cnn.com", "https://www.forbes.com", "https://www.marketwatch.com"]

req_str = 'https://news.google.com/rss/search'

workbook = xlsxwriter.Workbook('aapl_test.xlsx')
worksheet = workbook.add_worksheet()

wb_rows = []

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2010, 2, 1)
end_date = date(2020, 2, 8)

cnt = 0
for req_date in daterange(start_date, end_date):
	print(str(cnt))
	cnt += 1

	# req_date = datetime.datetime(2020, 1, 29)

	payload = {
		'q':'aapl ' + req_date.strftime("%m/%d/%Y"),
		'hl':'en-US',
		'gl':'US',
		'ceid':'US:en'
	}
	r = requests.get(req_str, params=payload)

	entries = feedparser.parse(r.text.encode(encoding="utf-8")).entries

	valid_entries = []

	for entry in entries:
		title = entry.title
		date = entry.published.split(" ", 1)[1]
		# if article title is readable as string
		if all(c in string.printable for c in title):
			# if source is valid
			if entry.source['href'] in sources:
				date = datetime.datetime.strptime(date, "%d %b %Y %H:%M:%S %Z")
				date_pac = timezone('GMT').localize(date).astimezone(timezone('US/Pacific'))
				# make sure the publishing date is not 0 in pacific time, e.g. it doesnt have a time
				# basically, make sure there is an actual time to the date and not just a filler
				if not (date_pac.hour == 0 and date_pac.minute == 0 and date_pac.second == 0):
					#east coast date
					date_ec = timezone('GMT').localize(date).astimezone(timezone('US/Eastern'))
					# make sure that the date matches up to the wanted date
					if (date_ec.year == req_date.year and date_ec.month == req_date.month and date_ec.day == req_date.day):
						valid_entries.append([title, date_ec])

	for e in valid_entries:
		# print(e[0] + " - " + e[1].strftime("%d %b %Y %H:%M:%S"))
		wb_rows.append([e[0], e[1].strftime("%d %b %Y %H:%M:%S")])


for i in range(len(wb_rows)):
	row = wb_rows[i]
	worksheet.write('A' + str(i), row[0])
	worksheet.write('B' + str(i), row[1])

workbook.close()