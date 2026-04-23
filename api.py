#V.2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from sentence_transformers import SentenceTransformer
import serpapi  # Make sure to run 'pip install serpapi'
from datetime import datetime
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when you start the server
    fetch_serpapi_trends() 
    yield

load_dotenv()

app = FastAPI()

# =========================
# 🔓 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔗 SUPABASE
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = "sb_publishable_Sf1j8TGii4ttw19PbaQxSA_tnanpNjY"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SECRET = os.getenv("SUPABASE_SECRET")

supabase = create_client(SUPABASE_URL, SUPABASE_SECRET)

# =========================
# 🧠 MODEL
# =========================
model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        model.half()
    return model

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/predict")
def predict():
    m = get_model()
    return {"message": "model loaded"}


# model = SentenceTransformer("all-MiniLM-L6-v2")
# model = SentenceTransformer("all-mpnet-base-v2")
# =========================
# 📦 REQUEST SCHEMA
# =========================
class QueryRequest(BaseModel):
    query: str
    year: int | None = None
    advisor: str | None = None


import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def cosine_cluster(projects, threshold=0.65):
    clusters = []

    for p in projects:
        placed = False

        for cluster in clusters:
            # 🔥 หา centroid ของ cluster
            embeddings = [x["embedding"] for x in cluster]
            centroid = np.mean(embeddings, axis=0)

            # 🔥 วัด similarity กับ centroid
            score = cosine_similarity(
                [p["embedding"]],
                [centroid]
            )[0][0]

            if score > threshold:
                cluster.append(p)
                placed = True
                break

        # 🔥 ถ้ายังไม่มี cluster → สร้างใหม่
        if not placed:
            clusters.append([p])

    return clusters

def cluster_projects(projects):
    clusters = cosine_cluster(projects, threshold=0.6)

    good_clusters = []
    outliers = []

    # 🔹 แยกตัวเดี่ยว
    for c in clusters:
        if len(c) == 1:
            outliers.append(c[0])
        else:
            good_clusters.append(c)

    # 🔹 เอา outliers ไปใส่ cluster ที่ใกล้สุด
    from sklearn.metrics.pairwise import cosine_similarity

    for outlier in outliers:
        best_cluster = None
        best_score = 0

        for cluster in good_clusters:
            for p in cluster:
                score = cosine_similarity(
                    [outlier["embedding"]],
                    [p["embedding"]]
                )[0][0]

                if score > best_score:
                    best_score = score
                    best_cluster = cluster

        # 🔥 ถ้าใกล้พอ → ยัดเข้า
        if best_score > 0.4:
            best_cluster.append(outlier)

    # 🔥 ตัวที่ยังเหลือ → Others
    remaining = []
    for o in outliers:
        if all(o not in c for c in good_clusters):
            remaining.append(o)

    if remaining:
        good_clusters.append(remaining)  # 👉 Others

    return good_clusters

def classify_project(text: str):
    text = text.lower()

    # 🔥 AI
    if any(k in text for k in [
        "ai", "artificial intelligence",
        "machine learning", "deep learning",
        "neural network", "cnn", "rnn",
        "nlp", "natural language processing",
        "text mining", "chatbot", "classification",
        "prediction model"
    ]):
        return "AI"

    # 🔥 IoT
    if any(k in text for k in [
        "iot", "internet of things",
        "sensor", "arduino", "raspberry",
        "embedded", "microcontroller",
        "smart", "device", "monitoring",
        "temperature", "humidity",
        "wireless", "automation"
    ]):
        return "IoT"

    # 🔥 Healthcare
    if any(k in text for k in [
    "health", "healthcare", "medical",
    "patient", "disease",
    "diagnosis", "hospital","Vaccine",
    "treatment", "symptom",
    "whodas", "disability", "assessment"
    ]):
        return "Healthcare"

    # 🔥 Data
    if any(k in text for k in [
        "data", "data science", "data analysis",
        "big data", "analytics",
        "mining", "forecast", "prediction",
        "statistics", "dashboard"
    ]):
        return "Data"

    # 🔥 Game
    if any(k in text for k in [
        "game", "gaming",
        "vr", "virtual reality","virtual",
        "ar", "augmented reality","Mobile Game",
        "unity", "3d", "simulation","Raspberry","Image Processing",
    ]):
        return "Game and VR"

    # 🔥 Security
    if any(k in text for k in [
        "security", "cybersecurity",
        "attack", "malware", "phishing",
        "encryption", "authentication"
    ]):
        return "Security"

    # 🔥 Web (ไว้ล่างสุดเสมอ)
    if any(k in text for k in [
        "web", "website",
        "application", "platform",
        "frontend", "backend",
        "api", "system"
    ]):
        return "Web"

    return "Others"


