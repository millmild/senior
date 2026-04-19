import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  // ======================
  // 🔍 SEARCH
  // ======================
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const controllerRef = useRef(null); // 🔥 ใช้ cancel request

  const handleSearch = async () => {
    if (!query.trim()) return;

    // 🔥 ยกเลิก request เก่า
    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        signal: controller.signal, // 🔥 สำคัญมาก
        body: JSON.stringify({
          query,
          year: null,
          advisor: null,
        }),
      });

      const data = await res.json();

      setResults(data.slice(0, 10));
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Search error:", err);
      }
    }

    setLoading(false);
  };

  
  // ======================
  // 🎨 UI
  // ======================
  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">📊 Dashboard</h1>

      {/* ================= SEARCH ================= */}
      <div className="bg-white p-4 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-3">🔎 Search Projects</h2>

        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !loading) handleSearch();
            }}
            placeholder="Search เช่น IoT, AI..."
            className="flex-1 border px-4 py-2 rounded-lg"
          />

          <button
            onClick={handleSearch}
            disabled={loading} // 🔥 กันกดซ้ำ
            className="bg-blue-500 text-white px-4 py-2 rounded-lg disabled:bg-gray-400"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* loading */}
        {loading && (
          <p className="mt-3 text-gray-500 animate-pulse">
            🔍 Searching...
          </p>
        )}

        {/* results */}
        <div className="mt-4">
          {!loading && results.length === 0 && (
            <p className="text-gray-400">No results</p>
          )}

          {results.map((item) => (
            <div
              key={item.id}
              onClick={() => navigate(`/project/${item.id}`)}
              className="p-3 border-b cursor-pointer hover:bg-gray-100"
            >
              <p className="font-medium">{item.title}</p>
              <p className="text-sm text-gray-500">
                {item.advisor} • {item.year}
              </p>
            </div>
          ))}
        </div>
      </div>


    </div>
  );
}