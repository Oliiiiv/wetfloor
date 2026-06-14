/** @type {import('next').NextConfig} */
const nextConfig = {
  // Required for the lightweight node-based Docker image we build with.
  output: "standalone",
  reactStrictMode: true,
};

export default nextConfig;