@app.get("/projects/classified")
def get_projects():
    res = supabase.table("proposal_docs") \
        .select("id, title, advisor, year, embedding") \
        .limit(200) \
        .execute()

    data = res.data or []

    # 🔥 ใช้ clustering
    clusters = cluster_projects(data)

    result = []

    for cluster in clusters:
        # 🔥 ถ้าเป็น Others (cluster ใหญ่แต่มั่ว)
        if len(cluster) == 1:
            topic = "Others"
        else:
           topics = [classify_project(p["title"]) for p in cluster]
           from collections import Counter 
           topic = Counter(topics).most_common(1)[0][0]

        result.append({
            "topic": topic,
            "projects": cluster
        })

    return result


@app.get("/projects/trend")
def trend():
    res = supabase.table("proposal_docs") \
        .select("id, title, advisor, year") \
        .limit(200) \
        .execute()

    data = res.data or []

    result = {}

    for p in data:
        year = p["year"]
        topic = classify_project(p["title"])

        if year not in result:
            result[year] = {}

        if topic not in result[year]:
            result[year][topic] = []

        result[year][topic].append(p)  # 🔥 เก็บ project จริง

    return result

@app.post("/search")
def search(req: QueryRequest):

    query = req.query or ""

    if query.strip() != "":
        query_embedding = model.encode(query).tolist()

        result = supabase.rpc("hybrid_search", {
            "query_text": query,
            "query_embedding": query_embedding,
            "match_count": 20
        }).execute()

        data = result.data
    else:
        result = supabase.table("proposal_docs") \
            .select("*") \
            .limit(20) \
            .execute()

        data = result.data

    return data


# search database page
@app.post("/search/full")
def full_search(
    req: QueryRequest,
    page: int = 1,
    limit: int = 20
):
    start = (page - 1) * limit
    end = start + limit - 1

    query = req.query or ""

    # =========================
    # 🔍 CASE 1: มี keyword → AI
    # =========================
    if query.strip() != "":
        query_embedding = model.encode(query).tolist()

        result = supabase.rpc("hybrid_search", {
            "query_text": query,
            "query_embedding": query_embedding,
            "match_count": 100
        }).execute()

        data = result.data

    # =========================
    # 📄 CASE 2: ไม่มี keyword
    # =========================
    else:
        result = supabase.table("proposal_docs") \
           .select("id,title,advisor,year,file_url,keywords")\
            .execute()

        data = result.data

    # =========================
    # 🔥 FILTER (สำคัญ)
    # =========================
    if req.year:
        data = [d for d in data if d.get("year") == req.year]

    if req.advisor:
        data = [
            d for d in data
            if d.get("advisor") and req.advisor.lower() in d["advisor"].lower()
        ]

    # =========================
    # PAGINATION
    # =========================
    paginated = data[start:end+1]

    return {
        "data": paginated,
        "total": len(data)
    }

# =========================
# SIMILAR


@app.get("/similar/{project_id}")
def similar(project_id: str):
    result = supabase.rpc("recommend_projects", {
        "input_id": project_id,
        "match_count": 100
    }).execute()

    return result.data



# =========================
# 👨‍🏫 ADVISORS
# =========================
@app.get("/stats/advisors")
def advisors():
    result = supabase.rpc("top_advisor_per_year").execute()
    return result.data

# =========================
# 📄 PROJECT DETAIL
# =========================
@app.get("/project/{project_id}")
def get_project(project_id: str):
    result = supabase.table("proposal_docs") \
        .select("*") \
        .eq("id", project_id) \
        .execute()

    if len(result.data) == 0:
        return {"error": "Not found"}

    return result.data[0]

@app.get("/projects/quick")
def get_quick_projects(page: int = 1, limit: int = 20):
    start = (page - 1) * limit
    end = start + limit - 1

    result = supabase.table("proposal_docs") \
        .select("id,title,advisor,year,file_url") \
        .range(start, end) \
        .execute()

    return result.data

from fastapi import HTTPException
from ai import generate_summary, extract_clean_keyword

@app.get("/project/{project_id}/summary")
def get_project_summary(project_id: str):
    try:
        # Use .single() to get the specific project
        result = supabase.table("proposal_docs").select("*").eq("id", project_id).single().execute()
        project = result.data

        if not project:
            return {"summary": "Project not found."}

        # 1. Try to return existing summary (Check for None/Null or empty string)
        existing = project.get("summary")
        if existing and len(str(existing).strip()) > 0:
            return {"summary": existing}

        # 2. If no summary, check if we have text to summarize
        raw_text = project.get("raw_text")
        if not raw_text or len(str(raw_text).strip()) < 100:
            return {"summary": "Project text is too short to generate a summary."}

        # 3. GENERATE IT
        # This will only happen ONCE per project
        new_summary = generate_summary(raw_text)

        # 4. SAVE IT (Using Service Role Key ensures this always succeeds)
        if new_summary and new_summary != "Summary unavailable.":
            supabase.table("proposal_docs") \
                .update({"summary": new_summary}) \
                .eq("id", project_id) \
                .execute()

        return {"summary": new_summary}

    except Exception as e:
        print(f"Error for {project_id}: {e}")
        return {"summary": "Summary currently unavailable."}

