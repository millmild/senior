

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import ast
from fastapi import Body

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
        "ar", "augmented reality",
        "unity", "3d", "simulation","Raspberry"
    ]):
        return "Game"

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





# topics = {
#     "AI": ["ai", "machine learning", "deep learning", "nlp", "vision"],
#     "IoT": ["iot", "sensor", "embedded", "arduino", "raspberry"],
#     "Web": ["web", "application", "system", "platform"],
#     "Data": ["data", "analysis", "prediction", "mining"],
#     "Healthcare": ["health", "medical", "patient", "disease"],
#     "Security": ["security", "attack", "malware"],
#     "Game": ["game", "vr"],
# }

# # ======================
# # 🔥 PRECOMPUTE EMBEDDING
# # ======================
# topic_embeddings = {
#     topic: model.encode(" ".join(words))
#     for topic, words in topics.items()
# }

# # ======================
# # 🧠 CLASSIFIER
# # ======================
# def classify_project(text: str):
#     text_lower = text.lower()

#     # ✅ keyword match ก่อน (แม่นสุด)
#     for topic, keywords in topics.items():
#         for k in keywords:
#             if k in text_lower:
#                 return topic

#     # ✅ fallback → embedding
#     vec = model.encode(text)

#     best_topic = None
#     best_score = -1

#     for topic, t_vec in topic_embeddings.items():
#         score = np.dot(vec, t_vec)
#         if score > best_score:
#             best_score = score
#             best_topic = topic

#     return best_topic or "Others"

# # ======================
# # 📊 API: CLASSIFIED PROJECTS
# # ======================
# @app.get("/projects/classified")
# def get_projects():
#     res = supabase.table("proposal_docs") \
#         .select("id, title, advisor, year, embedding") \
#         .limit(200) \
#         .execute()

#     data = res.data or []

#     clusters = cluster_projects(data)

#     result = []

#     for cluster in clusters:
#         text = " ".join([p["title"] for p in cluster])
#         topic = classify_project(text)

#         result.append({
#             "topic": topic,
#             "projects": cluster
#         })

#     return result   # ✅ อยู่ใน function แล้ว

# # ======================
# # 📈 API: TREND PER YEAR


# # ======================
# # 🔎 API: SEARCH + CLASSIFY
# # ======================
# @app.get("/search")
# def search(q: str):
#     res = supabase.table("proposal_docs") \
#         .select("id, title, advisor, year") \
#         .ilike("title", f"%{q}%") \
#         .limit(20) \
#         .execute()

#     data = res.data or []

#     for p in data:
#         p["topic"] = classify_project(p["title"])

#     return data













# @app.get("/projects/cluster")
# def cluster_projects():

#     result = supabase.table("proposal_docs") \
#         .select("id, title, year, advisor, file_url, embedding") \
#         .execute()

#     projects = result.data

#     # 🔥 แปลง embedding
#     clean_projects = []

#     for p in projects:
#         emb = p.get("embedding")

#         if not emb:
#             continue

#         if isinstance(emb, str):
#             emb = ast.literal_eval(emb)

#         p["embedding"] = emb
#         clean_projects.append(p)

#     # 🔥 ใช้ cosine clustering
#     clusters = cosine_cluster(clean_projects, threshold=0.8)

#     # 🔥 format output
#     final = {}

#     for cluster in clusters:
#         name = get_cluster_name(cluster)

#         items = []
#         for p in cluster:
#             p2 = p.copy()
#             p2.pop("embedding", None)
#             items.append(p2)

#         if name in final:
#             final[name].extend(items)
#         else:
#             final[name] = items

#     return final


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




# def get_cluster_name(words):
#     text = " ".join(words[:5]).lower()

#     if "ai" in text or "learning" in text or "data" in text:
#         return "🧠 AI & Data"

#     if "iot" in text or "sensor" in text:
#         return "🌐 IoT & Hardware"

#     if "medical" in text or "health" in text:
#         return "🏥 Healthcare"

#     if "web" in text or "system" in text:
#         return "💻 Software & Web"

#     return "📊 Others"


# def get_cluster_name(titles):
#     text = " ".join(titles[:3]).lower()

#     if any(x in text for x in ["ai", "learning", "nlp", "data"]):
#         return "🧠 AI & Data"

#     if any(x in text for x in ["iot", "sensor", "embedded"]):
#         return "🌐 IoT & Hardware"

#     if any(x in text for x in ["medical", "health", "hospital"]):
#         return "🏥 Healthcare"

#     if any(x in text for x in ["web", "system", "application"]):
#         return "💻 Software & Web"

#     return "📊 Others"

# def get_cluster_name(projects):
#     text = " ".join([p["title"] for p in projects[:5]]).lower()

#     if any(x in text for x in ["ai", "learning", "nlp", "data"]):
#         return "🧠 AI & Data"

#     if any(x in text for x in ["iot", "sensor", "tracking"]):
#         return "🌐 IoT & Hardware"

#     if any(x in text for x in ["medical", "health", "dental"]):
#         return "🏥 Healthcare"

#     if any(x in text for x in ["web", "system", "application"]):
#         return "💻 Software & Web"

#     return "📊 Others"


# @app.get("/stats/trend")
# def trend_per_year():
#     res = supabase.table("proposal_docs") \
#         .select("title, year, embedding") \
#         .execute()

#     data = res.data or []

#     embeddings = []
#     valid = []

#     for d in data:
#         if d["embedding"]:
#             emb = d["embedding"]

#             if isinstance(emb, str):
#                 emb = ast.literal_eval(emb)

#             embeddings.append(emb)
#             valid.append(d)

#     embeddings = np.array(embeddings)

#     # 🔥 cluster
#     kmeans = KMeans(n_clusters=5, random_state=42)
#     labels = kmeans.fit_predict(embeddings)

#     result = {}

#     for i, d in enumerate(valid):
#         year = d["year"]
#         cluster = int(labels[i])

#         if year not in result:
#             result[year] = {}

#         if cluster not in result[year]:
#             result[year][cluster] = 0

#         result[year][cluster] += 1

#     return result

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

# from dotenv import load_dotenv
# import os
# from fastapi import Body
# from pydantic import BaseModel
# from openai import OpenAI

# load_dotenv()

# print("DEBUG KEY:", os.getenv("OPENAI_API_KEY"))

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # ✅ request model
# class Query(BaseModel):
#     query: str

# @app.post("/ask")
# def ask_llm(data: Query):
#     query = data.query

#     # 🔥 ดึง project จาก DB
#     res = supabase.table("proposal_docs") \
#         .select("title, raw_text") \
#         .limit(10) \
#         .execute()

#     projects = res.data or []

#     # 🔥 ทำ context
#     context = "\n".join([
#         f"- {p['title']}: {p.get('raw_text', '')[:100]}"
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
