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

box_office_df = pd.read_csv("box_office.csv")
box_office_list = list(box_office_df["title"])

search_url = "https://v4-api-prod.what-song.com/graphql"

class WhatSongSpiderSpider(scrapy.Spider):
    name = "what_song_spider"
    allowed_domains = ["what-song.com"]

    def start_requests(self):
        for title in box_office_list[:20]:
            SEARCH_PAYLOAD = {
                "query": "query SearchElastic($query: String!) { searchElastic(query: $query) { type title year slug id artist_name img highlighted_title highlighted_artist_name _score } }",
                "variables": {"query": title},
                "operationName": "SearchElastic"
            }
            
            print(f"Requesting: {title}")
            yield scrapy.Request(
                url=search_url, 
                body=json.dumps(SEARCH_PAYLOAD), 
                headers=SEARCH_HEADERS, 
                callback=self.parse, 
                method="POST"
            )

# Each of those 20 crawl requests gets a dictionary of dictionaries with the top search movies that come up when searching

# return a json file with the number 1 top search results for each of the 20 movies
    def parse(self, response):
        data = response.json()
        
        # Extract the list of search results
        movies = data.get("data", {}).get("searchElastic", [])

        # Iterate over each movie and yield the data
        for movie in movies:
            yield {
                "title": movie.get("title"),
                "year": movie.get("year"),
                "slug": movie.get("slug"),
                "id": movie.get("id"),
                "img_url": movie.get("img"),
                "highlighted_title": movie.get("highlighted_title"),
                "artist_name": movie.get("artist_name", "Unknown"),  # Handle None values
                "score": movie.get("_score"),
            }
# {
#         "data": {
#             "searchElastic": [
#                 {
#                     "type": "movie",
#                     "title": "The Last Airbender",
#                     "year": 2010,
#                     "slug": "The-Last-Airbender",
#                     "id": 107164,
#                     "artist_name": null,
#                     "img": "/zgwRTYWEEPivTwjB9S03HtmMcbM.jpg",
#                     "highlighted_title": "<em>The</em> <em>Last</em> <em>Airbender</em>",
#                     "highlighted_artist_name": null,
#                     "_score": 21.172426
#                 },
