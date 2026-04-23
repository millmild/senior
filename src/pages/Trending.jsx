import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

export default function Trending() {
  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  const [clusters, setClusters] = useState({});
  const [selectedProjects, setSelectedProjects] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API_BASE_URL}/projects/trend`)
      .then((res) => res.json())
      .then((data) => {
        console.log("TREND:", data);
        setClusters(data || {});
      })
      .catch((err) => console.error(err));
  }, []);

  return (
    <div style={container}>
      <h1> Faculty Trend</h1>

      {/* 🔥 loop year */}
      {Object.entries(clusters).map(([year, topics]) => (
        <div key={year} style={{ marginBottom: "40px" }}>
          <h2>{year}</h2>

          <div style={scrollRow}>
            {/* 🔥 loop topic */}
            {Object.entries(topics).map(([topic, projects]) => (
              <div key={topic} style={card}>
                <h3>{topic}</h3>
                <p>{projects.length} projects</p>

                {/* 🔥 preview projects */}
                <div style={{ marginTop: "10px" }}>
                  {projects.slice(0, 3).map((p) => (
                    <p
                      key={p.id}
                      onClick={() => navigate(`/project/${p.id}`)}
                      style={{
                        fontSize: "12px",
                        color: "#555",
                        cursor: "pointer",
                      }}
                    >
                      • {p.title}
                    </p>
                  ))}
                </div>

                {/* ✅ VIEW ALL (POPUP) */}
                <button
                  onClick={() => setSelectedProjects(projects)}
                  style={btn}
                >
                  View all →
                </button>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* ================= POPUP ================= */}
      {selectedProjects && (
        <div style={overlay}>
          <div style={modal}>
            <h2>All Projects</h2>

            <div style={{ maxHeight: "400px", overflowY: "auto" }}>
              {selectedProjects.map((p) => (
                <div
                  key={p.id}
                  style={popupItem}
                  onClick={() => navigate(`/project/${p.id}`)}
                >
                  <p style={{ fontWeight: "bold" }}>{p.title}</p>
                  <p style={{ fontSize: "12px", color: "#666" }}>
                    {p.advisor} • {p.year}
                  </p>
                </div>
              ))}
            </div>

            <button onClick={() => setSelectedProjects(null)} style={btn}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/* 🎨 STYLE */

const container = {
  padding: "30px",
  background: "#f5f6f8",
  minHeight: "100vh",
};

const scrollRow = {
  display: "flex",
  overflowX: "auto",
  gap: "15px",
};

const card = {
  minWidth: "250px",
  background: "white",
  padding: "15px",
  borderRadius: "15px",
  flexShrink: 0,
  boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
};

const btn = {
  marginTop: "10px",
  padding: "5px 10px",
  background: "#f3f4f6",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
};

/* 🔥 POPUP */

const overlay = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  background: "rgba(0,0,0,0.5)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 999,
};

const modal = {
  background: "white",
  padding: "20px",
  borderRadius: "15px",
  width: "500px",
};

const popupItem = {
  padding: "10px",
  borderBottom: "1px solid #eee",
  cursor: "pointer",
};
