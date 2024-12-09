from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from multiprocessing import Pool, cpu_count

# Kết nối tới MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["job_db"]
collection = db["job"]

# Khởi tạo model SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Hàm xử lý một batch document
def process_batch(jobs_batch):
    for job in jobs_batch:
        job_title = job.get("job_title", "")
        if job_title:
            # Tính embedding cho job_title
            embedding = model.encode(job_title).tolist()  # Chuyển sang danh sách để lưu vào MongoDB
            # Cập nhật document với trường mới
            collection.update_one({"_id": job["_id"]}, {"$set": {"job_title_embedded": embedding}})

# Lấy tất cả các document từ collection
jobs = list(collection.find())

# Chia các document thành các batch

def divide_jobs(jobs, num_workers):
    """
    Chia danh sách các công việc thành num_workers batch nhỏ để mỗi worker xử lý riêng biệt.
    """
    # Dựa vào số công việc và worker count, chia danh sách thành từng phần
    chunk_size = len(jobs) // num_workers
    batches = []
    for i in range(num_workers):
        start_index = i * chunk_size
        # Đảm bảo worker xử lý công việc cuối cùng nhận hết phần còn lại
        if i == num_workers - 1:
            batch = jobs[start_index:]
        else:
            batch = jobs[start_index:start_index + chunk_size]
        batches.append(batch)
    return batches

jobs_batches = divide_jobs(jobs, num_workers=7)

# Sử dụng multiprocessing để xử lý từng batch
if __name__ == "__main__":
    num_workers = 7  # Số lượng worker tương ứng với số lõi CPU
    with Pool(processes=num_workers) as pool:
        pool.map(process_batch, jobs_batches)

print("Update complete!")
