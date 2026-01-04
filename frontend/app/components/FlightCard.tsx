import { motion } from 'framer-motion';
import { Plane, Clock, Calendar, CheckCircle2 } from 'lucide-react';

export default function FlightCard({ flight, idx, isBest }: { flight: any, idx: number, isBest: boolean }) {
    // Compute some display values
    const stops = flight.layovers?.length || 0;
    const stopText = stops === 0 ? "Nonstop" : `${stops} Stop${stops > 1 ? 's' : ''}`;
    const duration = flight.duration || "N/A";

    // Safely get extensions
    const amenities = flight.extensions || [];

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`relative group rounded-2xl border-2 transition-all overflow-hidden ${isBest
                    ? 'bg-gradient-to-br from-white to-amber-50 border-amber-200 shadow-xl hover:shadow-2xl hover:border-amber-300'
                    : 'bg-white border-gray-100 hover:border-purple-200 shadow-sm hover:shadow-md'
                }`}
        >
            {isBest && (
                <div className="absolute top-0 right-0 bg-amber-400 text-white text-xs font-bold px-3 py-1 rounded-bl-xl shadow-sm z-10">
                    BEST VALUE
                </div>
            )}

            <div className="p-6 flex flex-col md:flex-row gap-6 items-center">
                {/* Left: Airline Logo & Info */}
                <div className="flex flex-col items-center md:items-start min-w-[120px]">
                    {flight.airline_logo ? (
                        <img src={flight.airline_logo} alt={flight.airline} className="h-10 w-auto object-contain mb-2" />
                    ) : (
                        <div className="h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center mb-2">
                            <Plane className="text-gray-400" size={20} />
                        </div>
                    )}
                    <span className="font-bold text-gray-800 text-center md:text-left">{flight.airline}</span>
                    <span className="text-xs text-gray-400 font-mono mt-1">{flight.flight_number}</span>
                </div>

                {/* Center: Flight Timeline */}
                <div className="flex-1 w-full md:w-auto flex flex-col items-center justify-center px-4">
                    <div className="w-full flex justify-between text-sm font-semibold text-gray-600 mb-2">
                        <span>{flight.origin}</span>
                        <span>{flight.destination}</span>
                    </div>

                    <div className="relative w-full flex items-center">
                        <div className="h-[2px] bg-gray-200 w-full absolute"></div>
                        {/* Start Dot */}
                        <div className="w-3 h-3 rounded-full bg-purple-600 z-10"></div>

                        {/* Duration Label */}
                        <div className="bg-white px-2 py-0.5 rounded-full border border-gray-200 text-xs font-mono text-gray-500 z-10 mx-auto flex items-center">
                            <Clock size={12} className="mr-1" />
                            {duration}
                        </div>

                        {/* Stops Dots */}
                        {stops > 0 && (
                            <div className="absolute left-1/2 xs:hidden md:block transform -translate-x-1/2 -top-2">
                                <div className="w-2 h-2 rounded-full bg-orange-400 mx-auto mb-1"></div>
                            </div>
                        )}

                        {/* End Plane */}
                        <div className="z-10 bg-white p-1 rounded-full border border-purple-100">
                            <Plane className="text-purple-600 transform rotate-90" size={16} />
                        </div>
                    </div>

                    <div className="w-full flex justify-between text-xs text-gray-400 mt-2">
                        <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-md font-medium">
                            {stopText}
                        </span>
                        {flight.airplane && <span>{flight.airplane}</span>}
                    </div>
                </div>

                {/* Right: Price & Action */}
                <div className="flex flex-col items-center md:items-end min-w-[140px] pl-4 md:border-l border-gray-100">
                    <div className="text-2xl font-bold text-purple-600 mb-1">
                        ${flight.price}
                    </div>
                    <div className="text-xs text-gray-400 mb-3">{flight.travel_class || "Economy"}</div>

                    {flight.url && (
                        <a
                            href={flight.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${isBest
                                    ? 'bg-amber-400 text-white hover:bg-amber-500 shadow-lg hover:shadow-xl shadow-amber-200'
                                    : 'bg-purple-600 text-white hover:bg-purple-700 shadow-md hover:shadow-lg shadow-purple-200'
                                }`}
                        >
                            Select
                        </a>
                    )}
                </div>
            </div>

            {/* Footer: Amenities */}
            {amenities.length > 0 && (
                <div className="bg-gray-50 px-6 py-2 border-t border-gray-100 flex flex-wrap gap-3">
                    {amenities.map((item: string, i: number) => (
                        <div key={i} className="flex items-center text-xs text-gray-500">
                            <CheckCircle2 size={12} className="text-purple-400 mr-1" />
                            {item}
                        </div>
                    ))}
                </div>
            )}
        </motion.div>
    );
}
