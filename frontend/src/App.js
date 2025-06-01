import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [books, setBooks] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(1);
  const [verses, setVerses] = useState([]);
  const [currentLanguage, setCurrentLanguage] = useState("english");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [dailyVerse, setDailyVerse] = useState(null);
  const [showCrossRefs, setShowCrossRefs] = useState({});
  const [crossRefData, setCrossRefData] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("read");

  const languages = {
    english: { name: "English", dir: "ltr", class: "font-serif" },
    hindi: { name: "हिन्दी", dir: "ltr", class: "font-sans" },
    hebrew: { name: "עברית", dir: "rtl", class: "font-mono text-right" },
    greek: { name: "Ελληνικά", dir: "ltr", class: "font-serif" }
  };

  // Fetch books on component mount
  useEffect(() => {
    fetchBooks();
    fetchDailyVerse();
  }, []);

  const fetchBooks = async () => {
    try {
      const response = await axios.get(`${API}/books`);
      setBooks(response.data);
      if (response.data.length > 0) {
        setSelectedBook(response.data[0]);
      }
    } catch (error) {
      console.error("Error fetching books:", error);
    }
  };

  const fetchDailyVerse = async () => {
    try {
      const response = await axios.get(`${API}/daily-verse`);
      setDailyVerse(response.data);
    } catch (error) {
      console.error("Error fetching daily verse:", error);
    }
  };

  const fetchChapter = async (book, chapter) => {
    if (!book) return;
    setLoading(true);
    try {
      const response = await axios.get(`${API}/books/${book.name.english}/chapters/${chapter}`);
      setVerses(response.data);
    } catch (error) {
      console.error("Error fetching chapter:", error);
    } finally {
      setLoading(false);
    }
  };

  const searchVerses = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const response = await axios.get(`${API}/search`, {
        params: {
          q: searchQuery,
          language: currentLanguage,
          limit: 50
        }
      });
      console.log("Search response:", response.data); // Debug log
      setSearchResults(response.data.verses || []);
      setActiveTab("search");
    } catch (error) {
      console.error("Error searching verses:", error);
      setSearchResults([]); // Clear results on error
    } finally {
      setLoading(false);
    }
  };

  const fetchCrossReferences = async (verseId) => {
    try {
      const response = await axios.get(`${API}/cross-references/${verseId}`);
      setCrossRefData(prev => ({
        ...prev,
        [verseId]: response.data.cross_references
      }));
      setShowCrossRefs(prev => ({
        ...prev,
        [verseId]: !prev[verseId]
      }));
    } catch (error) {
      console.error("Error fetching cross references:", error);
    }
  };

  // Fetch chapter when book or chapter changes
  useEffect(() => {
    if (selectedBook && selectedChapter) {
      fetchChapter(selectedBook, selectedChapter);
    }
  }, [selectedBook, selectedChapter]);

  const VerseCard = ({ verse, showReference = true }) => {
    const langConfig = languages[currentLanguage];
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-4 border-l-4 border-blue-500">
        {showReference && (
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-bold text-gray-800">
              {verse.book} {verse.chapter}:{verse.verse}
            </h3>
            <button
              onClick={() => fetchCrossReferences(verse.id)}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Cross References {showCrossRefs[verse.id] ? "▼" : "▶"}
            </button>
          </div>
        )}
        
        <div className={`text-lg leading-relaxed mb-4 ${langConfig.class}`} dir={langConfig.dir}>
          {verse.text[currentLanguage] || verse.text.english}
        </div>

        {/* Transliteration for Hebrew/Greek */}
        {(currentLanguage === "hebrew" || currentLanguage === "greek") && verse.transliteration[currentLanguage] && (
          <div className="text-sm text-gray-600 italic mb-3 bg-gray-50 p-3 rounded">
            <strong>Transliteration:</strong> {verse.transliteration[currentLanguage]}
          </div>
        )}

        {/* Study Notes */}
        {verse.notes && (verse.notes.commentary || verse.notes.study_notes) && (
          <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            {verse.notes.commentary && (
              <div className="mb-2">
                <strong className="text-yellow-800">Commentary:</strong>
                <p className="text-sm text-yellow-700 mt-1">{verse.notes.commentary}</p>
              </div>
            )}
            {verse.notes.study_notes && (
              <div>
                <strong className="text-yellow-800">Study Notes:</strong>
                <p className="text-sm text-yellow-700 mt-1">{verse.notes.study_notes}</p>
              </div>
            )}
          </div>
        )}

        {/* Cross References */}
        {showCrossRefs[verse.id] && crossRefData[verse.id] && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <strong className="text-blue-800 block mb-3">Related Verses:</strong>
            <div className="space-y-3">
              {crossRefData[verse.id].map((refVerse, index) => (
                <div key={index} className="p-3 bg-white rounded border border-blue-100">
                  <div className="font-semibold text-sm text-blue-700 mb-1">
                    {refVerse.book} {refVerse.chapter}:{refVerse.verse}
                  </div>
                  <div className={`text-sm ${langConfig.class}`} dir={langConfig.dir}>
                    {refVerse.text[currentLanguage] || refVerse.text.english}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="text-3xl font-bold text-blue-800 flex items-center">
                <svg className="w-8 h-8 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                MultiLingual Bible
              </div>
            </div>
            
            {/* Language Selector */}
            <div className="flex items-center space-x-4">
              <select
                value={currentLanguage}
                onChange={(e) => setCurrentLanguage(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {Object.entries(languages).map(([code, lang]) => (
                  <option key={code} value={code}>{lang.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm mb-8">
          {[
            { id: "read", label: "Read Scripture", icon: "📖" },
            { id: "search", label: "Search", icon: "🔍" },
            { id: "daily", label: "Daily Verse", icon: "✨" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white shadow-lg"
                  : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Daily Verse Tab */}
        {activeTab === "daily" && dailyVerse && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Daily Verse</h2>
            <div className="max-w-3xl mx-auto">
              <VerseCard verse={dailyVerse} />
            </div>
          </div>
        )}

        {/* Search Tab */}
        {activeTab === "search" && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Search Scripture</h2>
            <div className="max-w-2xl mx-auto mb-8">
              <div className="flex gap-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for verses..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  onKeyPress={(e) => e.key === "Enter" && searchVerses()}
                />
                <button
                  onClick={searchVerses}
                  disabled={loading}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
                >
                  {loading ? "Searching..." : "Search"}
                </button>
              </div>
            </div>
            
            {searchResults.length > 0 && (
              <div className="max-w-4xl mx-auto">
                <p className="text-gray-600 mb-4">Found {searchResults.length} results</p>
                {searchResults.map((verse, index) => (
                  <VerseCard key={index} verse={verse} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Read Scripture Tab */}
        {activeTab === "read" && (
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Read Scripture</h2>
            
            {/* Book and Chapter Selection */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Book
                  </label>
                  <select
                    value={selectedBook?.id || ""}
                    onChange={(e) => {
                      const book = books.find(b => b.id === e.target.value);
                      setSelectedBook(book);
                      setSelectedChapter(1);
                    }}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {books.map(book => (
                      <option key={book.id} value={book.id}>
                        {book.name[currentLanguage] || book.name.english}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chapter
                  </label>
                  <select
                    value={selectedChapter}
                    onChange={(e) => setSelectedChapter(parseInt(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {selectedBook && Array.from({ length: selectedBook.chapters }, (_, i) => i + 1).map(chapter => (
                      <option key={chapter} value={chapter}>
                        Chapter {chapter}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Chapter Content */}
            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600">Loading chapter...</p>
              </div>
            ) : (
              <div className="max-w-4xl mx-auto">
                {verses.map((verse, index) => (
                  <VerseCard key={index} verse={verse} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
