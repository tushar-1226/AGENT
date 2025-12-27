/** @type {import('next').NextConfig} */
const nextConfig = {
    // Enable SWC minification for faster builds
    swcMinify: true,

    // Optimize production builds
    productionBrowserSourceMaps: false,

    // Webpack optimizations
    webpack: (config, { isServer }) => {
        // Disable performance warnings in development
        config.performance = {
            hints: false,
        };

        // Optimize chunks
        if (!isServer) {
            config.optimization = {
                ...config.optimization,
                splitChunks: {
                    chunks: 'all',
                    cacheGroups: {
                        default: false,
                        vendors: false,
                        // Vendor chunk for node_modules
                        vendor: {
                            name: 'vendor',
                            chunks: 'all',
                            test: /node_modules/,
                            priority: 20,
                        },
                        // Common chunk for shared code
                        common: {
                            name: 'common',
                            minChunks: 2,
                            chunks: 'all',
                            priority: 10,
                            reuseExistingChunk: true,
                            enforce: true,
                        },
                        // Separate chunk for Monaco Editor
                        monaco: {
                            name: 'monaco',
                            test: /[\\/]node_modules[\\/](@monaco-editor|monaco-editor)[\\/]/,
                            priority: 30,
                        },
                        // Separate chunk for Recharts
                        recharts: {
                            name: 'recharts',
                            test: /[\\/]node_modules[\\/](recharts)[\\/]/,
                            priority: 30,
                        },
                    },
                },
            };
        }

        return config;
    },

    // Experimental features
    experimental: {
        optimizeCss: true,
    },
};

// Bundle analyzer (only in analyze mode)
const withBundleAnalyzer = require('@next/bundle-analyzer')({
    enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer(nextConfig);
