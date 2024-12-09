from pymongo import MongoClient
from bson import ObjectId


def transform_data():
    # Kết nối đến MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["job_db"]

    # Các collection
    job_raw_collection = db["job_raw"]
    company_collection = db["company"]
    job_collection = db["job"]

    # Đảm bảo collections mục tiêu rỗng
    company_collection.delete_many({})
    job_collection.delete_many({})

    # Lấy dữ liệu từ job_raw
    job_raw_data = job_raw_collection.find()

    company_id_map = {}  # Dùng để lưu thông tin mapping company_name -> company_id

    for job in job_raw_data:
        # Kiểm tra nếu bất kỳ trường thông tin nào quan trọng là None thì ngừng chương trình
        if not job.get("Company") or not job.get("Job Id") or not job.get("Job Title") or not job.get("Experience"):
            print("Required field is missing. Aborting process...")
            continue  # Ngừng thêm dữ liệu nếu có bất kỳ trường thông tin nào quan trọng là None

        company_name = job.get("Company")

        # Tạo một company_id duy nhất
        if company_name not in company_id_map:
            company_id = str(ObjectId())
            company_id_map[company_name] = company_id

            # Thêm document vào collection company
            company_document = {
                "company_id": company_id,
                "company_name": company_name,
                "company_size": job.get("Company Size"),
                "industry": job.get("Company Profile", {}).get("Industry") if isinstance(job.get("Company Profile", {}), dict) else None,
                "city": job.get("Company Profile", {}).get("City") if isinstance(job.get("Company Profile", {}), dict) else None,
                "state": job.get("Company Profile", {}).get("State") if isinstance(job.get("Company Profile", {}), dict) else None,
                "country": job.get("Country"),
                "location": job.get("location"),
                "zip": job.get("Company Profile", {}).get("Zip") if isinstance(job.get("Company Profile", {}), dict) else None,
                "website": job.get("Company Profile", {}).get("Website") if isinstance(job.get("Company Profile", {}), dict) else None,
                "ticker": job.get("Company Profile", {}).get("Ticker") if isinstance(job.get("Company Profile", {}), dict) else None,
                "ceo": job.get("Company Profile", {}).get("CEO") if isinstance(job.get("Company Profile", {}), dict) else None,
                "latitude": job.get("latitude"),
                "longitude": job.get("longitude"),
                "benefit": job.get("Benefits"),
                "contact_person": job.get("Contact Person"),
                "contact": job.get("Contact"),
            }

            # Kiểm tra nếu bất kỳ thông tin trong company_document là None thì break
            if any(value is None for value in company_document.values()):
                print("Critical field in company data is missing. Aborting process...")
                continue

            company_collection.insert_one(company_document)

        # Thêm document vào collection job
        job_document = {
            "job_id": job.get("Job Id"),
            "company_id": company_id_map[company_name],
            "job_title": job.get("Job Title"),
            "salary": job.get("Salary Range"),
            "description": job.get("Job Description"),
            "years_of_experience": job.get("Experience"),
            "skills": job.get("skills"),
            "responsibilities": job.get("Responsibilities"),
        }

        # Kiểm tra nếu bất kỳ thông tin trong job_document là None thì break
        if any(value is None for value in job_document.values()):
            print("Critical field in job data is missing. Aborting process...")
            continue

        job_collection.insert_one(job_document)

    print("Data transformed and inserted successfully.")


if __name__ == "__main__":
    transform_data()
