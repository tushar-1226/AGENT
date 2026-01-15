'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import config from '@/config/api';

interface NewsArticle {
    title: string;
    description: string;
    url: string;
    source: string;
}

export default function DashboardCards() {
    const router = useRouter();
    const [news, setNews] = useState<NewsArticle[]>([]);
    const [loadingNews, setLoadingNews] = useState(true);

    useEffect(() => {
        fetchNews();
    }, []);

    const fetchNews = async () => {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/news`);
            const data = await response.json();

            // Handle both direct articles and nested data structure
            if (data.success && data.data && data.data.articles) {
                setNews(data.data.articles.slice(0, 3));
            } else if (data.articles) {
                setNews(data.articles.slice(0, 3));
            }
        } catch (error) {
            console.error('Error fetching news:', error);
        } finally {
            setLoadingNews(false);
        }
    };

    return (
        <div className="px-8 py-16">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 stagger">

                {/* Model Documentation Card - NEW */}
                <div
                    className="glass-card p-7 cursor-pointer hover:border-blue-500/50 transition-all duration-200"
                    onClick={() => router.push('/dashboard')}
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 flex items-center justify-center">

                        </div>
                        <h3 className="text-xl font-semibold text-white tracking-tight">
                            Documentation
                        </h3>
                    </div>
                    <p className="text-gray-400 text-sm leading-relaxed mb-4">
                        View comprehensive model documentation, API references, and usage examples
                    </p>
                    <div className="flex items-center gap-2 text-blue-400 text-sm font-medium">
                        Open Docs
                        <span>→</span>
                    </div>
                </div>

                {/* Quick Actions Card */}
                <div className="glass-card p-7">
                    <h3 className="text-xl font-semibold text-white mb-6 tracking-tight">
                        Quick Actions
                    </h3>
                    <div className="space-y-3">
                        {['Data Analysis', 'Draft an Email', 'Set a Reminder'].map((action, idx) => (
                            <button
                                key={idx}
                                className="w-full p-4 text-left rounded-xl bg-white/[0.03] border border-white/[0.08] hover:bg-white/[0.06] hover:border-blue-500/30 transition-all duration-200 text-gray-300 hover:text-white font-medium text-[0.9375rem] shadow-sm hover:shadow-md"
                            >
                                {action}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Recent Files Card */}
                <div className="glass-card p-7">
                    <h3 className="text-xl font-semibold text-white mb-6 tracking-tight">
                        Recent Files
                    </h3>
                    <div className="space-y-3">
                        {[
                            { name: 'Market Report.pdf', icon: 'PDF', size: '2.4 MB' },
                            { name: 'Project Plan.docx', icon: 'DOC', size: '1.8 MB' },
                            { name: 'Budget_2022.xlsx', icon: 'XLS', size: '856 KB' },
                        ].map((file, idx) => (
                            <div
                                key={idx}
                                className="flex items-center gap-3.5 p-3 rounded-lg hover:bg-white/[0.04] transition-all duration-200 cursor-pointer group"
                            >
                                <span className="text-2xl flex-shrink-0">{file.icon}</span>
                                <div className="flex-1 min-w-0">
                                    <p className="text-[0.9375rem] text-gray-300 group-hover:text-white truncate font-medium">
                                        {file.name}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-0.5">{file.size}</p>
                                </div>
                            </div>
                        ))}
                        <a
                            href="#"
                            className="text-sm text-blue-400 hover:text-blue-300 inline-flex items-center gap-1.5 mt-5 font-medium transition-colors duration-200"
                        >
                            View All
                            <span className="text-base">→</span>
                        </a>
                    </div>
                </div>

                {/* Recent News Card */}
                <div className="glass-card p-7">
                    <div className="flex items-center gap-2 mb-6">

                        <h3 className="text-xl font-semibold text-white tracking-tight">
                            Recent News
                        </h3>
                    </div>
                    <div className="space-y-4">
                        {loadingNews ? (
                            <div className="flex items-center justify-center py-8">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                            </div>
                        ) : news.length > 0 ? (
                            news.map((article, idx) => (
                                <a
                                    key={idx}
                                    href={article.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="block p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 hover:border-blue-500/40 transition-all duration-200 group"
                                >
                                    <p className="text-sm text-gray-300 leading-relaxed group-hover:text-white">
                                        <span className="font-semibold text-blue-400">{article.source}:</span>
                                        <br />
                                        <span className="text-gray-400 group-hover:text-gray-300 line-clamp-2">
                                            {article.title}
                                        </span>
                                    </p>
                                </a>
                            ))
                        ) : (
                            <div className="p-5 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                                <p className="text-sm text-gray-400 text-center">
                                    No news available. Add NEWS_API_KEY to .env
                                </p>
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
