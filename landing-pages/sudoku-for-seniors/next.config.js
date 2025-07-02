/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    CONVERTKIT_API_KEY: process.env.CONVERTKIT_API_KEY,
    CONVERTKIT_FORM_ID: process.env.CONVERTKIT_FORM_ID,
    GA_MEASUREMENT_ID: process.env.GA_MEASUREMENT_ID,
    FB_PIXEL_ID: process.env.FB_PIXEL_ID,
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;