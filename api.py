

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from sentence_transformers import SentenceTransformer

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

# =========================
# 🔍 SEARCH (AI + FILTER)
# =========================
# @app.post("/search")
# def search(req: QueryRequest):

#     # 🔥 มี query → ใช้ AI
#     if req.query and req.query.strip() != "":
#         query_embedding = model.encode(req.query).tolist()

#         result = supabase.rpc("hybrid_search", {
#             "query_text": req.query,
#             "query_embedding": query_embedding,
#             "match_count": 100
#         }).execute()

#         data = result.data

#     # 🔥 ไม่มี query → เอาทั้งหมด
#     else:
#         result = supabase.table("proposal_docs") \
#             .select("*") \
#             .execute()

#         data = result.data

#     # ✅ FIX YEAR (สำคัญมาก)
#     if req.year is not None:
#         data = [
#             d for d in data
#             if str(d.get("year")) == str(req.year)
#         ]

#     # ✅ filter advisor
#     if req.advisor:
#         data = [
#             d for d in data
#             if d.get("advisor") and req.advisor.lower() in d["advisor"].lower()
#         ]

#     return data

# @app.post("/search")
# def search(req: QueryRequest):

#     # 🔥 ใช้ SQL search ก่อน (เร็วมาก)
#     if req.query and req.query.strip() != "":
#         result = supabase.table("proposal_docs") \
#             .select("*") \
#             .ilike("title", f"%{req.query}%") \
#             .limit(50) \
#             .execute()

#         data = result.data

#     else:
#         result = supabase.table("proposal_docs") \
#             .select("*") \
#             .limit(50) \
#             .execute()

#         data = result.data

#     return data

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

@app.get("/keywords/trending")
def get_keywords(year: int = None):
    result = supabase.table("proposal_docs") \
        .select("keywords, year") \
        .execute()

    data = result.data

    keyword_count = {}

    for row in data:
        if year and row["year"] != year:
            continue

        if not row["keywords"]:
            continue

        for k in row["keywords"]:
            keyword_count[k] = keyword_count.get(k, 0) + 1

    # แปลงเป็น list + sort
    result = [
        {"keyword": k, "count": v}
        for k, v in keyword_count.items()
    ]

    result.sort(key=lambda x: x["count"], reverse=True)

    return result