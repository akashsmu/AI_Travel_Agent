import { motion } from 'framer-motion';
import { Plane, Clock, MapPin, Leaf, Users } from 'lucide-react';

export default function FlightCard({ flight, idx, isBest }: { flight: any, idx: number, isBest: boolean }) {
    // Compute some display values
    const stops = flight.layovers?.length || 0;
    const stopText = stops === 0 ? "Nonstop" : `${stops} Stop${stops > 1 ? 's' : ''}`;
    const duration = flight.duration || "N/A";

    // Extract times
    const depTime = flight.departure_time || "";
    const arrTime = flight.arrival_time || "";

    // Extract airport names (fallback to codes if not available)
    const originName = flight.origin_name || flight.origin;
    const destName = flight.destination_name || flight.destination;

    // Safely get extensions
    const amenities = flight.extensions || [];

    // Carbon emissions (if available)
    const carbonData = flight.carbon_emissions;
    const carbonGrams = carbonData?.this_flight;
    const carbonDiff = carbonData?.difference_percent;

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`relative group rounded-2xl border-2 transition-all overflow-hidden ${isBest
                ? 'bg-gradient-to-br from-white to-amber-50 border-amber-300 shadow-xl hover:shadow-2xl hover:border-amber-400'
                : 'bg-white border-gray-200 hover:border-purple-300 shadow-md hover:shadow-lg'
                }`}
        >
            {isBest && (
                <div className="absolute top-0 right-0 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-bold px-4 py-1.5 rounded-bl-xl shadow-md z-10 flex items-center gap-1">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    BEST VALUE
                </div>
            )}

            <div className="p-6">
                {/* Header: Airline Info */}
                <div className="flex items-center justify-between mb-5 pb-4 border-b border-gray-100">
                    <div className="flex items-center gap-3">
                        {flight.airline_logo ? (
                            <img
                                src={flight.airline_logo}
                                alt={flight.airline}
                                className="h-8 w-auto object-contain"
                            />
                        ) : (
                            <div className="h-8 w-8 bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg flex items-center justify-center">
                                <Plane className="text-purple-600" size={16} />
                            </div>
                        )}
                        <div>
                            <div className="font-bold text-gray-800">{flight.airline}</div>
                            <div className="text-xs text-gray-500 font-mono">{flight.flight_number}</div>
                        </div>
                    </div>

                    <div className="text-right">
                        <div className="text-3xl font-bold text-purple-600">
                            ${flight.price}
                        </div>
                        <div className="text-xs text-gray-500 mt-0.5">
                            {flight.travel_class || "Economy"}
                        </div>
                    </div>
                </div>

                {/* Flight Timeline */}
                <div className="mb-4">
                    {/* Times and Cities - Restructured */}
                    <div className="flex justify-between items-start mb-3">
                        {/* Origin */}
                        <div className="flex-1">
                            <div className="text-sm font-semibold text-gray-700">{flight.origin}</div>
                            <div className="text-xs text-gray-500 mt-0.5 max-w-[150px] truncate" title={originName}>
                                {originName}
                            </div>
                            <div className="text-2xl font-bold text-gray-900 mt-2">{depTime}</div>
                        </div>

                        {/* Timeline Visual - Adjusted */}
                        <div className="flex-1 flex flex-col items-center px-4">
                            {/* Visual Timeline */}
                            <div className="w-full relative flex items-center mb-2">
                                <div className="absolute w-full h-[2px] bg-gradient-to-r from-purple-300 via-purple-200 to-purple-300"></div>

                                {/* Origin dot */}
                                <div className="w-2.5 h-2.5 rounded-full bg-purple-600 border-2 border-white shadow-sm z-10"></div>

                                {/* Layover indicators - repositioned below */}
                                {stops > 0 && (
                                    <div className="absolute left-1/2 transform -translate-x-1/2 flex flex-col items-center top-3">
                                        <div className="w-2 h-2 rounded-full bg-orange-400 border border-white shadow-sm"></div>
                                        <div className="text-[10px] text-orange-600 font-bold mt-1 whitespace-nowrap">
                                            {stopText}
                                        </div>
                                    </div>
                                )}

                                {/* Plane icon */}
                                <div className="ml-auto bg-white p-1 rounded-full border-2 border-purple-300 shadow-sm z-10">
                                    <Plane className="text-purple-600 transform rotate-90" size={12} />
                                </div>
                            </div>

                            {/* Duration - moved below timeline */}
                            <div className="text-xs text-gray-500 font-medium flex items-center gap-1 mt-1">
                                <Clock size={12} />
                                {duration}
                            </div>
                        </div>

                        {/* Destination */}
                        <div className="flex-1 text-right">
                            <div className="text-sm font-semibold text-gray-700">{flight.destination}</div>
                            <div className="text-xs text-gray-500 mt-0.5 max-w-[150px] ml-auto truncate" title={destName}>
                                {destName}
                            </div>
                            <div className="text-2xl font-bold text-gray-900 mt-2">{arrTime}</div>
                        </div>
                    </div>

                    {/* Additional Details Row */}
                    <div className="flex flex-wrap items-center gap-3 mt-4 pt-3 border-t border-gray-50">
                        {flight.airplane && (
                            <div className="flex items-center gap-1.5 text-xs text-gray-600 bg-gray-50 px-3 py-1.5 rounded-full">
                                <Plane size={12} className="text-gray-400" />
                                {flight.airplane}
                            </div>
                        )}

                        {carbonGrams && (
                            <div className="flex items-center gap-1.5 text-xs bg-green-50 text-green-700 px-3 py-1.5 rounded-full">
                                <Leaf size={12} className="text-green-600" />
                                {carbonGrams}g CO₂
                                {carbonDiff && (
                                    <span className="text-[10px]">
                                        ({carbonDiff > 0 ? '+' : ''}{carbonDiff}%)
                                    </span>
                                )}
                            </div>
                        )}

                        <div className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full ${stops === 0
                            ? 'bg-green-100 text-green-700'
                            : 'bg-orange-100 text-orange-700'
                            }`}>
                            {stopText}
                        </div>
                    </div>
                </div>

                {/* Layover Details */}
                {flight.layovers && flight.layovers.length > 0 && (
                    <div className="mb-4 p-3 bg-orange-50 border border-orange-100 rounded-lg">
                        <div className="text-xs font-semibold text-orange-900 mb-2">Layovers:</div>
                        <div className="space-y-1">
                            {flight.layovers.map((layover: any, i: number) => (
                                <div key={i} className="flex items-center gap-2 text-xs text-orange-800">
                                    <MapPin size={10} className="text-orange-500" />
                                    <span className="font-mono font-semibold">{layover.id}</span>
                                    {layover.duration && (
                                        <span className="text-orange-600">• {layover.duration}</span>
                                    )}
                                    {layover.name && (
                                        <span className="text-orange-600 truncate">• {layover.name}</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Amenities - Fixed condition */}
                {amenities && amenities.length > 0 && (
                    <div className="mb-4">
                        <div className="text-xs font-semibold text-gray-700 mb-2">Amenities:</div>
                        <div className="flex flex-wrap gap-2">
                            {amenities.slice(0, 8).map((item: string, i: number) => (
                                <div
                                    key={i}
                                    className="text-xs text-purple-700 bg-purple-50 px-2.5 py-1 rounded-md border border-purple-100"
                                >
                                    {item}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* CTA Button */}
                {flight.url && (
                    <a
                        href={flight.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`block w-full text-center px-6 py-3 rounded-xl text-sm font-bold transition-all transform hover:scale-[1.02] active:scale-[0.98] ${isBest
                            ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 shadow-lg hover:shadow-xl shadow-amber-200'
                            : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 shadow-md hover:shadow-lg shadow-purple-200'
                            }`}
                    >
                        Select Flight →
                    </a>
                )}
            </div>
        </motion.div>
    );
}
