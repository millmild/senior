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

app = FastAPI(lifespan=lifespan)

# =========================
# 🔓 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"  #Your production link 
        ],
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




model = SentenceTransformer("all-MiniLM-L6-v2")
# model = SentenceTransformer("all-mpnet-base-v2")
# =========================
# 📦 REQUEST SCHEMA
# =========================
class QueryRequest(BaseModel):
    query: str
    year: int | None = None
    advisor: str | None = None

from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import numpy as np

# ==================================================
# MODEL
# ==================================================
model = SentenceTransformer("all-MiniLM-L6-v2")

# ==================================================
# REQUEST SCHEMA
# ==================================================
class QueryRequest(BaseModel):
    query: str
    year: int | None = None
    advisor: str | None = None

# ==================================================
# HELPER
# รวม title + keywords
# ==================================================
def build_project_text(project):
    title = project.get("title", "") or ""
    keywords = project.get("keywords", "") or ""

    # ถ้า keywords เป็น list
    if isinstance(keywords, list):
        keywords = " ".join(keywords)

    return f"{title} {keywords}".lower().strip()

# ==================================================
# CLUSTERING
# ==================================================
def cosine_cluster(projects, threshold=0.7):
    clusters = []

    for p in projects:

        # กัน embedding พัง
        if not p.get("embedding"):
            continue

        placed = False

        for cluster in clusters:

            embeddings = [
                x["embedding"]
                for x in cluster
                if x.get("embedding")
            ]

            if not embeddings:
                continue

            # centroid
            centroid = np.mean(embeddings, axis=0)

            # similarity
            score = cosine_similarity(
                [p["embedding"]],
                [centroid]
            )[0][0]

            if score > threshold:
                cluster.append(p)
                placed = True
                break

        # สร้าง cluster ใหม่
        if not placed:
            clusters.append([p])

    return clusters

# ==================================================
# POST PROCESS CLUSTER
# ==================================================
def cluster_projects(projects):

    clusters = cosine_cluster(projects, threshold=0.7)

    good_clusters = []
    outliers = []

    # แยก cluster เดี่ยว
    for c in clusters:
        if len(c) == 1:
            outliers.append(c[0])
        else:
            good_clusters.append(c)

    # เอา outlier ไปใส่ cluster ที่ใกล้สุด
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

        # similarity สูงพอ
        if best_score > 0.55 and best_cluster:
            best_cluster.append(outlier)

    # ที่เหลือ → Others
    remaining = []

    for o in outliers:
        if all(o not in c for c in good_clusters):
            remaining.append(o)

    if remaining:
        good_clusters.append(remaining)

    return good_clusters

# ==================================================
# CLASSIFICATION
# ==================================================
def classify_project(text: str):

    text = text.lower()

    categories = {


        "Healthcare": [
            "health",
            "Dengue Severity",
            "Dengue Haemorrhagic Fever",
            "healthcare",
            "medical",
            "Human",
            "diabetic retinopathy",
            "diabetes",
            "Flare-Up Prediction",
            "vessel",
            "patient",
            "disease",
            "diagnosis",
            "hospital",
            "vaccine",
            "treatment",
            "SUSPECTED DENGUE",
            "DFD",
            "symptom",
            "whodas",
            "disability",
            "assessment"
        ],

        "Business & E-Commerce Systems": [
            "e-commerce",
            "E-Commerce"
            "retail",
            "WHOLESALE"
            "inventory",
            "crm",
            "Retailer"
            "erp",
            "payment"

        ],
        "IoT": [
            "iot",
            "internet of things",
            "sensor",
            "arduino",
            "raspberry",
            "embedded",
            "microcontroller",
            "smart device",
            "monitoring",
            "temperature",
            "humidity",
            "Measurement",
            "Pressure Sensors",
            "wireless",
            "automation"
        ],

        "Artificial Intelligence": [
            "ai",
            "artificial intelligence",
            "image processing",
            "machine learning",
            "deep learning",
            "neural network",
            "cnn",
            "rnn",
            "nlp",
            "natural language processing",
            "image analysis",
            "text mining",
            "chatbot",
            "classification",
            "transformer",
            "bert",
            "gpt",
            "large language model",
            "llm",
            "generative ai",
            "Machine Learning",
            "Machine",
            "prediction model"

        ],
        
         "Game and VR": [
            "game",
            "gaming",
            "vr",
            "virtual reality",
            "ffmpeg",
            "augmented reality",
            "mobile game",
            "video game",
            "unity",
            "3d",
            "Education Game",
            "Rubric",
            "simulation"
            "robot",
            "robotics",
            "autonomous"
        ],

    
        "Data": [
            "data",
            "data science",
            "data analysis",
            "big data",
            "analytics",
            "mining",
            "forecast",
            "statistics",
            "dashboard"
        ],

        "Security": [
            "security",
            "cybersecurity",
            "attack",
            "malware",
            "phishing",
            "encryption",
            "authentication"
        ],
        "web & Mobile Development":[
            
        "web", "website",
        "application", "platform",
        "frontend", "backend",
        "api", "system","mobile", "app", "development"
        ]
    }

    for category, keywords in categories.items():

        if any(keyword in text for keyword in keywords):
            return category

    return "Others"


@app.get("/projects/classified")
def get_projects():

    res = supabase.table("proposal_docs") \
        .select("id, title, keywords, advisor, year, embedding") \
        .limit(200) \
        .execute()

    data = res.data or []

    # กัน embedding none
    data = [
        d for d in data
        if d.get("embedding") is not None
    ]

    # clustering
    clusters = cluster_projects(data)

    result = []

    for cluster in clusters:

        # cluster เดี่ยว
        if len(cluster) == 1:
            topic = "Others"

        else:
            topics = [
                classify_project(
                    build_project_text(p)
                )
                for p in cluster
            ]

            topic = Counter(topics).most_common(1)[0][0]

        result.append({
            "topic": topic,
            "projects": cluster
        })

    return result



@app.get("/projects/trend")
def trend():

    res = supabase.table("proposal_docs") \
        .select("id, title, keywords, advisor, year") \
        .limit(200) \
        .execute()

    data = res.data or []

    result = {}

    for p in data:

        year = p.get("year")

        text = build_project_text(p)

        topic = classify_project(text)

        if year not in result:
            result[year] = {}

        if topic not in result[year]:
            result[year][topic] = []

        result[year][topic].append(p)

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
# @app.get("/stats/advisors")
# def advisors():
#     result = supabase.rpc("top_advisor_per_year").execute()
#     return result.data

@app.get("/stats/advisors")
def advisors():
    result = supabase.table("proposal_docs") \
        .select("id, title, year, advisor") \
        .limit(500) \
        .execute()

    advisor_map = {}

    for row in result.data:
        name = row["advisor"]

        if name not in advisor_map:
            advisor_map[name] = []

        advisor_map[name].append(row)

    return [
        {"advisor": k, "projects": v}
        for k, v in advisor_map.items()
    ]

@app.get("/advisor/{advisor_name}")
def get_advisor_projects(advisor_name: str):
    result = supabase.table("proposal_docs") \
        .select("id, title, year, advisor") \
        .ilike("advisor", advisor_name + "%") \
        .execute()

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


