from urllib.error import URLError
from urllib.request import urlopen, Request
from sys import exit, stdout
from re import search
from html.parser import HTMLParser
from json import dumps, loads
from os import listdir
from datetime import date
from random import randrange

def niceDate(day):
	goodDay = date.fromisoformat(day)
	toReturn = goodDay.strftime("%B {}, %Y")
	toReturn = toReturn.format(goodDay.day)
	return toReturn

#class attributeParser
#saves the attributes from a start tag to a dictionary called self.attributes
class attributeParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		self.attributes = {}
		for attr in attrs:
			self.attributes[attr[0]] = attr[1]

#download()
#argments: year=int (optional)
#downloads the billboard Hot 100 charts for every year from year to the present
#saves every week as a json in corpus directory
def download(year=2019):

	fake_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

	#The first Hot 100 year to download is 1958
	if year < 1958:
		year = 1958
	elif year > 2019:
		year = 2019

	percy = attributeParser()

	while year < 2020:

		yearUrl = 'https://www.billboard.com/archive/charts/{}/hot-100'.format(year)
		
		yearList = []
		
		req = Request(url=yearUrl, headers=fake_header) 

		try:
			response = urlopen(req)
			for lines in response:
				if search("href=\"/charts/hot-100/", str(lines)) != None:
					tempLine = str(lines, 'utf-8')
					percy.feed(tempLine)
					date = percy.attributes["href"].split("/")[-1]
					yearList.append(date)
					percy.attributes = None
		except URLError as e:
			print("Error: "+e.reason.__str__())
			stdout.flush()
		
		#print("Downloading "+str(year))

		for date in yearList:

			chartUrl = 'https://www.billboard.com/charts/hot-100/'+date
			file_name = 'corpus/{}.json'.format(date)

			req = Request(url=chartUrl, headers=fake_header) 
			response = urlopen(req)
			f = open(file_name, 'w')
			tags100 = []
			percy = attributeParser()

			try:
				for lines in response:
					if search("data-rank=\"\d+\"", str(lines)) != None:
						tempLine = str(lines, 'utf-8')
						percy.feed(tempLine)
						if "data-brightcove-data" not in percy.attributes:
							lineJson = {k: percy.attributes[k] for k in percy.attributes if len(k)>5 and k[5] != "h"}
							tags100.append(lineJson)
						percy.attributes = None
			except URLError as e:
				print("Error: "+e.reason.__str__())
				stdout.flush()
				f.close()
				exit()
			f.write(dumps(tags100, sort_keys=True, indent=4))
			print("Downloaded "+chartUrl, end="\r")
			if len(tags100) != 100:
				print(chartUrl+" has {} items.".format(len(tags100)))
			stdout.flush()
			f.close()

		year += 1
		
		
def compile(fullchart=False):
	total = {}

	for i in listdir("corpus/"):
		filee = open("corpus/"+i, 'r')
		thisOne = loads(filee.read())
		filee.close()
		print("Doing {}".format(i), end='\r')
		good = [False for i in range(100)]
		errors = {"doubles": [], "missing": []}
		
		wantedList = []
		
		for songs in thisOne:
			numToUse = int(songs["data-rank"])
			if not good[numToUse-1]:
				good[numToUse-1] = True
			else:
				errors["doubles"].append(numToUse)
			if not fullchart and numToUse < 41:
				wantedList.append(songs)
			elif fullchart:
				wantedList.append(songs)
				
		for j in range(100):
			if not good[j]:
				errors["missing"].append(j+1)
		
		if len(errors["missing"]) + len(errors["doubles"]) > 0:
			print("{}: {}".format(i, dumps(errors)))
		
		for song in wantedList:
			art = song["data-artist"]
			title = song["data-title"]
			rank = int(song["data-rank"])
			if art not in total:
				if not fullchart:
					inner = {title: {"highest-rank": rank, "highest-date": i.split(".")[0]}}
				else:
					inner = {title: [{"rank": rank, "date": i.split(".")[0]}]}
				total[art] = inner
			elif title not in total[art]:
				if not fullchart:
					total[art][title] = {"highest-rank": rank, "highest-date": i.split(".")[0]}
				else:
					total[art][title] = [{"rank": rank, "date": i.split(".")[0]}]
			else:
				if not fullchart:
					if rank <= total[art][title]["highest-rank"]:
						total[art][title] = {"highest-rank": rank, "highest-date": i.split(".")[0]}
				else:
					total[art][title].append({"rank": rank, "date": i.split(".")[0]})

	if not fullchart:
		outFile = open("allTimeTop40.json", 'w')
	else:
		outFile = open("allTimeHot100.json", 'w')
	outFile.write(dumps(total, sort_keys=True, indent=4))
	outFile.close()
	songlist = open("songlist.txt", 'w')
	songlist.write(dumps([song for all in total for song in total[all]], sort_keys=True, indent=4))
	songlist.close()
	
def pickSongs():
	inFile = open("allTimeTop40.json", 'r')
	total = loads(inFile.read())
	inFile.close()

	giantList = []

	for allArtists in total:
		for allSongs in total[allArtists]:
			tempDic = total[allArtists][allSongs]
			tempDic["title"] = allSongs
			tempDic["artist"] = allArtists
			giantList.append(tempDic)
			
	strings = ["Good morning! To start you off, we've got \"{0}\" by {1}! This song last peaked at #{2} on {3}.",
	"Up next we have \"{0}\" by {1}. A big favorite of mine, I remember when it was #{2} back on {3}.",
	"Wow, what a great tune. Rounding out the hour we have {1} with \"{0}\", which peaked at #{2} on {3}.",
	"Where were you on {3}? I remember I was listening to \"{0}\" by {1}, which peaked at #{2} on that day.",
	"The day is {3}. {1} is playing on the radio. \"{0}\" was at its peak of {2} on that day.",
	"One last #{2} hit for you tonight, coming at you from {3}. We have {1} rounding out the night with \"{0}\". Good night!"]

	for i in range(15):
		choice = giantList[randrange(len(giantList))]
		if i == 0:
			num = 0
		elif i == 14:
			num = len(strings)-1
		else:
			num = randrange(1,len(strings)-1)
		#print(choice)
		print(strings[num].format(choice["title"],choice["artist"],choice["highest-rank"],niceDate(choice["highest-date"])))