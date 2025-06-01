import json
import re
import os

import requests

from pathlib import Path
from datetime import datetime

from tqdm import tqdm


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(SCRIPT_DIR, 'storage')

os.makedirs(STORAGE_DIR, exist_ok=True)

def extract_first_unit(text):
  """
  Extract the first unit of a text.
  The unit is a word followed by a space or a single letter followed by an apostrophe.
  """
  text = re.sub(r"«", "", text).strip()
  
  match = re.match(r"^\w+’\b|\w+\s", text)
  return match.group(0) if match else ''

def get_articles_metadata():
  storage_dir = Path('apps/article-urls-grabber/storage')
  json_files = list(storage_dir.glob('*.json'))
  
  all_articles = []
  article_urls = set() 
  
  for json_file in json_files:
    with open(json_file, 'r', encoding='utf-8') as f:
      data = json.load(f)
      for item in data:
        if item['url'] not in article_urls:
          article_urls.add(item['url'])
          all_articles.append(item)
        
  return all_articles

def get_likely_kirundi_articles():
  all_articles = get_articles_metadata()
  
  french_prefixes = set([
    "l’", "le ", "la ", "les ", "un ", "une ", "des ", "du ", "d’", "de ",

    "qui ", "qu’", "que ", "quoi ", "quel ", "quelle ", "quels ", "quelles ",
    "comment ", "pourquoi ", "quand ", "où ", "combien ", "jusqu’", "sur ",

    "je ", "j’", "tu ", "il ", "elle ", "on ", "nous ", "vous ", "ils ", "elles ",
    "ce ", "cette ", "ces ", "ceux ", "celles ", "c’",

    "après ", "avant ", "au-delà ", "aujourd'hui ", "hier ", "demain ", "là ", "ici ", "là-bas ", "là-haut ",

    "en ", "dans ", "avec ", "pour ", "mais ", "donc ", "car ",
    "parce ", "lorsque ", "pendant ", "depuis ", "sans ", "et ", 
    "à ", "au ", "aux ", "par ", "voici ", "voilà ", "ainsi ", "oui, ",

    "sont ", "était ", "avait ", "ont ", "doit ", "peut ", "va ", "aller ", "faire ", "être"
  ])

  
  potential_kirundi_articles = []
  for article in all_articles:
    title = article['title']
    first_unit = extract_first_unit(title).lower()
    if first_unit not in french_prefixes:
      potential_kirundi_articles.append(article)
  
  return potential_kirundi_articles

def get_article_lang(title):
  ollama_url = "http://localhost:11434/api/chat"
  ollama_model = "llama3.2:3b"
  
  response = requests.post(ollama_url, json={
    "model": ollama_model,
    "messages": [
      {
        "role": "system",
        "content": """
You are a language detection assistant. You will receive text in English, French, or Ikinyarwanda, and must 
respond with only "english", "french", or "Ikinyarwanda". If the text is in English or French, respond accordingly. 
If it is in Ikinyarwanda or any language other than English or French, respond with "Ikinyarwanda". 
If the text contains both English and French, respond with either "english" or "french", but never "Ikinyarwanda". 
Use only these exact words with no variations, explanations, or extra text."""
      },
      {"role": "user", "content": title}
    ],
    "stream": False
  })

  if response.status_code != 200:
    print(f"Error from Ollama API: {response.status_code}")
    return False
  
  try:
    data = response.json()
    language = data.get('message', {}).get('content', '').strip().lower()
    return language 
  except requests.exceptions.JSONDecodeError:
    print("Error decoding JSON response")
    return False

def save_articles(articles, filename):
  with open(filename, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
  likely_kirundi_articles = get_likely_kirundi_articles()
  articles_in_kirundi = []
  articles_not_in_kirundi = []
  
  for article in tqdm(likely_kirundi_articles, desc="Filtering articles"):
    title = article['title']
    lang = get_article_lang(title)
    if lang.lower() == "ikinyarwanda":
      articles_in_kirundi.append(article)
    else:
      articles_not_in_kirundi.append(article)

  timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
  save_articles(articles_in_kirundi, os.path.join(STORAGE_DIR, f'articles_in_kirundi_{timestamp}.json'))
  save_articles(articles_not_in_kirundi, os.path.join(STORAGE_DIR, f'articles_not_in_kirundi_{timestamp}.json'))
