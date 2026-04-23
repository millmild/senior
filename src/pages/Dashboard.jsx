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
  const controllerRef = useRef(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    if (controllerRef.current) controllerRef.current.abort();

    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({ query, year: null, advisor: null }),
      });
      const data = await res.json();
      setResults(data.slice(0, 10));
    } catch (err) {
      if (err.name !== "AbortError") console.error("Search error:", err);
    }
    setLoading(false);
  };

  // ======================
  // 🔥 TRENDING PROJECTS (New Section)
  // ======================
  const [trending, setTrending] = useState([]);
  const [loadingTrends, setLoadingTrends] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/projects/trending?limit=5")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setTrending(data);
        }
        setLoadingTrends(false);
      })
      .catch((err) => {
        console.error("Trend fetch error:", err);
        setLoadingTrends(false);
      });
  }, []);

  // ======================
  // 👨‍🏫 TOP ADVISORS
  // ======================
  const [advisors, setAdvisors] = useState([]);
  const [year, setYear] = useState(2021);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/stats/advisors")
      .then((res) => res.json())
      .then((data) => setAdvisors(data));
  }, []);

  const filteredAdvisors = advisors.filter((a) => a.year === year).slice(0, 5);

  return (
    <div className="p-6 bg-gray-100 min-h-screen space-y-6">
      <h1 className="text-3xl font-bold">📊 Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Search & Trends */}
        <div className="lg:col-span-2 space-y-6">
          {/* ================= SEARCH ================= */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="text-lg font-semibold mb-3">🔎 Search Projects</h2>
            <div className="flex gap-2">
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) =>
                  e.key === "Enter" && !loading && handleSearch()
                }
                placeholder="Search projects..."
                className="flex-1 border px-4 py-2 rounded-lg"
              />
              <button
                onClick={handleSearch}
                disabled={loading}
                className="bg-blue-500 text-white px-6 py-2 rounded-lg disabled:bg-gray-400"
              >
                {loading ? "..." : "Search"}
              </button>
            </div>

            <div className="mt-4">
              {results.map((item) => (
                <div
                  key={item.id}
                  onClick={() => navigate(`/project/${item.id}`)}
                  className="p-3 border-b cursor-pointer hover:bg-gray-50 rounded-lg transition"
                >
                  <p className="font-medium text-blue-600">{item.title}</p>
                  <p className="text-sm text-gray-500">
                    {item.advisor} • {item.year}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* ================= TRENDING PROJECTS ================= */}
          <div className="bg-white p-6 rounded-xl shadow">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xl">🔥</span>
              <h2 className="text-lg font-semibold">Dynamic Recommendations</h2>
            </div>

            {loadingTrends ? (
              <div className="animate-pulse space-y-3">
                <div className="h-10 bg-gray-200 rounded"></div>
                <div className="h-10 bg-gray-200 rounded"></div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {trending.map((project) => (
                  <div
                    key={project.id}
                    onClick={() => navigate(`/project/${project.id}`)}
                    className="p-4 border border-orange-100 bg-orange-50/30 rounded-xl cursor-pointer hover:shadow-md transition group"
                  >
                    <p className="font-bold text-gray-800 group-hover:text-orange-600">
                      {project.title}
                    </p>
                    <p className="text-xs font-semibold text-orange-500 mt-1 uppercase tracking-wider">
                      {project.trending_reason}
                    </p>
                    <p className="text-xs text-gray-500 mt-2 line-clamp-2">
                      {project.summary}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Advisors */}
        <div className="space-y-6">
          {/* ================= TOP ADVISORS ================= */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="text-lg font-semibold mb-3">👨‍🏫 Top Advisors</h2>
            <select
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="w-full border px-3 py-2 rounded-lg mb-4"
            >
              {[2020, 2021, 2022, 2023].map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>

            <div className="space-y-3">
              {filteredAdvisors.map((a, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-gray-400">#{i + 1}</span>
                    <p className="text-sm font-medium">{a.advisor}</p>
                  </div>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                    {a.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
