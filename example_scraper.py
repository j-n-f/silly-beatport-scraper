from silly_beatport_scraper import *
import os

all_files = os.listdir(".")
all_files = [f_name for f_name in all_files if "wav" in f_name]

my_scraper = SillyBeatportScraper()

for f in all_files:
	if f[-3:].lower() == "wav":
		print(my_scraper.meta_from_filename(f))