import React from 'react';
import { PlayCircle } from 'lucide-react';

interface VideoWidgetProps {
    data: {
        title: string;
        link: string;
        thumbnail: string;
        channel?: string;
        views?: string;
    };
}

export const VideoWidget: React.FC<VideoWidgetProps> = ({ data }) => {
    return (
        <a
            href={data.link}
            target="_blank"
            rel="noopener noreferrer"
            className="block group relative rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1"
        >
            <div className="aspect-video relative">
                <img
                    src={data.thumbnail}
                    alt={data.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                    <div className="bg-white/90 rounded-full p-4 shadow-lg backdrop-blur-sm group-hover:scale-110 transition-transform">
                        <PlayCircle size={32} className="text-red-600 ml-1" />
                    </div>
                </div>
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                    <h3 className="text-white font-bold text-lg line-clamp-2">{data.title}</h3>
                    <div className="flex gap-2 text-white/80 text-sm mt-1">
                        {data.channel && <span>{data.channel}</span>}
                        {data.views && <span>• {data.views}</span>}
                    </div>
                </div>
            </div>
        </a>
    );
};
