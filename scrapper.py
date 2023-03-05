#! venv/bin/python3

import requests
import lxml.html as html
import os
import datetime
import json

HOME_URL = 'https://www.larepublica.co/'

XPATH_LINK_TO_ARTICLE = '//text-fill/a/@href'
XPATH_TITLE = '//div[contains(@class, "OpeningPostNormal")]//h2/span//text()'
XPATH_SUMMARY = '//div[@class="lead"]/p//text()'
XPATH_BODY = '//div[@class="html-content"]/p'

def parse_new(link, today):
   try:
      response = requests.get(link)

      if response.status_code == 200:
         news_body = response.content.decode('utf-8')
         parsed = html.fromstring(news_body)

         try:
            news_title = parsed.xpath(XPATH_TITLE)[0]
            news_title = news_title.replace('\"', '').strip()
            news_summary = parsed.xpath(XPATH_SUMMARY)[0].strip()
            news_content = parsed.xpath(XPATH_BODY)
         except IndexError:
            return
         
         content_string = ""
         for content in news_content:
            closing = "" if content == news_content[-1] else "\n"
            content_string += f'{content.xpath("string()").strip()}{closing}'

         new = {
            "title": news_title,
            "summary": news_summary,
            "content": content_string,
            "date": today
         }

         return new
      else:
         raise ValueError(f'Error: {response.status_code}')

   except ValueError as ve:
      print(ve)

def parse_home():
   try:
      response = requests.get(HOME_URL)
      if response.status_code == 200:
         home = response.content.decode('utf-8')
         parsed = html.fromstring(home)
         links_to_news = parsed.xpath(XPATH_LINK_TO_ARTICLE)

         today = datetime.date.today().strftime('%d-%m-%Y')
         if not os.path.isdir("news"):
            os.mkdir("news")

         parsed_news = []
         for link in links_to_news:
            parsed_new = parse_new(link, today)
            if parsed_new != None:
               parsed_news.append(parsed_new)

         with open(f'news/{today}.json', 'w', encoding='utf-8') as file:
            json.dump(parsed_news, file, ensure_ascii=False)
      else:
         raise ValueError(f'Error: {response.status_code}')
   except ValueError as ve:
      print(ve)

def run():
   # print("starting program")
   parse_home()

if __name__ == '__main__':
   run()