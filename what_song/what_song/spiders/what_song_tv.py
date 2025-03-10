import scrapy
import json
import pandas as pd
import time
from pprint import pprint

class WhatSongSpider(scrapy.Spider):
    name = "what_song_tv"
    allowed_domains = ["what-song.com"]
    
    years = list(range(2020, 2024))
    
    start_urls = [f"https://www.what-song.com/_next/data/bE8z_Xdct2jxsav8F3NtQ/popular/tvshow-soundtracks/{str(year)}.json?year={str(year)}" for year in years]

    headers = {
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Purpose': 'prefetch',
        'Sec-Fetch-Mode': 'cors',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        'Referer': 'https://www.what-song.com/popular/tvshow-soundtracks/2016',
        'Connection': 'keep-alive',
        'Host': 'www.what-song.com',
        'Sec-Fetch-Dest': 'empty',
        'x-nextjs-data': '1'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, 
                headers=self.headers, 
                callback=self.parse,
            )

    def parse(self, response):
        # with open("output.json", "w") as file:
        #     file.write(response.text)
        data = response.json()
        # print(data)
        
        
        data = data["pageProps"]
        
        data.update({"original_url": response.url, "scraped_timestamp": time.time()})

        
        # yield data 
        
        for show in data["shows"][:2]:
            # print(show)
            
            show_url = f"https://www.what-song.com/Tvshow/{show['id']}/{show['slug']}"
            
            show = {
                "show_" + key: value for key, value in show.items()
            }
            
            # print('Current show: ', show)
            
            yield scrapy.Request(
                url=show_url, 
                callback=self.parse_show,
                meta=show)
        
    def parse_show(self, response):
        seasons = response.css("script#__NEXT_DATA__::text").get()
        seasons = json.loads(seasons)
        
        # seasons = {
        #     "seasons_" + key: value for key, value in seasons["props"]["pageProps"]["show"].items()
        # }
        # print('SEASONS: ')
        # pprint(seasons)
        
        seasons = seasons["props"]["pageProps"]["show"]["seasons"]
        
        for season in seasons:
            season_url = f"https://www.what-song.com/Tvshow/{response.meta["show_id"]}/{response.meta["show_slug"]}/s/{season["id"]}"
            
            yield scrapy.Request(
                url=season_url, 
                callback=self.parse_season,
                meta=season)
            
    def parse_season(self, response):
        episodes = response.css("div.relative > a::attr(href)").getall()
        
        episodes = [
            e for e in episodes if e not in ["/blog", "/vip"]
        ]
        
        episode_urls = [f"https://www.what-song.com/_next/data/bE8z_Xdct2jxsav8F3NtQ/{episode_slug}.json" for episode_slug in episodes]
        
        print(episode_urls)
         
        for url in episode_urls:
            yield scrapy.Request(
                url=url, 
                callback=self.parse_episode,
                meta=response.meta)
            
    def parse_episode(self, response):
        data = response.json()
        
        yield data
       

        
        
        
        
        
        # for season in seasons[:2]:
        #     season_url = f"https://www.what-song.com/Tvshow/{response.meta['show_id']}/{response.meta['show_slug']}/Season/{season['season_id']}/{season['season_slug']}"
            
         
            
        #     print("season_url ", season_url)
            
        #     # yield scrapy.Request(
        #     #     url=season_url, 
        #     #     callback=self.parse_season,
        #     #     meta=season) 
        
        # print(response.url)