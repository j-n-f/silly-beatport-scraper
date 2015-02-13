# Note: you must have `flac` and `metaflac` available in your path

from silly_beatport_scraper import *
import os
import subprocess
import urllib

all_files = os.listdir(".")
all_files = [f_name for f_name in all_files if "wav" in f_name]

my_scraper = SillyBeatportScraper()

print("{} file(s) to scrape".format(len(all_files)))
print("note: bpm values can be off, better to leave that to analysis software")

for f in all_files:
    if f[-3:].lower() == "wav":
        print('-' * 70)
        print("scraping for: {}".format(f))
        print('-' * 70)
        meta = my_scraper.meta_from_filename(f)
        
        print('track title:   {}'.format(meta['track_title']))
        print('track artists: {}'.format(meta['track_artists']))
        print('genre:         {}'.format(meta['genre']))
        print('bpm:           {}'.format(meta['bpm']))
        
        print('label:         {}'.format(meta['labels']))
        print('catalogue #:   {}'.format(meta['album_info']['catalogue-number']))
        print('release name:  {}'.format(meta['release_name']))
        print('release date:  {}-{}-{}'.format(
            meta['album_info']['release-date']['year'],
            meta['album_info']['release-date']['month'],
            meta['album_info']['release-date']['day'],
        ))
        try:
            print('track #:       {}'.format(meta['track_number']))
        except:
            print('exception!')
            print(meta)
        print('album art url: {}'.format(meta['album_art_url']))
        print("")

        print("fetching album art (saved as: {})".format(f.replace('wav', 'jpg')))
        urllib.urlretrieve(meta['album_art_url'], f.replace('wav', 'jpg'))
        print("")
        
        print("converting to flac...")
        args = ['flac', '--verify', '--best'] + [f]
        #print(args)
        subprocess.Popen(args).wait()
        print("")
        
        print("tagging...")
        tags = []
        tags += ['"Title={}"'.format(meta['track_title'])]
        tags += ['"Artist={}"'.format(meta['track_artists'])]
        tags += ['"Album={}"'.format(meta['release_name'])]
        tags += ['"Year={}"'.format(meta['album_info']['release-date']['year'])]
        tags += ['"Track={}"'.format(meta['track_number'])]
        tags += ['"Genre={}"'.format(meta['genre'])]
        tags += ['"Comment={}"'.format("Catalog #{}".format(meta['album_info']['catalogue-number']))]
        tags = ["--set-tag={}".format(tag) for tag in tags]
        tags = ['--remove-all-tags'] + tags
        tags += ['--import-picture-from={}'.format(f.replace('wav', 'jpg'))]
        
        args = 'metaflac ' + " ".join(tags) + " " + f.replace('wav', 'flac')
        #print(args)
        subprocess.Popen(args, shell=True).wait()
        print("")
