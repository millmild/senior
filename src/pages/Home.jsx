import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  const navigate = useNavigate();
  const scrollRef = useRef();

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  // 🔍 SEARCH STATE
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

  // 🔥 QUICK PICKS
  useEffect(() => {
    setLoading(true);

    fetch(`${API_BASE_URL}/projects/quick`)
      .then((res) => res.json())
      .then((data) => setProjects(data || []))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  // 🔍 SEARCH FUNCTION
  const handleSearch = async () => {
    if (!query.trim()) return;

    setSearchLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      setResults(data || []);
    } catch (err) {
      console.error(err);
    }

    setSearchLoading(false);
  };

  const scroll = (dir) => {
    const container = scrollRef.current;
    const amount = 300;

    if (dir === "left") container.scrollLeft -= amount;
    else container.scrollLeft += amount;
  };

  return (
    <div style={{ background: "#f5f6f8", minHeight: "100vh", padding: "30px" }}>
      {/* 🔵 HERO */}
      <div style={hero}>
        <h1>Welcome to SPR!</h1>
        <p>Explore senior projects, trends, and recommendations.</p>

        <div style={{ marginTop: "20px", display: "flex", gap: "10px" }}>
          <button onClick={() => navigate("/database")} style={heroBtn}>
            Senior Project Database
          </button>

          <button style={heroBtn}>Trending</button>

          <button onClick={() => navigate("/dashboard")} style={heroBtn}>
            Dashboard
          </button>
        </div>
      </div>

      {/* 🔍 SEARCH */}
      <div style={searchBox}>
        <h3>🔎 Search Projects</h3>

        <div style={{ display: "flex", gap: "10px" }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search เช่น AI, IoT..."
            style={input}
          />

          <button onClick={handleSearch} style={heroBtn}>
            Search
          </button>
        </div>

        {searchLoading && <p>🔍 Searching...</p>}

        <div style={{ marginTop: "10px" }}>
          {results.map((item) => (
            <div
              key={item.id}
              onClick={() => navigate(`/project/${item.id}`)}
              style={resultItem}
            >
              <b>{item.title}</b>
              <p style={{ fontSize: "12px", color: "#666" }}>
                {item.advisor} • {item.year}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 🔥 QUICK PICKS */}
      <h2 style={{ margin: "20px 0" }}>🔥 Quick Picks</h2>

      {loading && <p>🔍 Loading...</p>}

      <div style={{ position: "relative" }}>
        <button onClick={() => scroll("left")} style={leftBtn}>
          ‹
        </button>
        <button onClick={() => scroll("right")} style={rightBtn}>
          ›
        </button>

        <div ref={scrollRef} style={scrollContainer}>
          {projects.map((p) => (
            <div key={p.id} style={card}>
              <p style={{ color: "#888", fontSize: "12px" }}>📅 {p.year}</p>

              <h3>{p.title}</h3>
              <p>{p.advisor}</p>

              <div style={{ marginTop: "10px", display: "flex", gap: "5px" }}>
                <button
                  onClick={() => navigate(`/project/${p.id}`)}
                  style={btn}
                >
                  Detail
                </button>

                <button
                  onClick={() => navigate(`/similar/${p.id}`)}
                  style={btn}
                >
                  Similar
                </button>

                <button onClick={() => window.open(p.file_url)} style={btn}>
                  Open
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* 🎨 STYLE */

const hero = {
  background: "linear-gradient(to right, #4f6edb, #dae2fc)",
  padding: "30px",
  borderRadius: "20px",
  color: "white",
};

const heroBtn = {
  padding: "10px 15px",
  background: "white",
  color: "#2563eb",
  border: "none",
  borderRadius: "10px",
  cursor: "pointer",
  fontWeight: "bold",
};

const searchBox = {
  background: "white",
  padding: "15px",
  borderRadius: "15px",
  marginTop: "20px",
};

const input = {
  flex: 1,
  padding: "10px",
  borderRadius: "10px",
  border: "1px solid #ddd",
};

const resultItem = {
  padding: "10px",
  borderBottom: "1px solid #eee",
  cursor: "pointer",
};

const scrollContainer = {
  display: "flex",
  overflowX: "auto",
  gap: "15px",
  padding: "10px 0",
  scrollBehavior: "smooth",
};

const card = {
  minWidth: "250px",
  background: "white",
  padding: "15px",
  borderRadius: "12px",
  flexShrink: 0,
};

const btn = {
  padding: "5px 10px",
  background: "#f3f4f6",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
};

const leftBtn = {
  position: "absolute",
  left: 0,
  top: "40%",
  zIndex: 10,
};

const rightBtn = {
  position: "absolute",
  right: 0,
  top: "40%",
  zIndex: 10,
};
