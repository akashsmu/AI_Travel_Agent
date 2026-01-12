import React from 'react';
import { motion } from 'framer-motion';
import { MapPin, Star, MessageSquare, Newspaper, Camera } from 'lucide-react';

interface CommunitySectionProps {
  topSights: any[];
  localPlaces: any[];
  localNews: any[];
  discussions: any[];
}

export default function CommunitySection({ topSights, localPlaces, localNews, discussions }: CommunitySectionProps) {
  if (!topSights.length && !localPlaces.length && !localNews.length && !discussions.length) {
    return null;
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

      {/* Top Sights Carousel */}
      {topSights.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Camera className="text-pink-500" />
            <h2 className="text-xl font-bold text-gray-800">Top Sights & Attractions</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {topSights.slice(0, 3).map((sight, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100 hover:shadow-lg transition-all"
              >
                {sight.image && (
                  <div className="h-40 w-full overflow-hidden">
                    <img src={sight.image} alt={sight.title} className="w-full h-full object-cover hover:scale-110 transition-transform duration-500" />
                  </div>
                )}
                <div className="p-4">
                  <h3 className="font-bold text-gray-900">{sight.title}</h3>
                  <div className="flex items-center gap-1 text-yellow-500 text-sm my-1">
                    <Star size={14} fill="currentColor" />
                    <span>{sight.rating || "N/A"}</span>
                    <span className="text-gray-400">({sight.reviews || 0})</span>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2">{sight.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* Local Gems & News Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* Local Gems */}
        {localPlaces.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="text-indigo-500" />
              <h2 className="text-xl font-bold text-gray-800">Local Gems</h2>
            </div>
            <div className="space-y-3">
              {localPlaces.slice(0, 4).map((place, idx) => (
                <div key={idx} className="flex gap-4 bg-white p-3 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all">
                  {place.thumbnail && (
                    <img src={place.thumbnail} alt={place.title} className="w-20 h-20 rounded-lg object-cover" />
                  )}
                  <div>
                    <h4 className="font-bold text-gray-800">{place.title}</h4>
                    <p className="text-xs text-indigo-600 font-medium">{place.type}</p>
                    <div className="flex items-center gap-1 text-yellow-500 text-xs mt-1">
                      <Star size={12} fill="currentColor" />
                      <span>{place.rating}</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-1">{place.address}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* News & Discussions */}
        <div className="space-y-8">
          {localNews.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Newspaper className="text-blue-500" />
                <h2 className="text-xl font-bold text-gray-800">Local News</h2>
              </div>
              <div className="space-y-3">
                {localNews.slice(0, 3).map((news, idx) => (
                  <a key={idx} href={news.link} target="_blank" rel="noopener noreferrer" className="block group">
                    <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 hover:bg-blue-100 transition-colors">
                      <h4 className="font-semibold text-gray-900 group-hover:text-blue-700 line-clamp-1">{news.title}</h4>
                      <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                        <span>{news.source}</span>
                        <span>{news.date}</span>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            </section>
          )}

          {discussions.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="text-green-500" />
                <h2 className="text-xl font-bold text-gray-800">Community Chatter</h2>
              </div>
              <div className="space-y-3">
                {discussions.slice(0, 3).map((disc, idx) => (
                  <a key={idx} href={disc.link} target="_blank" rel="noopener noreferrer" className="block group">
                    <div className="bg-green-50 p-3 rounded-lg border border-green-100 hover:bg-green-100 transition-colors">
                      <h4 className="font-semibold text-gray-900 group-hover:text-green-700 line-clamp-1">{disc.title}</h4>
                      <p className="text-xs text-gray-600 mt-1 line-clamp-2">{disc.snippet}</p>
                      <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                        <span>{disc.source}</span>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            </section>
          )}
        </div>

      </div>
    </div>
  );
}
