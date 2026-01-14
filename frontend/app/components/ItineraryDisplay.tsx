import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Palmtree } from 'lucide-react';

interface ItineraryDisplayProps {
    itinerary: string;
}

export default function ItineraryDisplay({ itinerary }: ItineraryDisplayProps) {
    if (!itinerary) return null;

    return (
        <div className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl p-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center">
                <Palmtree className="mr-3 text-purple-600" />
                Your Personalized Itinerary
            </h2>

            <div className="prose prose-lg prose-purple max-w-none text-gray-700">
                <ReactMarkdown
                    components={{
                        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-4" {...props} />,
                        h2: ({ node, ...props }) => <h2 className="text-xl font-bold text-gray-800 mt-5 mb-3 border-b border-gray-100 pb-2" {...props} />,
                        h3: ({ node, ...props }) => <h3 className="text-lg font-semibold text-purple-700 mt-4 mb-2" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc list-outside space-y-1 ml-4" {...props} />,
                        li: ({ node, ...props }) => <li className="text-gray-700 leading-relaxed" {...props} />,
                        strong: ({ node, ...props }) => <strong className="font-semibold text-gray-900" {...props} />,
                        p: ({ node, ...props }) => <p className="mb-4 leading-relaxed" {...props} />,
                    }}
                >
                    {itinerary}
                </ReactMarkdown>
            </div>
        </div>
    );
}
