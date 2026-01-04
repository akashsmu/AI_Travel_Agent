import { motion } from 'framer-motion';
import { Cloud, Sun, CloudRain, CloudSnow, Wind, Droplets } from 'lucide-react';

export default function WeatherWidget({ weatherInfo }: { weatherInfo: any }) {
    if (!weatherInfo || !weatherInfo.forecast) return null;

    const getWeatherIcon = (condition: string) => {
        const c = condition.toLowerCase();
        if (c.includes('rain')) return <CloudRain className="text-blue-400" size={24} />;
        if (c.includes('cloud')) return <Cloud className="text-gray-400" size={24} />;
        if (c.includes('snow')) return <CloudSnow className="text-cyan-200" size={24} />;
        if (c.includes('clear') || c.includes('sun')) return <Sun className="text-yellow-400" size={24} />;
        return <Sun className="text-yellow-400" size={24} />;
    };

    return (
        <div className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl p-8 mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="mr-3 text-4xl">🌤️</span>
                Forecast for {weatherInfo.location}
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {weatherInfo.forecast.slice(0, 5).map((day: any, idx: number) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bg-gradient-to-b from-blue-50 to-white border border-blue-100 rounded-xl p-4 flex flex-col items-center text-center hover:shadow-lg transition-all"
                    >
                        <span className="text-sm font-bold text-gray-500 mb-2">{day.day}</span>
                        <div className="mb-3 p-3 bg-white rounded-full shadow-sm">
                            {getWeatherIcon(day.condition)}
                        </div>
                        <span className="text-gray-700 font-medium text-sm mb-1">{day.condition}</span>
                        <div className="flex items-center gap-2 mt-auto">
                            <span className="text-lg font-bold text-gray-800">{day.max_temp}°</span>
                            <span className="text-sm text-gray-400">{day.min_temp}°</span>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
