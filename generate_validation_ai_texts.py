#!/usr/bin/env python3
"""
Generate AI texts for validation set Wikipedia articles.
"""

import json
import os
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def load_metadata(filepath):
    """Load metadata from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_metadata(filepath, data):
    """Save metadata to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_ai_text(title, groq_client):
    """Generate AI text for a given Wikipedia article title."""
    prompt = f"""Write a comprehensive, detailed article about "{title}" in an encyclopedic style. 
The article MUST be at least 6000 characters long (approximately 1000-1200 words).
Be informative and thorough with multiple well-developed paragraphs covering:
- Introduction and overview
- Historical background or context
- Key concepts, features, or characteristics
- Detailed explanations with examples
- Current state or modern developments
- Significance and impact

Write ONLY the article content with no meta-commentary. Make it comprehensive and detailed to reach 6000+ characters."""
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2500  # Increased to generate longer text in one call
    )
    
    text = response.choices[0].message.content.strip()
    return text

def main():
    print("="*60)
    print("Generating AI texts for validation set")
    print("="*60)
    
    # Load validation Wikipedia metadata
    print("\nLoading validation Wikipedia metadata...")
    wiki_metadata = load_metadata('validation_set/metadata.json')
    print(f"Found {len(wiki_metadata)} Wikipedia articles")
    
    # Create output directory for validation AI texts
    output_dir = 'validation_ai_texts'
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize Groq client
    print("Initializing Groq API...")
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    # Generate AI texts
    ai_metadata = []
    total_length = 0
    
    print(f"\nGenerating {len(wiki_metadata)} AI texts...")
    print("(This will take approximately 10 minutes)\n")
    
    start_time = time.time()
    
    for idx, wiki_article in enumerate(wiki_metadata, 1):
        title = wiki_article['title']
        article_id = wiki_article['id']
        filename = f'validation_ai_{article_id:03d}.txt'
        filepath = os.path.join(output_dir, filename)
        
        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"[{idx}/{len(wiki_metadata)}] Skipping {filename} (already exists)")
            # Load existing file length for metadata
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            ai_metadata.append({
                'id': article_id,
                'title': title,
                'filename': filename,
                'length': len(text)
            })
            total_length += len(text)
            continue
        
        print(f"[{idx}/{len(wiki_metadata)}] Generating {filename} for '{title}'...")
        
        try:
            # Generate AI text
            text = generate_ai_text(title, groq_client)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Add to metadata
            ai_metadata.append({
                'id': article_id,
                'title': title,
                'filename': filename,
                'length': len(text)
            })
            
            total_length += len(text)
            
            print(f"    ✓ Generated {len(text)} characters")
            
            # Rate limiting (0.5 seconds between requests)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue
    
    # Save metadata
    print(f"\nSaving metadata to {output_dir}/metadata.json...")
    save_metadata(f'{output_dir}/metadata.json', ai_metadata)
    
    # Calculate statistics
    elapsed_time = time.time() - start_time
    avg_length = total_length / len(ai_metadata) if ai_metadata else 0
    
    print("\n" + "="*60)
    print("✓ Validation AI text generation complete!")
    print(f"  Total AI texts: {len(ai_metadata)}")
    print(f"  Total length: {total_length:,} characters")
    print(f"  Average length: {avg_length:.0f} characters")
    print(f"  Time elapsed: {elapsed_time/60:.1f} minutes")
    print(f"  Output directory: {output_dir}/")
    print("="*60)

if __name__ == '__main__':
    main()
