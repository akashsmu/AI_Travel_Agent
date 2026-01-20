import React from 'react';
import { MapPin, Star } from 'lucide-react';

interface PlaceWidgetProps {
    data: {
        name: string;
        type?: string;
        rating?: number;
        reviews?: number;
        address?: string;
        thumbnail?: string;
    };
}

export const PlaceWidget: React.FC<PlaceWidgetProps> = ({ data }) => {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md p-4 flex gap-4 hover:bg-gray-50 transition-colors border border-gray-100 dark:border-gray-700">
            {data.thumbnail ? (
                <img
                    src={data.thumbnail}
                    alt={data.name}
                    className="w-24 h-24 rounded-xl object-cover flex-shrink-0"
                />
            ) : (
                <div className="w-24 h-24 rounded-xl bg-purple-100 flex items-center justify-center flex-shrink-0">
                    <MapPin className="text-purple-500" size={32} />
                </div>
            )}

            <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start">
                    <h4 className="font-bold text-gray-900 dark:text-gray-100 truncate pr-2 text-lg">
                        {data.name}
                    </h4>
                    {data.rating && (
                        <div className="flex items-center bg-yellow-100 px-2 py-1 rounded-lg">
                            <Star size={12} className="text-yellow-600 fill-yellow-600 mr-1" />
                            <span className="text-xs font-bold text-yellow-700">{data.rating}</span>
                        </div>
                    )}
                </div>

                {data.type && (
                    <span className="inline-block mt-1 px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full font-medium">
                        {data.type}
                    </span>
                )}

                {data.address && (
                    <p className="text-sm text-gray-500 mt-2 truncate">
                        {data.address}
                    </p>
                )}
            </div>
        </div>
    );
};
