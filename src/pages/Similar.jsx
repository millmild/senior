import { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";

export default function Similar() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState([]);

  const API = "http://127.0.0.1:8000";

  useEffect(() => {
    fetchSimilar();
  }, []);

  const fetchSimilar = async () => {
    try {
      const res = await axios.get(`${API}/similar/${id}`);
      setData(res.data);
    } catch (err) {
      console.error("ERROR:", err);
    }
  };

  return (
    <div style={{ padding: "30px", background: "#f5f6f8", minHeight: "100vh" }}>
      
      <h2 style={{ marginBottom: "20px" }}>🔥 Similar Projects</h2>

      <div style={grid}>
        {data.map((item) => (
          <div key={item.id} style={card}>
            
            {/* 📅 YEAR */}
            <p style={year}>
              📅 {item.year || "-"}
            </p>

            {/* 🧠 TITLE */}
            <h3 style={title}>{item.title}</h3>

            {/* 👨‍🏫 ADVISOR */}
            <p style={advisor}>
              {item.advisor || "-"}
            </p>

            {/* 🔘 BUTTONS */}
            <div style={btnRow}>
              
              <button
                onClick={() => navigate(`/project/${item.id}`)}
                style={btn}
              >
                Detail
              </button>

              <button
                onClick={() => navigate(`/similar/${item.id}`)}
                style={btn}
              >
                Similar
              </button>

              <button
                onClick={() => {
                  if (item.file_url) {
                    window.open(item.file_url, "_blank");
                  } else {
                    alert("No file");
                  }
                }}
                style={btn}
              >
                Open
              </button>

            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* 🎨 STYLE */

const grid = {
  display: "grid",
  gridTemplateColumns: "repeat(3, 1fr)",
  gap: "20px",
};

const card = {
  background: "white",
  borderRadius: "15px",
  padding: "20px",
  boxShadow: "0 2px 10px rgba(0,0,0,0.05)",
  transition: "0.2s",
};

const year = {
  fontSize: "13px",
  color: "#888",
  marginBottom: "5px",
};

const title = {
  margin: "5px 0",
};

const advisor = {
  color: "#555",
  fontSize: "14px",
};

const btnRow = {
  marginTop: "15px",
  display: "flex",
  gap: "8px",
};

const btn = {
  padding: "6px 12px",
  background: "#f3f4f6",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
};