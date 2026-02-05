"""
Load Wikipedia articles and AI-generated texts into lists for analysis
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Tuple

class DatasetLoader:
    def __init__(self, wiki_folder="wiki_articles", ai_folder="ai_generated_texts"):
        self.wiki_folder = wiki_folder
        self.ai_folder = ai_folder
        self.wiki_list = []
        self.ai_list = []
        self.wiki_metadata = []
        self.ai_metadata = []
    
    def load_wikipedia_articles(self) -> List[str]:
        """Load all Wikipedia articles into a list"""
        print(f"Loading Wikipedia articles from '{self.wiki_folder}'...")
        
        # Load metadata
        metadata_path = os.path.join(self.wiki_folder, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.wiki_metadata = json.load(f)
        
        # Load articles in order
        for item in sorted(self.wiki_metadata, key=lambda x: x['id']):
            filepath = os.path.join(self.wiki_folder, item['filename'])
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.wiki_list.append(content)
        
        print(f"✓ Loaded {len(self.wiki_list)} Wikipedia articles")
        return self.wiki_list
    
    def load_ai_texts(self) -> List[str]:
        """Load all AI-generated texts into a list"""
        print(f"Loading AI-generated texts from '{self.ai_folder}'...")
        
        # Load metadata
        metadata_path = os.path.join(self.ai_folder, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.ai_metadata = json.load(f)
        
        # Load texts in order
        for item in sorted(self.ai_metadata, key=lambda x: x['id']):
            filepath = os.path.join(self.ai_folder, item['filename'])
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.ai_list.append(content)
        
        print(f"✓ Loaded {len(self.ai_list)} AI-generated texts")
        return self.ai_list
    
    def load_all(self) -> Tuple[List[str], List[str]]:
        """Load both Wikipedia articles and AI texts"""
        self.load_wikipedia_articles()
        self.load_ai_texts()
        
        return self.wiki_list, self.ai_list
    
    def get_paired_data(self) -> List[Dict]:
        """Get paired data with metadata"""
        paired = []
        
        for i in range(min(len(self.wiki_list), len(self.ai_list))):
            wiki_meta = self.wiki_metadata[i] if i < len(self.wiki_metadata) else {}
            ai_meta = self.ai_metadata[i] if i < len(self.ai_metadata) else {}
            
            paired.append({
                'id': i + 1,
                'title': wiki_meta.get('title', f'Article {i+1}'),
                'wiki_text': self.wiki_list[i],
                'ai_text': self.ai_list[i],
                'wiki_length': len(self.wiki_list[i]),
                'ai_length': len(self.ai_list[i]),
            })
        
        return paired
    
    def print_statistics(self):
        """Print dataset statistics"""
        print("\n" + "="*60)
        print("DATASET STATISTICS")
        print("="*60)
        
        print(f"\nWikipedia Articles:")
        print(f"  Total: {len(self.wiki_list)}")
        if self.wiki_list:
            wiki_lengths = [len(text) for text in self.wiki_list]
            print(f"  Average length: {sum(wiki_lengths) / len(wiki_lengths):.0f} characters")
            print(f"  Min length: {min(wiki_lengths)} characters")
            print(f"  Max length: {max(wiki_lengths)} characters")
        
        print(f"\nAI-Generated Texts:")
        print(f"  Total: {len(self.ai_list)}")
        if self.ai_list:
            ai_lengths = [len(text) for text in self.ai_list]
            print(f"  Average length: {sum(ai_lengths) / len(ai_lengths):.0f} characters")
            print(f"  Min length: {min(ai_lengths)} characters")
            print(f"  Max length: {max(ai_lengths)} characters")
        
        print("\n" + "="*60)
    
    def sample_texts(self, n=3):
        """Print sample texts for verification"""
        print(f"\n{'='*60}")
        print(f"SAMPLE TEXTS (first {n})")
        print("="*60)
        
        for i in range(min(n, len(self.wiki_list), len(self.ai_list))):
            if i < len(self.wiki_metadata):
                title = self.wiki_metadata[i].get('title', f'Article {i+1}')
            else:
                title = f'Article {i+1}'
            
            print(f"\n[{i+1}] {title}")
            print("-" * 60)
            
            print("\n📄 Wikipedia (first 200 chars):")
            print(self.wiki_list[i][:200] + "...")
            
            print("\n🤖 AI-Generated (first 200 chars):")
            print(self.ai_list[i][:200] + "...")
            print()


def main():
    """Main function to demonstrate usage"""
    # Create loader instance
    loader = DatasetLoader(
        wiki_folder="wiki_articles",
        ai_folder="ai_generated_texts"
    )
    
    # Load all data
    wiki_list, ai_list = loader.load_all()
    
    # Print statistics
    loader.print_statistics()
    
    # Show samples
    loader.sample_texts(n=3)
    
    # Get paired data
    paired_data = loader.get_paired_data()
    
    print(f"\n✓ Dataset ready for analysis!")
    print(f"✓ {len(paired_data)} paired samples available")
    print(f"\nYou can now use:")
    print(f"  - wiki_list: List of {len(wiki_list)} Wikipedia articles")
    print(f"  - ai_list: List of {len(ai_list)} AI-generated texts")
    print(f"  - paired_data: List of {len(paired_data)} paired dictionaries")
    
    return wiki_list, ai_list, paired_data


if __name__ == "__main__":
    wiki_list, ai_list, paired_data = main()
