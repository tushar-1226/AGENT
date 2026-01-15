/** @type {import('next').NextConfig} */
const nextConfig = {
    // Production optimizations
    reactStrictMode: true,
    swcMinify: true,

    // Performance optimizations
    compress: true,

    // Security headers
    poweredByHeader: false,

    // Environment variables
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    },

    // Output configuration for Docker
    output: 'standalone',

    // Image optimization
    images: {
        domains: ['localhost'],
        unoptimized: false,
    },

    // Webpack configuration
    webpack: (config, { isServer }) => {
        // Additional optimizations can be added here
        return config;
    },

    // API rewrites (optional - for proxying API requests)
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
            },
        ];
    },

    // Headers for security and CORS
    async headers() {
        return [
            {
                source: '/:path*',
                headers: [
                    {
                        key: 'X-DNS-Prefetch-Control',
                        value: 'on'
                    },
                    {
                        key: 'Strict-Transport-Security',
                        value: 'max-age=63072000; includeSubDomains; preload'
                    },
                    {
                        key: 'X-Content-Type-Options',
                        value: 'nosniff'
                    },
                    {
                        key: 'X-Frame-Options',
                        value: 'SAMEORIGIN'
                    },
                    {
                        key: 'X-XSS-Protection',
                        value: '1; mode=block'
                    },
                    {
                        key: 'Referrer-Policy',
                        value: 'origin-when-cross-origin'
                    }
                ],
            },
        ];
    },
}

module.exports = nextConfig