#////////////////////////////////////////////////////////////////////////////
import time
from datetime import datetime, timezone, timedelta
def fetch_serpapi_trends():
    print("\n--- 🚀 Checking Technology Trend Cache ---")
    api_key = os.getenv("SERPAPI_KEY")
    client = serpapi.Client(api_key=api_key)
    
    try:
        # 1. CACHE CHECK
        recent_data = supabase.table("trending_topics").select("last_updated").limit(1).execute()
        
        if recent_data.data:
            last_sync_str = recent_data.data[0]["last_updated"]
            
            # Convert string to datetime
            dt = datetime.fromisoformat(last_sync_str.replace('Z', '+00:00'))
            
            # FORCE it to be UTC aware (This fixes the 'naive' error)
            last_sync = dt.replace(tzinfo=timezone.utc)
            
            # Get current time as UTC aware
            now = datetime.now(timezone.utc)
            
            # Now both are 'Aware', and subtraction is safe
            if now - last_sync < timedelta(hours=12):
                print(f"🕒 Trends are fresh (Synced {now - last_sync} ago). Skipping.")
                return

        # 2. FETCH NEW TRENDS
        print("📡 Cache stale. Fetching fresh trends from SerpApi...")
        results = client.search({
            "engine": "google_trends",
            "q": "Technology",
            "data_type": "RELATED_QUERIES",
            "geo": "US",
            "hl": "en"
        })

        trends = results.get("related_queries", {}).get("rising", [])
        payload = []

        for item in trends[:1]:
            raw_query = item.get("query")
            if not raw_query: continue

            # 3. GEMINI REFINEMENT
            refined_topic = extract_clean_keyword(raw_query)
            
            # Cooldown to avoid 429 Resource Exhausted on Free Tier
            time.sleep(2) 

            # 4. GROWTH LOGIC
            growth_raw = item.get("value", 0)
            if isinstance(growth_raw, str) and "breakout" in growth_raw.lower():
                growth = 5000.0
            else:
                try:
                    growth = float(str(growth_raw).replace('+', '').replace('%', ''))
                except:
                    growth = 0.0

            # 5. VECTOR EMBEDDING (Using the REFINED topic)
            trend_vec = model.encode(refined_topic).tolist()

            payload.append({
                "keyword": raw_query,              # Raw Google query
                "extracted_keyword": refined_topic, # Cleaned Gemini topic
                "growth_pct": growth,
                "category": "Technology",
                "embedding": trend_vec,
                "last_updated": datetime.now(timezone.utc).isoformat()
            })

        if payload:
            # 6. ATOMIC UPDATE: Clear and Replace
            supabase.table("trending_topics").delete().neq("keyword", "force_delete").execute()
            supabase.table("trending_topics").insert(payload).execute()
            print(f"✅ Successfully synced {len(payload)} refined trends.")
        
    except Exception as e:
        print(f"❌ Trend sync failed: {e}")


# ==================================================
# MANUAL REFRESH ROUTE
# ==================================================
@app.get("/trends/sync")
def sync_trends():
    fetch_serpapi_trends()
    return {"message": "Technology trends synced successfully."}


# ==================================================
# TRENDING PROJECTS TAB
# (NO AUTO DAILY REFRESH YET)
# ==================================================
@app.get("/projects/trending")
def get_trending_projects(limit: int = 5):
    try:
        # 1. Get the top trend from our recently synced table
        trend_res = supabase.table("trending_topics") \
            .select("keyword, embedding") \
            .order("growth_pct", desc=True) \
            .limit(1).execute()

        if not trend_res.data:
            return []

        top_trend = trend_res.data[0]
        
        # 2. Use Vector Search (RPC) to find projects related to that keyword
        # This requires the 'match_documents' SQL function in Supabase
        rpc_res = supabase.rpc("match_documents", {
            "query_embedding": top_trend["embedding"],
            "match_threshold": 0.3,
            "match_count": limit
        }).execute()

        # 3. Format for Dashboard.jsx
        return [{
            "id": p["id"],
            "title": p["title"],
            "summary": p.get("summary", "No summary available"),
            "advisor": p.get("advisor", "Unknown"),
            "trending_reason": f"Matches trend: {top_trend['keyword']}"
        } for p in rpc_res.data]

    except Exception as e:
        print(f"Error: {e}")
        return []



if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run("api:app", host="0.0.0.0", port=port)


