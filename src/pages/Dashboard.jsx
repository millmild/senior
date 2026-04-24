import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  // ================= SEARCH =================
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
      const res = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({ query, year: null, advisor: null }),
      });

      const data = await res.json();
      setResults(data.slice(0, 10));
    } catch (err) {
      if (err.name !== "AbortError") console.error(err);
    }

    setLoading(false);
  };

  // ================= TRENDING =================
  const [trending, setTrending] = useState([]);
  const [loadingTrends, setLoadingTrends] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/projects/trending?limit=5`)
      .then((res) => res.json())
      .then((data) => {
        setTrending(Array.isArray(data) ? data : []);
        setLoadingTrends(false);
      })
      .catch(() => setLoadingTrends(false));
  }, []);

  // ================= ADVISORS =================
  const [advisors, setAdvisors] = useState([]);
  const [year, setYear] = useState(0);
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [selectedAdvisor, setSelectedAdvisor] = useState(null);
  const [loadingAdvisor, setLoadingAdvisor] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/stats/advisors`)
      .then((res) => res.json())
      .then((data) => setAdvisors(data || []));
  }, []);

  return (
    <div className="p-6 bg-gray-100 min-h-screen space-y-6">
      <h1 className="text-3xl font-bold">📊 Dashboard</h1>

      {/* ================= REMOVED THE 3-COLUMN GRID ================= */}
      <div className="space-y-6">
        {/* SEARCH - Now automatically takes full width */}
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-lg font-semibold mb-3">🔎 Search Projects</h2>
          <div className="flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="flex-1 border px-4 py-2 rounded-lg"
            />
            <button
              onClick={handleSearch}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg"
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

        {/* TRENDING - Updated to grid-cols-3 for better use of full width */}
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="font-semibold mb-4">🔥 Trending Projects</h2>
          {loadingTrends ? (
            <p>Loading...</p>
          ) : (
            /* Changed md:grid-cols-2 to lg:grid-cols-3 since we have more horizontal space */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trending.map((p) => (
                <div
                  key={p.id}
                  onClick={() => navigate(`/project/${p.id}`)}
                  className="p-4 border rounded-xl cursor-pointer hover:shadow transition bg-gray-50"
                >
                  <p className="font-bold line-clamp-2">{p.title}</p>
                  <p className="text-xs text-orange-500 mt-1">
                    {p.trending_reason}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ================= 🔥 ADVISORS (MOVED DOWN) ================= */}
      <div className="bg-white p-6 rounded-2xl shadow-md">
        <div className="flex justify-between mb-4">
          <h2 className="text-xl font-bold">👨‍🏫 Browse Advisors</h2>

          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="border px-3 py-2 rounded-lg"
          >
            <option value={0}>All</option>
            <option value={2016}>2016</option>
            <option value={2017}>2017</option>
            <option value={2020}>2020</option>
            <option value={2021}>2021</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {advisors.map((a) => {
            const projects = (a.projects || []).filter(
              (p) => !year || p.year === year,
            );

            if (projects.length === 0) return null;

            return (
              <div key={a.advisor} className="bg-gray-50 p-4 rounded-xl shadow">
                <p className="font-semibold text-lg">{a.advisor}</p>
                <p className="text-sm text-gray-500">
                  {projects.length} projects
                </p>

                <div className="max-h-32 overflow-y-auto text-sm mt-2">
                  {projects.slice(0, 5).map((p) => (
                    <p
                      key={p.id}
                      onClick={() => navigate(`/project/${p.id}`)}
                      className="cursor-pointer hover:text-blue-500"
                    >
                      • {p.title}
                    </p>
                  ))}
                </div>

                <button
                  className="mt-2 text-blue-600"
                  onClick={async () => {
                    setLoadingAdvisor(true);
                    setSelectedAdvisor(a.advisor);

                    const res = await fetch(
                      `${API_BASE_URL}/advisor/${encodeURIComponent(
                        a.advisor,
                      )}`,
                    );
                    const data = await res.json();

                    setSelectedProjects(data || []);
                    setLoadingAdvisor(false);
                  }}
                >
                  View projects →
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {selectedAdvisor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* BACKDROP */}
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => {
              setSelectedAdvisor(null);
              setSelectedProjects([]);
            }}
          />

          {/* MODAL */}
          <div className="relative bg-white w-[600px] max-h-[80vh] overflow-y-auto p-6 rounded-xl z-10">
            {/* HEADER */}
            <div className="flex justify-between mb-4">
              <h2 className="text-lg font-bold">{selectedAdvisor}</h2>
              <button
                onClick={() => {
                  setSelectedAdvisor(null);
                  setSelectedProjects([]);
                }}
              >
                ✕
              </button>
            </div>

            {/* LIST */}
            {loadingAdvisor ? (
              <p>Loading...</p>
            ) : (
              (selectedProjects || []).map((p) => (
                <button
                  key={p.id}
                  onClick={(e) => {
                    e.stopPropagation(); // 🔥 สำคัญ
                    setSelectedAdvisor(null); // ปิด modal
                    navigate(`/project/${p.id}`);
                  }}
                  className="w-full text-left p-3 border-b hover:bg-gray-50 cursor-pointer"
                >
                  <p className="font-medium">{p.title}</p>
                  <p className="text-sm text-gray-500">{p.year}</p>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
