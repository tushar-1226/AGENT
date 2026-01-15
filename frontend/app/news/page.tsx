'use client';

import { useEffect, useState } from 'react';
import config from '@/config/api';

interface NewsArticle {
    title: string;
    description: string;
    url: string;
    source: string;
}

export default function NewsPage() {
    const [news, setNews] = useState<NewsArticle[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchNews();
    }, []);

    const fetchNews = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/news`);
            const data = await response.json();
            if (data.success && data.data && data.data.articles) {
                setNews(data.data.articles);
            }
        } catch (error) {
            console.error('Error fetching news:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold text-white mb-6">Recent News</h1>
                <div className="space-y-4">
                    {loading ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                        </div>
                    ) : (
                        news.map((article, idx) => (
                            <a
                                key={idx}
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block glass-card p-6 hover:border-blue-500/30 transition-all"
                            >
                                <div className="flex items-start gap-4">
                                    <div className="flex-1">
                                        <div className="text-sm text-blue-400 mb-2">{article.source}</div>
                                        <h3 className="text-lg font-semibold text-white mb-2">{article.title}</h3>
                                        <p className="text-sm text-gray-400">{article.description}</p>
                                    </div>
                                </div>
                            </a>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
