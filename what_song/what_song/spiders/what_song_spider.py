import scrapy
import json
import pandas as pd

SEARCH_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': '*/*',
  'Authorization': '',
  'Sec-Fetch-Site': 'same-site',
  'Accept-Language': 'en-GB,en;q=0.9',
  'Accept-Encoding': 'utf-8',
  'Sec-Fetch-Mode': 'cors',
  'Host': 'v4-api-prod.what-song.com',
  'Origin': 'https://www.what-song.com',
  'Content-Length': '308',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
  'Referer': 'https://www.what-song.com/',
  'Connection': 'keep-alive',
  'Sec-Fetch-Dest': 'empty'
}

box_office_df = pd.read_csv("box_office.csv")

box_office_list = list(box_office_df["title"])

print(box_office_list)



QUERY = "Toy Story 3"

search_url = "https://v4-api-prod.what-song.com/graphql"

class WhatSongSpiderSpider(scrapy.Spider):
    name = "what_song_spider"
    allowed_domains = ["what-song.com"]
    
    def start_requests(self):
            for title in box_office_list[:20]:
                SEARCH_PAYLOAD = json.dumps({
                    "query": "\n    query SearchElastic($query: String!) {\n  searchElastic(query: $query) {\n    type\n    title\n    year\n    slug\n    id\n    artist_name\n    img\n    highlighted_title\n    highlighted_artist_name\n    _score\n  }\n}\n    ",
                    "variables": {
                        "query": title 
                    },
                    "operationName": "SearchElastic"
                })
                headers = SEARCH_HEADERS.copy()
                headers['Content-Length'] = str(len(SEARCH_PAYLOAD))
                print(f"requesting this {title}, {SEARCH_PAYLOAD}")
                yield scrapy.Request(search_url, body=SEARCH_PAYLOAD, headers=headers, callback=self.parse, method="POST")


    def parse(self, response):
        print(response.text, response.url)
        pass



