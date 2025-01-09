// @ts-check
import { PHASE_DEVELOPMENT_SERVER } from 'next/constants.js';

export default (phase) => {
  const isDev = phase === PHASE_DEVELOPMENT_SERVER;

  const cdnUrl = 'https://d3h0ehcnk39jwg.cloudfront.net';

  /**
   * @type {import('next').NextConfig}
   */
  const nextConfig = {
    assetPrefix: isDev ? undefined : cdnUrl,

    async rewrites() {
      return [
        {
          source: '/api/:path*/',
          destination: 'http://localhost:8000/api/:path*/',
        },
        {
          source: '/media/:path*/',
          destination: 'http://localhost:8000/media/:path*/',
        },
        {
          source: '/cdn/media/:path*/',
          destination: `${cdnUrl}/media/:path*/`,
        },
      ];
    },

    async headers() {
      return [
        {
          source: '/api/:path*/',
          headers: [
            {
              key: 'Access-Control-Allow-Origin',
              value: '*',
            },
            {
              key: 'Access-Control-Allow-Methods',
              value: 'GET, POST, PUT, DELETE, OPTIONS',
            },
            {
              key: 'Access-Control-Allow-Headers',
              value: 'Content-Type, Authorization',
            },
          ],
        },
        {
          source: '/cdn/media/:path*/',
          headers: [
            {
              key: 'Access-Control-Allow-Origin',
              value: '*',
            },
            {
              key: 'Access-Control-Allow-Methods',
              value: 'GET, OPTIONS',
            },
          ],
        },
      ];
    },

    output: 'export',
    trailingSlash: true,
  };

  return nextConfig;
};
