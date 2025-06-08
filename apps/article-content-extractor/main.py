import json

import requests
import markdownify

from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


def get_kirundi_article_urls():
  try:
    current_dir = Path(__file__).parent
    json_path = current_dir.parent / "kirundi-articles-filter" / "storage" / "articles_in_kirundi_20250601_201145.json"
    
    with open(json_path, "r", encoding="utf-8") as f:
      articles = json.load(f)
    return articles
  except Exception as e:
    print(f"Error reading articles file: {e}")
    return []

def get_article_content(url: str):
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
  }
  page = requests.get(url, headers=headers).text
  soup = BeautifulSoup(page, "html.parser")
  article = soup.find("article")
  if not article:
    raise Exception(f"No article found for url: {url}")
    
  content = article.find(class_="entry-content")
  if not content:
    raise Exception(f"No content found for url: {url}")
    
  did_you_find = content.find(class_="did-you-find")
  if did_you_find:
    did_you_find.decompose()
    
  return content.prettify()

def save_article_content(article_content: str, article: dict):
  markdown_content = f"""Title: {article['title']}
Author: {article['author']}
Source: {article['url']}
Date: {article['postedAt']}
Category: {article['category']}

========================================

{markdownify.markdownify(article_content)}"""
  
  current_dir = Path(__file__).parent
  storage_dir = current_dir / "storage"
  storage_dir.mkdir(exist_ok=True)
  
  parsed_url = urlparse(article["url"])
  file_path = parsed_url.path.strip("/").replace("/", "_")  
  file_path = storage_dir / f"yaga_burundi__{file_path}.md"
  with open(file_path, "w", encoding="utf-8") as f:
    f.write(markdown_content)
    print(f"Article {article['url']} processed and saved")

def upload_article_content(article_content: str, article: dict):
  pass

def is_already_processed(url: str):
  current_dir = Path(__file__).parent
  storage_dir = current_dir / "storage"
  parsed_url = urlparse(url)
  file_path = storage_dir / f"yaga_burundi__{parsed_url.path.strip("/").replace("/", "_")}.md"
  
  if not file_path.exists():
    return False
    
  try:
    with open(file_path, "r", encoding="utf-8") as f:
      content = f.read().strip()
      result = len(content) > 0
      
    if result:
      print(f"Article {url} already processed")
      
    return result
  except Exception as e:
    print(f"Error reading file {file_path}: {e}")
    return False

def process_articles():
  articles = get_kirundi_article_urls()
  
  for article in articles:
    url = article["url"]
    if not is_already_processed(url):
      article_content = get_article_content(url)
      save_article_content(article_content, article)
      
    # upload_article_content(article_content, article)

if __name__ == "__main__":
  process_articles()
