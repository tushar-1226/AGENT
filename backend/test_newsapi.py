#!/usr/bin/env python3
"""
Test NewsAPI.org integration
Run this to verify your NEWS_API_KEY works correctly
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_newsapi():
    """Test NewsAPI.org integration"""
    api_key = os.getenv('NEWS_API_KEY')
    
    if not api_key:
        print(" ERROR: NEWS_API_KEY not found in environment")
        print("   Please set NEWS_API_KEY in your .env file")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...")
    print("\n Testing NewsAPI.org connection...\n")
    
    # Test endpoint
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'category': 'technology',
        'country': 'us',
        'pageSize': 5,
        'apiKey': api_key
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'ok':
                        articles = data.get('articles', [])
                        print(f" SUCCESS! NewsAPI.org is working correctly")
                        print(f"   Retrieved {len(articles)} articles\n")
                        
                        print(" Latest Headlines:\n")
                        for i, article in enumerate(articles[:3], 1):
                            print(f"{i}. {article.get('title', 'No title')}")
                            print(f"   Source: {article.get('source', {}).get('name', 'Unknown')}")
                            print(f"   URL: {article.get('url', '')}\n")
                        
                        return True
                    else:
                        error_msg = data.get('message', 'Unknown error')
                        print(f" ERROR: {error_msg}")
                        return False
                        
                elif response.status == 401:
                    print(" ERROR: Authentication failed")
                    print("   Your API key is invalid or expired")
                    print("   Get a new key from: https://newsapi.org/account")
                    return False
                    
                elif response.status == 429:
                    print(" ERROR: Rate limit exceeded")
                    print("   You've made too many requests")
                    print("   Free tier allows 100 requests/day")
                    return False
                    
                else:
                    print(f" ERROR: HTTP {response.status}")
                    text = await response.text()
                    print(f"   Response: {text[:200]}")
                    return False
                    
    except aiohttp.ClientError as e:
        print(f" CONNECTION ERROR: {str(e)}")
        print("   Check your internet connection")
        return False
        
    except Exception as e:
        print(f" UNEXPECTED ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  NewsAPI.org Integration Test")
    print("=" * 50)
    print()
    
    result = asyncio.run(test_newsapi())
    
    print()
    print("=" * 50)
    if result:
        print(" NewsAPI.org is ready for deployment!")
    else:
        print(" Please fix the errors above")
    print("=" * 50)
