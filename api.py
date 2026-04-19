

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import ast

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
SUPABASE_URL = "https://aktmcjjhyezxiaggwenf.supabase.co"
SUPABASE_KEY = "sb_publishable_Sf1j8TGii4ttw19PbaQxSA_tnanpNjY"  # 🔥 ใส่ของคุณ

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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


# @app.get("/stats/advisors")
# def advisor_stats():
#     result = supabase.table("proposal_docs") \
#         .select("id, title, advisor, year") \
#         .execute()

#     data = result.data

#     advisor_map = {}

#     for p in data:
#         name = p["advisor"]

#         if not name:
#             continue

#         if name not in advisor_map:
#             advisor_map[name] = {
#                 "advisor": name,
#                 "projects": []
#             }

#         advisor_map[name]["projects"].append({
#             "id": p["id"],
#             "title": p["title"],
#             "year": p["year"]
#         })

#     return list(advisor_map.values())

# test chat bot

# from fastapi import Body
# from openai import OpenAI

# client = OpenAI()

# @app.post("/ask")
# def ask_llm(query: str = Body(...)):
#     # 🔥 ดึง project จาก DB
#     res = supabase.table("proposal_docs") \
#         .select("title, abstract") \
#         .limit(10) \
#         .execute()

#     projects = res.data

#     # 🔥 ทำ context
#     context = "\n".join([
#         f"- {p['title']}: {p.get('abstract', '')[:100]}"
#         for p in projects
#     ])

#     # 🔥 เรียก LLM
#     response = client.chat.completions.create(
#         model="gpt-4.1-mini",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "You recommend senior projects based on user needs."
#             },
#             {
#                 "role": "user",
#                 "content": f"""
# User wants: {query}

# Here are some projects:
# {context}

# Recommend 3 projects and explain why.
# """
#             }
#         ]
#     )

#     return {
#         "answer": response.choices[0].message.content
#     }