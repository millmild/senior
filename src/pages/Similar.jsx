import { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

export default function Similar() {
  const { id } = useParams();
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
    <div style={{ padding: "30px" }}>
      <h2>🔥 Similar Projects</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "20px",
        }}
      >
        {data.map((item, i) => (
          <div
            key={item.id}
            style={{
              border: "1px solid #ccc",
              borderRadius: "10px",
              padding: "15px",
            }}
          >
            <h3>{item.title}</h3>
            <p>Score: {item.similarity?.toFixed(3)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}