import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function SeniorDatabase() {
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [year, setYear] = useState("");
  const [advisor, setAdvisor] = useState("");

  const [results, setResults] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const limit = 12;

  const handleSearch = async (newPage = 1) => {
    setLoading(true);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/search/full?page=${newPage}&limit=${limit}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query,
            year: year ? Number(year) : null,
            advisor: advisor || null,
          }),
        }
      );

      const data = await res.json();

      setResults(data.data || []);
      setTotal(data.total || 0);
      setPage(newPage);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  useEffect(() => {
    handleSearch(1);
  }, []);

  const totalPages = Math.ceil(total / limit);

  return (
    <div style={{ padding: "30px", background: "#f5f6f8", minHeight: "100vh" }}>
      <h2 style={{ marginBottom: "20px" }}>📚 Senior Database</h2>

      {/* 🔍 SEARCH */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input
          placeholder="Search by keyword or title..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ padding: "10px", flex: 1 }}
        />

        <select
          value={year}
          onChange={(e) => setYear(e.target.value)}
          style={{ padding: "10px" }}
        >
          <option value="">All years</option>
          <option value="2025">2025</option>
          <option value="2024">2024</option>
          <option value="2023">2023</option>
          <option value="2022">2022</option>
          <option value="2021">2021</option>
          <option value="2020">2020</option>
          <option value="2017">2017</option>
          <option value="2016">2016</option>
        </select>

        <input
          placeholder="Advisor (optional)"
          value={advisor}
          onChange={(e) => setAdvisor(e.target.value)}
          style={{ padding: "10px" }}
        />

        <button onClick={() => handleSearch(1)} style={searchBtn}>
          Search
        </button>

        <button
          onClick={() => {
            setQuery("");
            setYear("");
            setAdvisor("");
            handleSearch(1);
          }}
          style={clearBtn}
        >
          Clear
        </button>
      </div>

      <p>Results: {total}</p>

      {loading && <p>🔍 Loading...</p>}

      {/* 📦 RESULTS */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "20px",
          marginTop: "20px",
        }}
      >
        {results.map((item, i) => (
          <div
            key={item.id}
            style={{
              background: "white",
              borderRadius: "15px",
              padding: "15px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
            }}
          >
            <p style={{ color: "#888", fontSize: "14px" }}>
              #{i + 1} • {item.year}
            </p>

            <h3>{item.title}</h3>

            <p style={{ color: "#555" }}>
              Advisor: {item.advisor}
            </p>

            {/* 🔘 BUTTONS */}
            <div style={{ marginTop: "10px", display: "flex", gap: "8px" }}>
              <button
                onClick={() => navigate(`/project/${item.id}`)}
                style={btnStyle}
              >
                Detail
              </button>

              <button
                onClick={() => navigate(`/similar/${item.id}`)}
                style={btnStyle}
              >
                Similar
              </button>

              <button
                onClick={() => {
                  console.log("URL:", item.file_url); // debug
                  if (item.file_url) {
                    window.open(item.file_url, "_blank");
                  } else {
                    alert("No file");
                  }
                }}
                style={btnStyle}
              >
                📄 Open
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 🔄 PAGINATION */}
      <div style={{ marginTop: "30px", textAlign: "center" }}>
        <button
          onClick={() => handleSearch(page - 1)}
          disabled={page === 1}
          style={pageBtn}
        >
          ⬅ Prev
        </button>

        <span style={{ margin: "0 15px" }}>
          Page {page} / {totalPages || 1}
        </span>

        <button
          onClick={() => handleSearch(page + 1)}
          disabled={page === totalPages || totalPages === 0}
          style={pageBtn}
        >
          Next ➡
        </button>
      </div>
    </div>
  );
}

/* 🎨 STYLE */
const btnStyle = {
  padding: "6px 12px",
  background: "#f3f4f6",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
};

const searchBtn = {
  padding: "10px 15px",
  background: "#2563eb",
  color: "white",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
};

const clearBtn = {
  padding: "10px 15px",
  background: "#e5e7eb",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
};

const pageBtn = {
  padding: "8px 12px",
  margin: "0 5px",
  cursor: "pointer",
};