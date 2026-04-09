import { useEffect, useState } from "react";

export default function Trending() {
  const [keywords, setKeywords] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/keywords/trending")
      .then(res => res.json())
      .then(data => {
        console.log("DATA:", data);
        setKeywords(data || []);
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div style={{ padding: "30px" }}>
      <h2>📊 Trending Keywords</h2>

      <div style={grid}>
        {keywords
          .filter(k => k.keyword && k.keyword.trim() !== "")
          .map((k, i) => (
            <div key={i} style={card}>
              <h3>{format(k.keyword)}</h3>
              <p>{k.count} projects</p>
            </div>
          ))}
      </div>
    </div>
  );
}

const grid = {
  display: "grid",
  gridTemplateColumns: "repeat(4, 1fr)",
  gap: "15px",
  marginTop: "20px",
};

const card = {
  background: "white",
  padding: "15px",
  borderRadius: "12px",
};

function format(text) {
  return text
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}