import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Database() {
  const [query, setQuery] = useState("");
  const [year, setYear] = useState("");
  const [results, setResults] = useState([]);

  const navigate = useNavigate();

  const handleSearch = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/search", {
        query: query || "",
        year: year ? Number(year) : null,
      });

      setResults(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  // 🔥 โหลดครั้งแรก
  useEffect(() => {
    handleSearch();
  }, []);

  // 🔥 เลือกปีแล้วค้นหาเลย
  useEffect(() => {
    handleSearch();
  }, [year]);

  return (
    <div className="p-8">
      <h1>📚 Senior Database</h1>

      <input
        placeholder="Search..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <select value={year} onChange={(e) => setYear(e.target.value)}>
        <option value="">All</option>
        <option value="2021">2021</option>
        <option value="2020">2020</option>
        <option value="2017">2017</option>
        <option value="2016">2016</option>
      </select>

      <button onClick={handleSearch}>Search</button>

      <p>Results: {results.length}</p>

      <div>
        {results.map((r) => (
          <div key={r.id}>
            <h3>{r.title}</h3>
            <p>{r.year}</p>

            <button onClick={() => navigate(`/project/${r.id}`)}>
              Detail
            </button>

            <button onClick={() => navigate(`/similar/${r.id}`)}>
              Similar
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}