'use client';

import { useState, useEffect } from 'react';
import config from '@/config/api';

interface WeatherData {
    city: string;
    temperature: number;
    description: string;
    humidity: number;
    wind_speed: number;
    icon: string;
}

interface NewsArticle {
    title: string;
    description: string;
    url: string;
    source: string;
    published_at: string;
}

interface StockData {
    symbol: string;
    price: number;
    change: number;
    change_percent: number;
}

export default function EnhancedDailyBriefing() {
    const [weather, setWeather] = useState<WeatherData | null>(null);
    const [news, setNews] = useState<NewsArticle[]>([]);
    const [stocks, setStocks] = useState<StockData[]>([]);
    const [city, setCity] = useState('London');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadAllData();
    }, []);

    const loadAllData = async () => {
        setLoading(true);
        await Promise.all([
            loadWeather(),
            loadNews(),
            loadStocks()
        ]);
        setLoading(false);
    };

    const loadWeather = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/weather?city=${city}`);
            const data = await response.json();
            if (data.success && !data.data.error) {
                setWeather(data.data);
            }
        } catch (error) {
            console.error('Weather error:', error);
        }
    };

    const loadNews = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/news?category=technology`);
            const data = await response.json();
            if (data.success && !data.data.error) {
                setNews(data.data.articles || []);
            }
        } catch (error) {
            console.error('News error:', error);
        }
    };

    const loadStocks = async () => {
        try {
            const symbols = ['AAPL', 'GOOGL', 'MSFT'];
            const stockPromises = symbols.map(symbol =>
                fetch(`${config.apiBaseUrl}/api/stocks/${symbol}`).then(r => r.json())
            );
            const results = await Promise.all(stockPromises);
            const stockData = results
                .filter(r => r.success && !r.data.error)
                .map(r => r.data);
            setStocks(stockData);
        } catch (error) {
            console.error('Stocks error:', error);
        }
    };

    if (loading) {
        return (
            <div className="glass-card p-8 text-center">
                <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
                <p className="text-gray-400 mt-4">Loading briefing...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Weather */}
            {weather && (
                <div className="glass-card p-6 border-blue-500/20">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                            <span>☀️</span> Weather
                        </h3>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={city}
                                onChange={(e) => setCity(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && loadWeather()}
                                className="px-3 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white text-sm focus:outline-none focus:border-blue-500/30"
                                placeholder="City"
                            />
                            <button
                                onClick={loadWeather}
                                className="px-3 py-1 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 text-sm transition-all"
                            >
                                Update
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="text-center">
                            <div className="text-5xl font-bold text-white">{weather.temperature}°C</div>
                            <div className="text-sm text-gray-400 mt-1">{weather.city}</div>
                        </div>
                        <div className="flex-1">
                            <div className="text-lg text-gray-300 capitalize">{weather.description}</div>
                            <div className="grid grid-cols-2 gap-2 mt-3 text-sm text-gray-400">
                                <div>💧 Humidity: {weather.humidity}%</div>
                                <div>💨 Wind: {weather.wind_speed} m/s</div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Stocks */}
            {stocks.length > 0 && (
                <div className="glass-card p-6 border-green-500/20">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <span>📈</span> Stocks
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {stocks.map((stock) => (
                            <div key={stock.symbol} className="p-4 rounded-lg bg-white/[0.02] border border-white/[0.05]">
                                <div className="text-sm text-gray-400">{stock.symbol}</div>
                                <div className="text-2xl font-bold text-white mt-1">${stock.price}</div>
                                <div className={`text-sm mt-1 ${stock.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {stock.change >= 0 ? '↑' : '↓'} {Math.abs(stock.change_percent)}%
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* News */}
            {news.length > 0 && (
                <div className="glass-card p-6 border-purple-500/20">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <span>Top Tech News</span>
                    </h3>
                    <div className="space-y-3 max-h-96 overflow-y-auto scrollbar-dark">
                        {news.slice(0, 5).map((article, index) => (
                            <a
                                key={index}
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block p-4 rounded-lg bg-white/[0.02] border border-white/[0.05] hover:border-purple-500/30 hover:bg-white/[0.04] transition-all"
                            >
                                <h4 className="text-sm font-semibold text-white mb-1 line-clamp-2">
                                    {article.title}
                                </h4>
                                <p className="text-xs text-gray-400 line-clamp-2 mb-2">
                                    {article.description}
                                </p>
                                <div className="flex items-center gap-2 text-xs text-gray-500">
                                    <span>{article.source}</span>
                                    <span>•</span>
                                    <span>{new Date(article.published_at).toLocaleDateString()}</span>
                                </div>
                            </a>
                        ))}
                    </div>
                </div>
            )}

            {/* Refresh Button */}
            <button
                onClick={loadAllData}
                className="w-full py-3 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-white font-semibold transition-all"
            >
                🔄 Refresh All
            </button>
        </div>
    );
}
