"""
Complete pipeline: Download Wikipedia articles, generate AI texts, and load dataset
"""

import sys
import time
from download_wikipedia_articles import WikipediaDownloader
from generate_ai_texts import AITextGenerator
from load_dataset import DatasetLoader

def main():
    print("="*70)
    print("AI TEXT DETECTION DATASET GENERATION PIPELINE")
    print("="*70)
    
    # Step 1: Download Wikipedia articles
    print("\n" + "="*70)
    print("STEP 1: Downloading Wikipedia Articles")
    print("="*70 + "\n")
    
    downloader = WikipediaDownloader(
        output_folder="wiki_articles",
        num_articles=300
    )
    
    articles = downloader.download_articles()
    
    if len(articles) < 100:
        print("\n⚠ Warning: Less than 100 articles downloaded. Continue anyway? (y/n)")
        response = input().strip().lower()
        if response != 'y':
            print("Aborted.")
            return
    
    time.sleep(2)
    
    # Step 2: Generate AI texts
    print("\n" + "="*70)
    print("STEP 2: Generating AI Texts")
    print("="*70 + "\n")
    
    generator = AITextGenerator(
        metadata_file="wiki_articles/metadata.json",
        output_folder="ai_generated_texts"
    )
    
    ai_texts = generator.generate_all_texts()
    
    time.sleep(2)
    
    # Step 3: Load dataset
    print("\n" + "="*70)
    print("STEP 3: Loading Dataset")
    print("="*70 + "\n")
    
    loader = DatasetLoader(
        wiki_folder="wiki_articles",
        ai_folder="ai_generated_texts"
    )
    
    wiki_list, ai_list = loader.load_all()
    loader.print_statistics()
    loader.sample_texts(n=2)
    
    # Final summary
    print("\n" + "="*70)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"\n✓ Wikipedia articles: {len(wiki_list)}")
    print(f"✓ AI-generated texts: {len(ai_list)}")
    print(f"\nData is ready for training AI detection models!")
    print(f"\nFolders created:")
    print(f"  - wiki_articles/     (human-written Wikipedia texts)")
    print(f"  - ai_generated_texts/ (AI-generated texts)")
    print(f"\nTo load the data in your scripts:")
    print(f"  from load_dataset import DatasetLoader")
    print(f"  loader = DatasetLoader()")
    print(f"  wiki_list, ai_list = loader.load_all()")
    
    return wiki_list, ai_list


if __name__ == "__main__":
    try:
        wiki_list, ai_list = main()
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
