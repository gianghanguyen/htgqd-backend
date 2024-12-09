from pymongo import MongoClient
import random

# Kết nối tới MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["job_db"]
job_collection = db["job"]
job_reduce_collection = db["job_reduce"]

# Xóa dữ liệu cũ trong collection job_reduce (nếu cần)
job_reduce_collection.delete_many({})

# Nhóm các document theo job_title và lấy 1% mỗi nhóm
pipeline = [
    {"$group": {
        "_id": "$job_title",
        "docs": {"$push": "$$ROOT"}
    }}
]

# Chạy pipeline để nhóm dữ liệu
result = job_collection.aggregate(pipeline)

for group in result:
    job_title = group["_id"]
    documents = group["docs"]

    # Lấy 1% ngẫu nhiên số document từ nhóm này
    sample_size = max(1, len(documents) // 10)  # Ít nhất 1 document
    sampled_documents = random.sample(documents, sample_size)

    # Chèn vào collection job_reduce
    job_reduce_collection.insert_many(sampled_documents)

print("Hoàn thành việc lưu dữ liệu vào job_reduce.")