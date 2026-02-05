"""
Download 300 Wikipedia articles, clean them, and save the first 2 pages
"""

import wikipedia
import re
import os
import time
from pathlib import Path
import json

class WikipediaDownloader:
    def __init__(self, output_folder="wiki_articles", num_articles=300):
        self.output_folder = output_folder
        self.num_articles = num_articles
        self.articles_data = []
        
        # Create output directory
        Path(self.output_folder).mkdir(exist_ok=True)
        
        # Topics to search for diverse articles
        self.search_topics = [
            # Science & Technology
            "artificial intelligence", "quantum physics", "biotechnology", "neuroscience",
            "computer science", "genetics", "astronomy", "chemistry", "robotics", "nanotechnology",
            # History
            "world war", "ancient civilization", "renaissance", "industrial revolution",
            "medieval history", "cold war", "roman empire", "ancient egypt", "vikings",
            # Geography & Places
            "mountain", "river", "city", "country", "ocean", "continent", "island",
            "national park", "landmark", "desert",
            # Arts & Culture
            "painting", "sculpture", "literature", "music", "cinema", "theater",
            "architecture", "poetry", "novel", "composer",
            # Sports
            "olympic games", "football", "basketball", "tennis", "athletics",
            "swimming", "chess", "martial arts", "cricket", "baseball",
            # Nature & Biology
            "mammal", "bird", "reptile", "fish", "plant", "tree", "flower",
            "ecosystem", "endangered species", "dinosaur",
            # Philosophy & Religion
            "philosopher", "philosophy", "religion", "mythology", "ethics",
            "buddhism", "hinduism", "christianity", "islam",
            # Economy & Business
            "company", "entrepreneur", "economics", "finance", "trade",
            "industry", "innovation", "market", "corporation",
        ]
    
    def clean_text(self, text):
        """Clean text from odd symbols and formatting"""
        # Remove references like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\'\"\(\)]', ' ', text)
        
        # Remove multiple spaces again
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def get_first_n_pages(self, text, num_pages=2, chars_per_page=3000):
        """Extract approximately the first N pages of text"""
        total_chars = num_pages * chars_per_page
        
        # Get the text up to total_chars
        excerpt = text[:total_chars]
        
        # Try to end at a sentence boundary
        last_period = excerpt.rfind('.')
        if last_period > total_chars * 0.8:  # If we're reasonably close
            excerpt = excerpt[:last_period + 1]
        
        return excerpt
    
    def download_articles(self):
        """Download Wikipedia articles"""
        print(f"Downloading {self.num_articles} Wikipedia articles...")
        
        downloaded = 0
        attempts = 0
        max_attempts = self.num_articles * 3  # Allow some failures
        
        while downloaded < self.num_articles and attempts < max_attempts:
            attempts += 1
            
            try:
                # Pick a random search topic
                import random
                topic = random.choice(self.search_topics)
                
                # Search for articles
                search_results = wikipedia.search(topic, results=10)
                
                if not search_results:
                    continue
                
                # Pick a random article from results
                article_title = random.choice(search_results)
                
                # Skip if already downloaded
                if any(article['title'] == article_title for article in self.articles_data):
                    continue
                
                # Try to get the article
                try:
                    page = wikipedia.page(article_title, auto_suggest=False)
                except wikipedia.exceptions.DisambiguationError as e:
                    # Pick first option from disambiguation
                    if e.options:
                        page = wikipedia.page(e.options[0], auto_suggest=False)
                    else:
                        continue
                
                # Clean the content
                cleaned_content = self.clean_text(page.content)
                
                # Get first 2 pages
                excerpt = self.get_first_n_pages(cleaned_content, num_pages=2)
                
                # Skip if too short
                if len(excerpt) < 500:
                    print(f"⚠ Skipping '{article_title}' (too short)")
                    continue
                
                # Save to file
                filename = f"wiki_{downloaded+1:03d}.txt"
                filepath = os.path.join(self.output_folder, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(excerpt)
                
                # Store metadata
                self.articles_data.append({
                    'id': downloaded + 1,
                    'title': page.title,
                    'filename': filename,
                    'url': page.url,
                    'length': len(excerpt)
                })
                
                downloaded += 1
                
                if downloaded % 10 == 0:
                    print(f"✓ Downloaded {downloaded}/{self.num_articles} articles")
                
                # Small delay to avoid overwhelming Wikipedia API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠ Error: {str(e)}")
                continue
        
        print(f"\n✓ Successfully downloaded {downloaded} articles")
        
        # Save metadata
        metadata_file = os.path.join(self.output_folder, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Metadata saved to {metadata_file}")
        
        return self.articles_data


if __name__ == "__main__":
    downloader = WikipediaDownloader(
        output_folder="wiki_articles",
        num_articles=300
    )
    
    articles = downloader.download_articles()
    
    print(f"\n✓ All done! {len(articles)} articles saved in 'wiki_articles/' folder")
    print(f"✓ Average article length: {sum(a['length'] for a in articles) / len(articles):.0f} characters")
