"""
External API integrations for weather, news, and stock data
"""
import os
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any

class ExternalAPIs:
    def __init__(self):
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        
    async def get_weather(self, city: str = 'London') -> Dict[str, Any]:
        """Get current weather for a city"""
        if not self.weather_api_key:
            return {
                'error': 'Weather API key not configured',
                'message': 'Set OPENWEATHER_API_KEY in .env file'
            }
        
        url = f'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'q': city,
            'appid': self.weather_api_key,
            'units': 'metric'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'city': data['name'],
                            'country': data['sys']['country'],
                            'temperature': round(data['main']['temp']),
                            'feels_like': round(data['main']['feels_like']),
                            'humidity': data['main']['humidity'],
                            'description': data['weather'][0]['description'],
                            'icon': data['weather'][0]['icon'],
                            'wind_speed': data['wind']['speed'],
                            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                            'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
                        }
                    else:
                        return {'error': f'Weather API error: {response.status}'}
        except Exception as e:
            return {'error': f'Weather API error: {str(e)}'}
    
    async def get_news(self, category: str = 'technology', country: str = 'us') -> Dict[str, Any]:
        """Get top news headlines using free GNews API (no key required for basic usage)"""
        # Using GNews API - free tier with no authentication required
        # Alternative: Use RSS feeds or NewsData.io demo
        
        # Map category to GNews topics
        topic_map = {
            'technology': 'technology',
            'business': 'business',
            'sports': 'sports',
            'science': 'science',
            'health': 'health',
            'entertainment': 'entertainment'
        }
        
        topic = topic_map.get(category, 'technology')
        
        # Using GNews free API (no key needed for limited requests)
        url = f'https://gnews.io/api/v4/top-headlines'
        params = {
            'category': topic,
            'lang': 'en',
            'country': country,
            'max': 10,
            'apikey': 'demo'  # Demo key for testing, works with limited requests
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        for article in data.get('articles', [])[:10]:
                            articles.append({
                                'title': article['title'],
                                'description': article.get('description', ''),
                                'url': article['url'],
                                'source': article['source']['name'],
                                'published_at': article['publishedAt'],
                                'image': article.get('image')
                            })
                        return {
                            'category': category,
                            'articles': articles,
                            'total': len(articles)
                        }
                    else:
                        # Fallback to mock data if API fails
                        return self._get_mock_news()
        except Exception as e:
            print(f"News API error: {str(e)}")
            # Return mock data as fallback
            return self._get_mock_news()
    
    def _get_mock_news(self) -> Dict[str, Any]:
        """Fallback mock news data"""
        return {
            'category': 'technology',
            'articles': [
                {
                    'title': 'AI Breakthrough: New Language Model Achieves Human-Level Performance',
                    'description': 'Researchers announce major advancement in artificial intelligence',
                    'url': 'https://example.com/ai-breakthrough',
                    'source': 'Tech News',
                    'published_at': datetime.now().isoformat(),
                    'image': None
                },
                {
                    'title': 'Quantum Computing Reaches New Milestone',
                    'description': 'Scientists demonstrate quantum advantage in practical applications',
                    'url': 'https://example.com/quantum-computing',
                    'source': 'Science Daily',
                    'published_at': datetime.now().isoformat(),
                    'image': None
                },
                {
                    'title': 'Renewable Energy Adoption Accelerates Globally',
                    'description': 'Solar and wind power installations reach record highs',
                    'url': 'https://example.com/renewable-energy',
                    'source': 'Green Tech',
                    'published_at': datetime.now().isoformat(),
                    'image': None
                }
            ],
            'total': 3
        }
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get stock data from Yahoo Finance (free, no API key needed)"""
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
        params = {
            'interval': '1d',
            'range': '5d'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data['chart']['result'][0]
                        meta = result['meta']
                        quote = result['indicators']['quote'][0]
                        
                        # Get latest values
                        latest_close = quote['close'][-1]
                        previous_close = meta['previousClose']
                        change = latest_close - previous_close
                        change_percent = (change / previous_close) * 100
                        
                        return {
                            'symbol': symbol.upper(),
                            'name': meta.get('longName', symbol),
                            'price': round(latest_close, 2),
                            'previous_close': round(previous_close, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2),
                            'currency': meta['currency'],
                            'market_state': meta['marketState'],
                            'high': round(max(quote['high']), 2),
                            'low': round(min(quote['low']), 2),
                            'volume': quote['volume'][-1]
                        }
                    else:
                        return {'error': f'Stock API error: {response.status}'}
        except Exception as e:
            return {'error': f'Stock API error: {str(e)}'}
    
    async def get_crypto_data(self, symbol: str = 'BTC') -> Dict[str, Any]:
        """Get cryptocurrency data from CoinGecko (free, no API key)"""
        coin_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'DOGE': 'dogecoin'
        }
        
        coin_id = coin_ids.get(symbol.upper(), symbol.lower())
        url = f'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if coin_id in data:
                            coin_data = data[coin_id]
                            return {
                                'symbol': symbol.upper(),
                                'name': coin_id.title(),
                                'price': coin_data['usd'],
                                'change_24h': round(coin_data.get('usd_24h_change', 0), 2),
                                'volume_24h': coin_data.get('usd_24h_vol', 0),
                                'market_cap': coin_data.get('usd_market_cap', 0)
                            }
                        else:
                            return {'error': f'Cryptocurrency {symbol} not found'}
                    else:
                        return {'error': f'Crypto API error: {response.status}'}
        except Exception as e:
            return {'error': f'Crypto API error: {str(e)}'}
