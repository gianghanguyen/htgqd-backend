from pymongo import MongoClient


# Kết nối đến MongoDB local
client = MongoClient("mongodb://localhost:27017/")

# Chọn database và collections
db = client["job_db"]
job_collection = db["job"]
company_collection = db["company"]

# Lấy danh sách company_id hợp lệ từ collection company
valid_company_ids = set(
    company["company_id"] for company in company_collection.find({}, {"company_id": 1})
)

# Xóa các job có company_id không nằm trong danh sách hợp lệ
result = job_collection.delete_many(
    {"company_id": {"$nin": list(valid_company_ids)}}
)

# In kết quả
print(f"Đã xóa {result.deleted_count} công việc không hợp lệ.")

# from pymongo import MongoClient

# # Kết nối đến MongoDB local
# client = MongoClient("mongodb://localhost:27017/")

# # Chọn database và collections
# db = client["job_db"]
# job_collection = db["job"]

# # Xóa các job không có trường job_title_embedded
# result = job_collection.delete_many({"job_title_embedded": {"$exists": False}})

# # In kết quả
# print(f"Đã xóa {result.deleted_count} công việc không có trường 'job_title_embedded'.")