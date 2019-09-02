# Billboard scraping script

Use Python 3  
`python bb.py -all`: downloads entire corpus to directory `corpus`  
`python bb.py -u`: updates the corpus for the current year (adds new weeks as the are published)  
`python bb.py -c`: recompiles the corpus into the top 40 songs  
`python bb.py -c -100`: sets the compilation value to the top 100 songs

#### Known bugs:
1. Does not create `corpus` directory automatically
2. can easily cause `429: Too Many Requests` error
3. does not detect or force use of Python 3