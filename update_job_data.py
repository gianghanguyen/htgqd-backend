# from pymongo import MongoClient
# import re


# # Kết nối MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client['job_db']
# job_collection = db['job']


# # Hàm để chuyển đổi khoảng lương từ dạng chuỗi sang hai số và tính trung bình
# def parse_salary(salary_str):
#     """
#     Parses a salary string like "$59K-$99K" and returns the average salary as integer.
#     """
#     # Dùng regex để tìm các số trong chuỗi
#     match = re.findall(r'\d+', salary_str.replace('K', ''))
#     if len(match) == 2:
#         low_salary = int(match[0]) * 1000
#         high_salary = int(match[1]) * 1000
#         avg_salary = (low_salary + high_salary) // 2
#         return avg_salary
#     return 0


# # Hàm để parse years_of_experience và lấy số nhỏ nhất từ khoảng
# def parse_experience(exp_str):
#     """
#     Parses years_of_experience string like '5 to 15 Years' and returns the smaller number as integer.
#     """
#     match = re.findall(r'\d+', exp_str)
#     if len(match) >= 2:
#         # Lấy số nhỏ nhất
#         return min(int(match[0]), int(match[1]))
#     return 0


# # Duyệt qua tất cả các bản ghi và cập nhật dữ liệu trực tiếp vào các trường gốc
# def process_and_update_jobs():
#     for job in job_collection.find():
#         # Parse salary
#         avg_salary = parse_salary(job.get('salary', '0'))
        
#         # Parse years of experience
#         min_experience = parse_experience(job.get('years_of_experience', '0'))

#         # Cập nhật thông tin vào các trường gốc
#         update_fields = {
#             "salary": avg_salary,
#             "years_of_experience": min_experience
#         }

#         # Cập nhật bản ghi MongoDB
#         job_collection.update_one(
#             {"_id": job["_id"]},
#             {"$set": update_fields}
#         )

#         print(f"Updated job_id: {job['job_id']} with new salary: {avg_salary} and new years_of_experience: {min_experience}")


# # Thực thi
# if __name__ == "__main__":
#     process_and_update_jobs()


from pymongo import MongoClient
import re
from multiprocessing import Pool


# Kết nối MongoDB độc lập trong mỗi tiến trình
def get_mongo_client():
    """Mỗi worker sẽ tự thiết lập kết nối MongoDB riêng biệt"""
    client = MongoClient("mongodb://localhost:27017/")
    db = client['job_db']
    job_collection = db['job']
    return job_collection


# Hàm để chuyển đổi khoảng lương từ dạng chuỗi sang hai số và tính trung bình
def parse_salary(salary_str):
    """
    Parses a salary string like "$59K-$99K" and returns the average salary as integer.
    """
    match = re.findall(r'\d+', salary_str.replace('K', ''))
    if len(match) == 2:
        low_salary = int(match[0]) * 1000
        high_salary = int(match[1]) * 1000
        avg_salary = (low_salary + high_salary) // 2
        return avg_salary
    return 0


# Hàm để parse years_of_experience và lấy số nhỏ nhất từ khoảng
def parse_experience(exp_str):
    """
    Parses years_of_experience string like '5 to 15 Years' and returns the smaller number as integer.
    """
    match = re.findall(r'\d+', exp_str)
    if len(match) >= 2:
        return min(int(match[0]), int(match[1]))
    return 0


# Worker Function để xử lý một phần công việc
def worker_process(job_batch):
    """
    Worker xử lý một phần công việc (một batch của MongoDB).
    """
    try:
        # Kết nối MongoDB riêng biệt trong từng worker
        job_collection = get_mongo_client()

        # Duyệt qua danh sách bản ghi để parse và cập nhật thông tin
        for job in job_batch:
            avg_salary = parse_salary(job.get('salary', '0'))
            min_experience = parse_experience(job.get('years_of_experience', '0'))
            update_fields = {
                "salary": avg_salary,
                "years_of_experience": min_experience
            }

            # Cập nhật thông tin MongoDB
            job_collection.update_one(
                {"_id": job["_id"]},
                {"$set": update_fields}
            )

            print(f"Updated job_id: {job['job_id']} with new salary: {avg_salary} and new years_of_experience: {min_experience}")
        return len(job_batch)
    except Exception as e:
        print(f"Error processing batch: {e}")
        return 0


# Chia công việc thành các batch nhỏ để các worker xử lý song song
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


# Lấy danh sách công việc cần xử lý từ MongoDB
def get_jobs_to_process():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['job_db']
    job_collection = db['job']

    # Lấy tất cả bản ghi từ MongoDB
    jobs = list(job_collection.find({}))
    return jobs


# Main Function để thực thi multiprocessing
def main():
    # Lấy danh sách công việc
    jobs = get_jobs_to_process()

    # Số worker bạn muốn sử dụng, điều chỉnh theo CPU của bạn
    num_workers = 4

    # Chia công việc thành các batch nhỏ, mỗi worker xử lý một batch
    job_batches = divide_jobs(jobs, num_workers)

    # Dùng multiprocessing Pool để xử lý công việc song song
    with Pool(num_workers) as pool:
        # Dùng pool.map để truyền mỗi batch cho từng worker
        results = pool.map(worker_process, job_batches)

    # Thống kê kết quả
    total_processed = sum(results)
    print(f"Total jobs processed: {total_processed}")


# Thực thi
if __name__ == "__main__":
    main()
