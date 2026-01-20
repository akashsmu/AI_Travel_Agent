import React from 'react';
import { Newspaper, ExternalLink } from 'lucide-react';

interface NewsWidgetProps {
  data: {
    title: string;
    snippet: string;
    link: string;
    source: string;
    date?: string;
    thumbnail?: string;
  };
}

export const NewsWidget: React.FC<NewsWidgetProps> = ({ data }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md overflow-hidden hover:shadow-lg transition-shadow border border-gray-100 dark:border-gray-700">
      <div className="flex flex-col md:flex-row">
        {data.thumbnail && (
          <div className="md:w-1/3 h-48 md:h-auto relative">
            <img 
              src={data.thumbnail} 
              alt={data.title} 
              className="w-full h-full object-cover"
            />
          </div>
        )}
        <div className="p-6 flex-1 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm text-blue-600 font-semibold mb-2">
              <Newspaper size={16} />
              <span>{data.source}</span>
              {data.date && <span className="text-gray-400">• {data.date}</span>}
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3 leading-tight">
              {data.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4 line-clamp-3">
              {data.snippet}
            </p>
          </div>
          <a
            href={data.link}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center text-purple-600 hover:text-purple-700 font-semibold transition-colors"
          >
            Read Source <ExternalLink size={16} className="ml-1" />
          </a>
        </div>
      </div>
    </div>
  );
};
