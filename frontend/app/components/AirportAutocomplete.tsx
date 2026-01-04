import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Loader2 } from 'lucide-react';

interface Suggestion {
    id: string;
    name: string;
    code: string;
}

interface Props {
    label: string;
    value: string; // The display value (what shows in input)
    onChange: (value: string) => void; // Updates display value
    onSelect?: (suggestion: Suggestion) => void; // Optional: returns full object
    placeholder?: string;
    icon?: any;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AirportAutocomplete({ label, value, onChange, onSelect, placeholder, icon: Icon }: Props) {
    const [query, setQuery] = useState(value);
    const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const wrapperRef = useRef<HTMLDivElement>(null);
    const isSelectedRef = useRef(false);

    useEffect(() => {
        setQuery(value);
    }, [value]);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
        const fetchSuggestions = async () => {
            // Don't search if we just selected an item
            if (isSelectedRef.current) {
                isSelectedRef.current = false;
                return;
            }

            if (!query || query.length < 2) {
                setSuggestions([]);
                return;
            }

            setIsLoading(true);
            try {
                const res = await axios.get(`${API_URL}/autocomplete`, { params: { query } });
                // console.log("Autocomplete Results:", res.data); // Debuging
                setSuggestions(res.data);
                if (res.data.length > 0) {
                    setIsOpen(true);
                } else {
                    setIsOpen(false);
                }
            } catch (error) {
                console.error("Autocomplete error", error);
            } finally {
                setIsLoading(false);
            }
        };

        const timeoutId = setTimeout(fetchSuggestions, 500);
        return () => clearTimeout(timeoutId);
    }, [query]);

    const handleSelect = (suggestion: Suggestion) => {
        // PREFER NAME for display in the Input box
        const displayVal = suggestion.name;

        // Callback with full details (so parent can store ID)
        if (onSelect) {
            onSelect(suggestion);
        }

        // Set flag to prevent immediate re-search
        isSelectedRef.current = true;

        onChange(displayVal);
        setQuery(displayVal);
        setIsOpen(false);
    };

    return (
        <div className="relative" ref={wrapperRef}>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
                {Icon && <Icon className="inline mr-2" size={18} />}
                {label}
            </label>
            <div className="relative">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => {
                        setQuery(e.target.value);
                        onChange(e.target.value);
                        isSelectedRef.current = false;
                        if (e.target.value.length >= 2) setIsOpen(true);
                    }}
                    onFocus={() => {
                        if (suggestions.length > 0) setIsOpen(true);
                    }}
                    placeholder={placeholder}
                    className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all outline-none text-gray-800 bg-white"
                    required
                />
                {isLoading && (
                    <div className="absolute right-3 top-3.5">
                        <Loader2 className="animate-spin text-gray-400" size={20} />
                    </div>
                )}
            </div>

            {isOpen && suggestions.length > 0 && (
                <ul className="absolute z-50 w-full mt-1 bg-white border border-gray-100 rounded-xl shadow-xl max-h-60 overflow-auto">
                    {suggestions.map((s, idx) => (
                        <li
                            key={idx}
                            onClick={() => handleSelect(s)}
                            className="px-4 py-3 hover:bg-purple-50 cursor-pointer flex justify-between items-center text-gray-700 border-b border-gray-50 last:border-0"
                        >
                            <div className="flex flex-col">
                                <span className="font-medium">{s.name}</span>
                                <span className="text-xs text-gray-400">{s.id}</span>
                            </div>
                            <span className="text-sm font-bold text-purple-600 bg-purple-50 px-2 py-1 rounded">{s.code}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
