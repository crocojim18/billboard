from kasem import download, compile, pickSongs
from sys import argv

updateCorpus = False
downloadCorpus = False
recompileCorpus = False
fullchart = False

for i in argv:
	if i == "-u":
		updateCorpus = True
	elif i == "-all":
		downloadCorpus = True
	elif i == "-c":
		recompileCorpus = True
	elif i == "-100":
		fullchart = True
		
if downloadCorpus:
	download(1958)
elif updateCorpus:
	download()
if downloadCorpus or updateCorpus or recompileCorpus:
	compile(fullchart)
pickSongs()