from unicodedata import category
from unittest import result
from fastapi import FastAPI, params
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import os
from dotenv import load_dotenv
import ast
import requests
import serpapi  # Make sure to run 'pip install serpapi'
from datetime import datetime
from contextlib import asynccontextmanager



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
SUPABASE_SECRET = os.getenv("SUPABASE_SECRET")

supabase = create_client(SUPABASE_URL, SUPABASE_SECRET)

# =========================
# 🧠 MODEL
# =========================
model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# 📦 REQUEST SCHEMA
# =========================
class QueryRequest(BaseModel):
    query: str
    year: int | None = None
    advisor: str | None = None

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def cosine_cluster(projects, threshold=0.8):
    clusters = []
    used = set()

    embeddings = [p["embedding"] for p in projects]

    sim_matrix = cosine_similarity(embeddings)

    for i, p in enumerate(projects):
        if i in used:
            continue

        cluster = [p]
        used.add(i)

        for j in range(len(projects)):
            if j not in used and sim_matrix[i][j] > threshold:
                cluster.append(projects[j])
                used.add(j)

        clusters.append(cluster)

    return clusters




@app.get("/projects/cluster")
def cluster_projects():

    result = supabase.table("proposal_docs") \
        .select("id, title, year, advisor, file_url, embedding") \
        .execute()

    projects = result.data

    # 🔥 แปลง embedding
    clean_projects = []

    for p in projects:
        emb = p.get("embedding")

        if not emb:
            continue

        if isinstance(emb, str):
            emb = ast.literal_eval(emb)

        p["embedding"] = emb
        clean_projects.append(p)

    # 🔥 ใช้ cosine clustering
    clusters = cosine_cluster(clean_projects, threshold=0.8)

    # 🔥 format output
    final = {}

    for cluster in clusters:
        name = get_cluster_name(cluster)

        items = []
        for p in cluster:
            p2 = p.copy()
            p2.pop("embedding", None)
            items.append(p2)

        if name in final:
            final[name].extend(items)
        else:
            final[name] = items

    return final


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
        "match_count": 5
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

# @app.get("/projects/quick")
# def get_quick_projects():
#     result = supabase.table("proposal_docs") \
#         .select("id,title,advisor,year,file_url") \
#         .order("year", desc=True) \
#         .limit(4) \
#         .execute()

#     return result.data

# @app.get("/projects/quick")
# def get_quick_projects():
#     result = supabase.rpc("random_projects", {
#         "limit_count": 10
#     }).execute()

#     return result.data

@app.get("/projects/quick")
def get_quick_projects(page: int = 1, limit: int = 20):
    start = (page - 1) * limit
    end = start + limit - 1

    result = supabase.table("proposal_docs") \
        .select("id,title,advisor,year,file_url") \
        .range(start, end) \
        .execute()

    return result.data

# @app.get("/keywords/trending")
# def get_keywords(year: int = None):
#     result = supabase.table("proposal_docs") \
#         .select("keywords, year") \
#         .execute()

#     data = result.data

#     keyword_count = {}

#     for row in data:
#         if year and row["year"] != year:
#             continue

#         if not row["keywords"]:
#             continue

#         for k in row["keywords"]:
#             keyword_count[k] = keyword_count.get(k, 0) + 1

#     # แปลงเป็น list + sort
#     result = [
#         {"keyword": k, "count": v}
#         for k, v in keyword_count.items()
#     ]

#     result.sort(key=lambda x: x["count"], reverse=True)

#     return result



def get_cluster_name(words):
    text = " ".join(words[:5]).lower()

    if "ai" in text or "learning" in text or "data" in text:
        return "🧠 AI & Data"

    if "iot" in text or "sensor" in text:
        return "🌐 IoT & Hardware"

    if "medical" in text or "health" in text:
        return "🏥 Healthcare"

    if "web" in text or "system" in text:
        return "💻 Software & Web"

    return "📊 Others"


def get_cluster_name(titles):
    text = " ".join(titles[:3]).lower()

    if any(x in text for x in ["ai", "learning", "nlp", "data"]):
        return "🧠 AI & Data"

    if any(x in text for x in ["iot", "sensor", "embedded"]):
        return "🌐 IoT & Hardware"

    if any(x in text for x in ["medical", "health", "hospital"]):
        return "🏥 Healthcare"

    if any(x in text for x in ["web", "system", "application"]):
        return "💻 Software & Web"

    return "📊 Others"

def get_cluster_name(projects):
    text = " ".join([p["title"] for p in projects[:5]]).lower()

    if any(x in text for x in ["ai", "learning", "nlp", "data"]):
        return "🧠 AI & Data"

    if any(x in text for x in ["iot", "sensor", "tracking"]):
        return "🌐 IoT & Hardware"

    if any(x in text for x in ["medical", "health", "dental"]):
        return "🏥 Healthcare"

    if any(x in text for x in ["web", "system", "application"]):
        return "💻 Software & Web"

    return "📊 Others"

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
    client = serpapi.Client(os.getenv("SERPAPI_KEY"))
    
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


