'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plane, Hotel, Calendar, DollarSign, Users, Briefcase,
  Palmtree, Loader2, Sparkles, MapPin
} from 'lucide-react';
import axios from 'axios';
import { format } from 'date-fns';
import AirportAutocomplete from './components/AirportAutocomplete';
import FlightCard from './components/FlightCard';
import WeatherWidget from './components/WeatherWidget';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function HomePage() {
  // Separate state for display values (Names) vs submitted values (IDs)
  const [displayOrigin, setDisplayOrigin] = useState('');
  const [displayDestination, setDisplayDestination] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    startDate: '',
    endDate: '',
    tripPurpose: 'vacation',
    travelParty: 'solo', // 'solo' or 'group'
    travelerAge: null as number | null,
    groupAgeMin: null as number | null,
    groupAgeMax: null as number | null,
    transportationMode: 'public',
    bedrooms: 1,
    maxPrice: 200,
    minRating: 4.0,
    budget: 5000
  });

  const [logs, setLogs] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResults(null);
    setLogs([]);

    // 1. Start WebSocket connection for real-time logs
    const ws = new WebSocket(`${API_URL.replace('http', 'ws')}/ws/chat`);

    ws.onopen = () => {
      console.log('Connected to WebSocket');
      // Send initial data to start the graph (if your backend supports receiving it via WS)
      // Note: Current backend implementation might expect HTTP POST to start, 
      // but let's assume we want to just listen or if we modify backend to accept start via WS.
      // Based on server.py, /ws/chat accepts text and runs the graph.

      // Use IDs if available, else fallback to whatever user typed (display value)
      ws.send(JSON.stringify({
        origin: displayOrigin, // Send Name for Weather/Hotels/LLM
        destination: displayDestination, // Send Name 
        origin_id: formData.origin, // Send ID for Flights
        destination_id: formData.destination, // Send ID for Flights
        start_date: formData.startDate,
        end_date: formData.endDate,
        trip_purpose: formData.tripPurpose,
        travel_party: formData.travelParty,
        traveler_age: formData.travelerAge ? parseInt(formData.travelerAge as any) : null,
        group_age_min: formData.groupAgeMin ? parseInt(formData.groupAgeMin as any) : null,
        group_age_max: formData.groupAgeMax ? parseInt(formData.groupAgeMax as any) : null,
        transportation_mode: formData.transportationMode,
        budget: formData.budget ? parseFloat(formData.budget as any) : null,
        bedrooms: formData.bedrooms,
        max_price: formData.maxPrice,
        min_rating: formData.minRating
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'update') {
        // It's a log/step update
        setLogs(prev => [...prev, `Checking ${data.step}...`]);
      } else if (data.type === 'complete' || data.itinerary) {
        // It's the final result (server.py might need tweaks to send this structure exactly, 
        // but let's assume standard graph output)
        if (data.data) {
          setResults(data.data); // If wrapped
        } else {
          setResults(data); // If direct state
        }
        ws.close();
        setIsLoading(false);
      } else if (data.type === 'error') {
        console.error("WS Error:", data);
        alert("Error during planning");
        ws.close();
        setIsLoading(false);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
      // Fallback to HTTP if WS fails
      fallbackHttpPlan();
    };
  };

  const fallbackHttpPlan = async () => {
    try {
      const response = await axios.post(`${API_URL}/plan`, {
        origin: formData.origin,
        destination: formData.destination,
        start_date: formData.startDate,
        end_date: formData.endDate,
        trip_purpose: formData.tripPurpose,
        travel_party: formData.travelParty,
        bedrooms: formData.bedrooms,
        max_price: formData.maxPrice,
        min_rating: formData.minRating,
        budget: formData.budget
      });
      setResults(response.data);
    } catch (error) {
      console.error('Planning failed:', error);
      alert('Failed to plan trip. Make sure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative z-10 container mx-auto px-4 py-16">
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="text-6xl md:text-7xl font-extrabold text-white mb-4 tracking-tight">
              <Sparkles className="inline-block mr-3 mb-2" size={60} />
              AI Travel Agent
            </h1>
            <p className="text-xl md:text-2xl text-white/90 max-w-2xl mx-auto">
              Your intelligent companion for crafting unforgettable journeys
            </p>
          </motion.div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        {/* Planning Form */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl p-8 mb-8"
        >
          <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center">
            <MapPin className="mr-3 text-purple-600" />
            Plan Your Journey
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Destination Row */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <AirportAutocomplete
                  label="From"
                  value={displayOrigin}
                  onChange={(val) => {
                    setDisplayOrigin(val);
                    setFormData({ ...formData, origin: '' }); // Clear ID on manual type until selected
                  }}
                  onSelect={(suggestion) => {
                    setDisplayOrigin(suggestion.name);
                    setFormData({ ...formData, origin: suggestion.id }); // Store ID (e.g. SFO or /m/...)
                  }}
                  placeholder="e.g., San Francisco, SFO"
                  icon={Plane}
                />
              </div>

              <div>
                <AirportAutocomplete
                  label="To"
                  value={displayDestination}
                  onChange={(val) => {
                    setDisplayDestination(val);
                    setFormData({ ...formData, destination: '' });
                  }}
                  onSelect={(suggestion) => {
                    setDisplayDestination(suggestion.name);
                    setFormData({ ...formData, destination: suggestion.id });
                  }}
                  placeholder="e.g., Paris, Tokyo"
                  icon={MapPin}
                />
              </div>
            </div>

            {/* Date Row */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  <Calendar className="inline mr-2" size={18} />
                  Departure Date
                </label>
                <input
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  <Calendar className="inline mr-2" size={18} />
                  Return Date
                </label>
                <input
                  type="date"
                  value={formData.endDate}
                  onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                  required
                />
              </div>
            </div>

            {/* Trip Type Row */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  <Briefcase className="inline mr-2" size={18} />
                  Trip Purpose
                </label>
                <select
                  value={formData.tripPurpose}
                  onChange={(e) => setFormData({ ...formData, tripPurpose: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                >
                  <option value="vacation">🏝️ Vacation</option>
                  <option value="work">💼 Business Trip</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  <Users className="inline mr-2" size={18} />
                  Traveling As
                </label>
                <select
                  value={formData.travelParty}
                  onChange={(e) => setFormData({ ...formData, travelParty: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                >
                  <option value="solo">👤 Solo Traveler</option>
                  <option value="group">👥 Group/Family</option>
                </select>
              </div>
            </div>

            {/* Conditional Age & Transportation Row */}
            <div className="grid md:grid-cols-2 gap-6">
              {formData.travelParty === 'solo' ? (
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-2">
                    Your Age
                  </label>
                  <input
                    type="number"
                    placeholder="Your Age"
                    value={formData.travelerAge || ''}
                    onChange={(e) => setFormData({ ...formData, travelerAge: parseInt(e.target.value) })}
                    className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white placeholder-gray-400"
                  />
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-900 mb-2">Min Age</label>
                    <input
                      type="number"
                      placeholder="Min"
                      value={formData.groupAgeMin || ''}
                      onChange={(e) => setFormData({ ...formData, groupAgeMin: parseInt(e.target.value) })}
                      className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white placeholder-gray-400"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-900 mb-2">Max Age</label>
                    <input
                      type="number"
                      placeholder="Max"
                      value={formData.groupAgeMax || ''}
                      onChange={(e) => setFormData({ ...formData, groupAgeMax: parseInt(e.target.value) })}
                      className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white placeholder-gray-400"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Transportation Mode
                </label>
                <select
                  value={formData.transportationMode}
                  onChange={(e) => setFormData({ ...formData, transportationMode: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                >
                  <option value="public">🚍 Public Transit</option>
                  <option value="car">🚗 Rental/Own Car</option>
                  <option value="walking">🚶 Walking/Biking</option>
                </select>
              </div>
            </div>

            {/* Budget & Accommodation Row */}
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  <DollarSign className="inline mr-2" size={18} />
                  Total Budget ($)
                </label>
                <input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: parseInt(e.target.value) })}
                  min="500"
                  step="100"
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  <Hotel className="inline mr-2" size={18} />
                  Max Price/Night ($)
                </label>
                <input
                  type="number"
                  value={formData.maxPrice}
                  onChange={(e) => setFormData({ ...formData, maxPrice: parseInt(e.target.value) })}
                  min="50"
                  step="10"
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Bedrooms
                </label>
                <input
                  type="number"
                  value={formData.bedrooms}
                  onChange={(e) => setFormData({ ...formData, bedrooms: parseInt(e.target.value) })}
                  min="1"
                  max="5"
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                />
              </div>
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 animate-spin" />
                  {logs.length > 0 ? logs[logs.length - 1] : "Planning Your Perfect Trip..."}
                </>
              ) : (
                <>
                  <Sparkles className="mr-2" />
                  Generate My Itinerary
                </>
              )}
            </motion.button>
          </form>
        </motion.div>

        {/* Results Section */}
        <AnimatePresence>
          {results && (
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              {/* Weather Widget */}
              {results.weather_info ? (
                <WeatherWidget weatherInfo={results.weather_info} />
              ) : results.weather_summary ? (
                <div className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl p-8 mb-8 transform hover:scale-[1.01] transition-transform">
                  <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center">
                    <span className="mr-3 text-4xl">🌤️</span>
                    Local Weather
                  </h2>
                  <div className="bg-gradient-to-r from-blue-100 to-cyan-100 rounded-2xl p-6 border-l-8 border-blue-400">
                    <p className="text-xl text-blue-900 font-medium leading-relaxed">
                      {results.weather_summary}
                    </p>
                  </div>
                </div>
              ) : null}

              {/* Hotels */}
              {results.accommodations && results.accommodations.length > 0 && (
                <div className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl p-8">
                  <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center">
                    <Hotel className="mr-3 text-purple-600" />
                    Recommended Hotels
                  </h2>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {results.accommodations.slice(0, 6).map((hotel: any, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border-2 border-purple-100 hover:border-purple-300 transition-all"
                      >
                        <h3 className="font-bold text-lg text-gray-800 mb-2">{hotel.name}</h3>
                        <div className="space-y-1 text-sm text-gray-600">
                          <p>⭐ Rating: {hotel.rating || 'N/A'}</p>
                          <p>💰 ${hotel.price || hotel.price_per_night}/night</p>
                          <p>📍 {hotel.city}</p>
                        </div>
                        {hotel.url && (
                          <a
                            href={hotel.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-4 inline-block text-purple-600 hover:text-purple-800 font-semibold"
                          >
                            View Details →
                          </a>
                        )}
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}

              {/* Flights */}
              {results.flights && results.flights.length > 0 && (
                <div className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl p-8">
                  <h2 className="text-3xl font-bold text-gray-800 mb-8 flex items-center">
                    <Plane className="mr-3 text-purple-600" />
                    Flight Options
                  </h2>

                  {/* Best Flights Section */}
                  <div className="mb-10">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                      <Sparkles className="text-yellow-500 mr-2" size={20} />
                      Best Value Flights
                    </h3>
                    <div className="space-y-6">
                      {results.flights.filter((f: any) => f.type === 'Best').map((flight: any, idx: number) => (
                        <FlightCard key={`best-${idx}`} flight={flight} idx={idx} isBest={true} />
                      ))}
                    </div>
                  </div>

                  {/* Other Flights Section */}
                  {results.flights.some((f: any) => f.type === 'Other') && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-700 mb-4 ml-1">Other Options</h3>
                      <div className="space-y-4">
                        {results.flights.filter((f: any) => f.type === 'Other').map((flight: any, idx: number) => (
                          <FlightCard key={`other-${idx}`} flight={flight} idx={idx} isBest={false} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Fallback if no type defined (backward compatibility) */}
                  {!results.flights.some((f: any) => f.type) && (
                    <div className="space-y-4">
                      {results.flights.map((flight: any, idx: number) => (
                        <FlightCard key={`flight-${idx}`} flight={flight} idx={idx} isBest={idx < 1} />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Itinerary */}
              {results.itinerary && (
                <div className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl p-8">
                  <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center">
                    <Palmtree className="mr-3 text-purple-600" />
                    Your Personalized Itinerary
                  </h2>
                  <div className="prose prose-lg max-w-none">
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border-2 border-green-200 whitespace-pre-wrap text-gray-700 leading-relaxed">
                      {results.itinerary}
                    </div>
                  </div>
                </div>
              )
              }
            </motion.div >
          )}
        </AnimatePresence >
      </div >
    </div >
  );
}
