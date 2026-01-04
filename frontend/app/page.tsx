'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plane, Hotel, Calendar, DollarSign, Users, Briefcase,
  Palmtree, Loader2, Sparkles, MapPin
} from 'lucide-react';
import axios from 'axios';
import { format } from 'date-fns';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    startDate: '',
    endDate: '',
    tripPurpose: 'vacation',
    travelParty: 'solo_male',
    bedrooms: 1,
    maxPrice: 200,
    minRating: 4.0,
    budget: 5000
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResults(null);

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
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Plane className="inline mr-2" size={18} />
                  From
                </label>
                <input
                  type="text"
                  value={formData.origin}
                  onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
                  placeholder="e.g., San Francisco, SFO"
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <MapPin className="inline mr-2" size={18} />
                  To
                </label>
                <input
                  type="text"
                  value={formData.destination}
                  onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                  placeholder="e.g., Paris, Tokyo"
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
                  required
                />
              </div>
            </div>

            {/* Date Row */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Calendar className="inline mr-2" size={18} />
                  Departure Date
                </label>
                <input
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Calendar className="inline mr-2" size={18} />
                  Return Date
                </label>
                <input
                  type="date"
                  value={formData.endDate}
                  onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
                  required
                />
              </div>
            </div>

            {/* Trip Type Row */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Briefcase className="inline mr-2" size={18} />
                  Trip Purpose
                </label>
                <select
                  value={formData.tripPurpose}
                  onChange={(e) => setFormData({ ...formData, tripPurpose: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
                >
                  <option value="vacation">🏝️ Vacation</option>
                  <option value="work">💼 Business Trip</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Users className="inline mr-2" size={18} />
                  Traveling As
                </label>
                <select
                  value={formData.travelParty}
                  onChange={(e) => setFormData({ ...formData, travelParty: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
                >
                  <option value="solo_male">👨 Solo Male</option>
                  <option value="solo_female">👩 Solo Female</option>
                  <option value="group">👥 Group/Family</option>
                </select>
              </div>
            </div>

            {/* Budget & Accommodation Row */}
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <DollarSign className="inline mr-2" size={18} />
                  Total Budget ($)
                </label>
                <input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: parseInt(e.target.value) })}
                  min="500"
                  step="100"
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Hotel className="inline mr-2" size={18} />
                  Max Price/Night ($)
                </label>
                <input
                  type="number"
                  value={formData.maxPrice}
                  onChange={(e) => setFormData({ ...formData, maxPrice: parseInt(e.target.value) })}
                  min="50"
                  step="10"
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Bedrooms
                </label>
                <input
                  type="number"
                  value={formData.bedrooms}
                  onChange={(e) => setFormData({ ...formData, bedrooms: parseInt(e.target.value) })}
                  min="1"
                  max="5"
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none"
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
                  Planning Your Perfect Trip...
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
                  <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center">
                    <Plane className="mr-3 text-purple-600" />
                    Flight Options
                  </h2>
                  <div className="space-y-4">
                    {results.flights.slice(0, 5).map((flight: any, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -50 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-6 border-2 border-indigo-100 hover:border-indigo-300 transition-all"
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="font-bold text-lg text-gray-800">{flight.airline}</h3>
                            <p className="text-gray-600">
                              {flight.origin} → {flight.destination}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-bold text-purple-600">
                              ${flight.price || 'N/A'}
                            </p>
                            {flight.url && (
                              <a
                                href={flight.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-purple-600 hover:text-purple-800"
                              >
                                Book Now →
                              </a>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
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
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
