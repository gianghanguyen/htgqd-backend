from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Kết nối tới MongoDB localhost
db = client["job_db"]
job_collection = db["job"]
job_processed_collection = db["job_processed"]

# Lấy tất cả các document từ job collection
pipeline = [
    {
        "$sort": {"years_of_experience": -1}  # Sắp xếp theo years_of_experience giảm dần
    },
    {
        "$group": {  # Dùng $group để nhóm theo company_id và job_title
            "_id": {"company_id": "$company_id", "job_title": "$job_title"},
            "max_doc": {"$first": "$$ROOT"}  # Lấy document đầu tiên sau khi sắp xếp
        }
    }
]

# Thực thi pipeline aggregation
results = job_collection.aggregate(pipeline)

# Lưu kết quả vào collection job_processed
for result in results:
    document_to_store = result["max_doc"]
    # Chèn dữ liệu vào job_processed
    job_processed_collection.insert_one(document_to_store)

print("Data has been processed and saved to 'job_processed'.")
