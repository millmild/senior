import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const scrollRef = useRef();

  const [project, setProject] = useState(null);
  const [similar, setSimilar] = useState([]);

  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  // ================= SUMMARY =================
  useEffect(() => {
    setLoadingSummary(true);
    fetch(`http://127.0.0.1:8000/project/${id}/summary`)
      .then((res) => res.json())
      .then((data) => {
        setSummary(data.summary);
        setLoadingSummary(false);
      })
      .catch((err) => {
        console.error(err);
        setLoadingSummary(false);
      });
  }, [id]);
  // ================= LOAD DETAIL =================
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/project/${id}`)
      .then((res) => res.json())
      .then((data) => setProject(data))
      .catch((err) => console.error(err));
  }, [id]);

  // ================= LOAD SIMILAR =================
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/similar/${id}`)
      .then((res) => res.json())
      .then((data) => setSimilar(data))
      .catch((err) => console.error(err));
  }, [id]);

  // ================= SCROLL =================
  const scroll = (dir) => {
    const container = scrollRef.current;
    const amount = 320;

    if (dir === "left") container.scrollLeft -= amount;
    else container.scrollLeft += amount;
  };

  if (!project) return <p style={{ padding: "30px" }}>Loading...</p>;

  return (
    <div style={container}>
      {/* ================= DETAIL ================= */}
      <h1>{project.title}</h1>

      <p style={info}>
        {project.advisor} • {project.year}
      </p>

      {/* 🏷️ KEYWORDS */}
      <div style={{ margin: "10px 0" }}>
        {project.keywords?.slice(0, 5).map((k, i) => (
          <span key={i} style={tag}>
            {formatTag(k)}
          </span>
        ))}
      </div>

      {/* 📄 ABSTRACT */}
      <p style={{ maxWidth: "800px" }}>{project.abstract}</p>

      {/* 📄 PDF PREVIEW */}
      {project.file_url && (
        <iframe
          src={project.file_url}
          title="PDF"
          width="100%"
          height="500px"
          style={pdf}
        />
      )}
      <div style={summaryBox}>
        <h3 style={{ marginTop: 0, color: "#2c3e50" }}>✨ AI Key Insights</h3>
        {loadingSummary ? (
          <p style={{ color: "#7f8c8d", fontStyle: "italic" }}>
            Analyzing project details...
          </p>
        ) : (
          <div style={summaryContent}>
            {/* This renders the text while preserving newlines from the AI */}
            <pre style={summaryPre}>{summary || "No summary available."}</pre>
          </div>
        )}
      </div>

      {/* ================= SIMILAR ================= */}
      <h2 style={{ marginTop: "40px" }}>🔥 Similar Projects</h2>

      <div style={{ position: "relative" }}>
        <button onClick={() => scroll("left")} style={leftBtn}>
          ‹
        </button>
        <button onClick={() => scroll("right")} style={rightBtn}>
          ›
        </button>

        <div ref={scrollRef} style={scrollContainer}>
          {similar.map((item) => (
            <div
              key={item.id}
              style={card}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = "scale(1.05)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = "scale(1)";
              }}
            >
              {/* YEAR */}
              <p style={year}>📅 {item.year}</p>

              {/* TITLE */}
              <h3>{item.title}</h3>

              {/* ADVISOR */}
              <p style={{ color: "#555" }}>{item.advisor}</p>

              {/* SCORE
              <p style={score}>⭐ {item.similarity?.toFixed(3)}</p> */}

              {/* BUTTONS */}
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
                      window.open(item.file_url);
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
    </div>
  );
}

/* ================= STYLE ================= */

const container = {
  padding: "30px",
  background: "#f5f6f8",
  minHeight: "100vh",
};

const info = {
  color: "#666",
  marginBottom: "10px",
};

const tag = {
  background: "#e0e7ff",
  padding: "5px 10px",
  borderRadius: "12px",
  fontSize: "12px",
  marginRight: "5px",
};

const pdf = {
  marginTop: "20px",
  borderRadius: "10px",
  border: "1px solid #ddd",
};

const scrollContainer = {
  display: "flex",
  overflowX: "auto",
  gap: "15px",
  padding: "10px 0",
  scrollBehavior: "smooth",
};

const card = {
  minWidth: "300px",
  background: "white",
  padding: "15px",
  borderRadius: "15px",
  flexShrink: 0,
  cursor: "pointer",
  boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
  transition: "0.2s",
};

const btnRow = {
  marginTop: "10px",
  display: "flex",
  gap: "8px",
};

const btn = {
  padding: "6px 12px",
  background: "#f3f4f6",
  border: "none",
  borderRadius: "10px",
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

const year = {
  fontSize: "12px",
  color: "#888",
};

const score = {
  fontSize: "12px",
  color: "#888",
};

/* 🔧 FORMAT TAG */

function formatTag(text) {
  return text
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

const summaryBox = {
  background: "#ffffff",
  borderRadius: "14px",
  padding: "20px",
  marginTop: "25px",
  marginBottom: "25px",
  boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
  border: "1px solid #ecf0f1",
  maxWidth: "900px",
};

const summaryContent = {
  marginTop: "10px",
};

const summaryPre = {
  whiteSpace: "pre-wrap",
  fontFamily: "inherit",
  fontSize: "15px",
  lineHeight: "1.7",
  color: "#2d3436",
  margin: 0,
};

// import { useState } from "react";
// import axios from "axios";
// import { useNavigate } from "react-router-dom";

// export default function Home() {
//   const [query, setQuery] = useState("");
//   const [results, setResults] = useState([]);
//   const navigate = useNavigate();

//   const handleSearch = async () => {
//     try {
//       const res = await axios.post("http://127.0.0.1:8000/search", {
//         query: query
//       });
//       setResults(res.data);
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   return (
//     <div className="p-6">
//       <h1 className="text-2xl font-bold mb-4">Search Projects</h1>

//       <div className="flex gap-2">
//         <input
//           className="border p-2"
//           value={query}
//           onChange={(e) => setQuery(e.target.value)}
//           placeholder="Search..."
//         />
//         <button
//           onClick={handleSearch}
//           className="bg-blue-500 text-white px-4"
//         >
//           Search
//         </button>
//       </div>

//       <div className="mt-4 bg-white rounded shadow">
//         {results.map((p, i) => (
//           <div
//             key={i}
//             className="p-3 border-b cursor-pointer hover:bg-gray-100"
//             onClick={() => navigate(`/project/${p.project_id}`)}
//           >
//             {p.title}
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// }
