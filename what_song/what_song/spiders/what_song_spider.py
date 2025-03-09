import scrapy
import json
import pandas as pd

SEARCH_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-site',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Sec-Fetch-Mode': 'cors',
    'Host': 'v4-api-prod.what-song.com',
    'Origin': 'https://www.what-song.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Referer': 'https://www.what-song.com/',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty'
}

import pandas as pd

box_office_df = pd.read_csv("../box_office.csv")

box_office_list = box_office_df[["title", "release_year"]].to_dict(orient="records")

search_url = "https://v4-api-prod.what-song.com/graphql"

class WhatSongSpiderSpider(scrapy.Spider):
    name = "what_song_spider"
    allowed_domains = ["what-song.com"]

    def start_requests(self):
        for title in box_office_list[:40]:
            SEARCH_PAYLOAD = {
                "query": "query SearchElastic($query: String!) { searchElastic(query: $query) { type title year slug id artist_name img highlighted_title highlighted_artist_name _score } }",
                "variables": {"query": title["title"]},
                "operationName": "SearchElastic"
            }
            
            print(f"Requesting: {title}")
            yield scrapy.Request(
                url=search_url, 
                body=json.dumps(SEARCH_PAYLOAD), 
                headers=SEARCH_HEADERS, 
                callback=self.parse, 
                method="POST",
                meta=title
            )

# Each of those 20 crawl requests gets a dictionary of dictionaries with the top search movies that come up when searching for the title of the movie

    def parse(self, response):
        data = response.json()
        
        # Extract the list of search results
        # movies = data.get("data", {}).get("searchElastic", [])

        # Iterate over each movie and yield the data
        for movie in data["data"]["searchElastic"]:
            print("METADATA", response.meta)
            if movie.get("title").lower() == response.meta["title"].lower() and movie.get("year") == response.meta["release_year"]:            
                movie.update(response.meta)
                # yield movie
                soundtrack_url = f"https://what-song.com/Movies/Soundtrack/{movie["id"]}/{movie["slug"]}"
                yield scrapy.Request(url=soundtrack_url, meta=movie, callback=self.parse_soundtrack, method="GET")
    
    def parse_soundtrack(self, response):
        soundtracks = response.css("script#__NEXT_DATA__::text").get()
        soundtracks = json.loads(soundtracks)
        soundtracks.update(response.meta)
        print("SOUNDTRACKS", soundtracks)   
        yield soundtracks
          
          
          # Do not need to yield each single element as entire thing (movie) is dictionary
            # yield {
            #     "title": movie.get("title"),
            #     "year": movie.get("year"),
            #     "slug": movie.get("slug"),
            #     "id": movie.get("id"),
            #     "img_url": movie.get("img"),
            #     "highlighted_title": movie.get("highlighted_title"),
            #     "artist_name": movie.get("artist_name", "Unknown"),  # Handle None values
            #     "score": movie.get("_score"),
            # }
            
            