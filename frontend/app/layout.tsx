import type { Metadata } from 'next';
import { Inter, Outfit } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit' });

export const metadata: Metadata = {
  title: 'AI Travel Agent - Your Intelligent Journey Companion',
  description: 'Plan your perfect trip with AI-powered itineraries, real-time flight and hotel searches, and personalized recommendations.',
};

export default function RootLayout({
  children,
}: {
  children: React.Node;
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${outfit.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
