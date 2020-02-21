import requests
import json


i = 0
r = r.json()

while !r_is_empty:
	r = requests.get("https://www.nasdaq.com/api/v1/screener?marketCap=Mega,Large,Medium&page=" + i + "&pageSize=50").json()
	i += 1

print(len(r['data']))