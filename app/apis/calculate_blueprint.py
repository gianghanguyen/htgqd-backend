from sanic import Blueprint, Request
from sanic import exceptions
from sanic.response import json
from sanic_ext import openapi, validate

from app.models.project import CalculateQuery
from app.utils.logger_utils import get_logger
from app.databases.mongodb import MongoDB

from concurrent.futures import ThreadPoolExecutor, as_completed
from haversine import haversine, Unit
import Levenshtein
from sentence_transformers import SentenceTransformer, util

WORKER_NUM = 10

logger = get_logger('Calculate blueprint')

calculate_bp = Blueprint('calculate', url_prefix='/calculate')


def calculate_company_point(user_latitude, user_longtitude, company_list):
    real_distance = dict()
    company_size_point = dict()

    for company in company_list:
        real_distance[company['company_id']] = haversine(
            (user_latitude, user_longtitude),
            (company['latitude'], company['longitude']),
            unit=Unit.KILOMETERS
        )
        company_size_point[company['company_id']] = company['company_size']

    max_location = max(real_distance.values())
    max_company_size = max(company_size_point.values())

    location_point = {k: (max_location - v) / max_location for k, v in real_distance.items()}
    company_size_point = {k: v / max_company_size for k, v in company_size_point.items()}
    return real_distance,location_point, company_size_point


def divide_jobs(jobs, num_workers):
    chunk_size = len(jobs) // num_workers
    batches = []
    for i in range(num_workers):
        start_index = i * chunk_size
        if i == num_workers - 1:
            batch = jobs[start_index:]
        else:
            batch = jobs[start_index:start_index + chunk_size]
        batches.append(batch)
    return batches


def job_worker_process(args):
    print("Start job worker process")
    job_batch, job_title_embed, experience, real_distance, location_point, company_size_point, location_weight, company_size_weight, job_title_weight, experience_weight, salary_weight = args

    mongo_db = MongoDB()

    job_title_point = dict()
    for job in job_batch:
        print(f"Calculating job title point for job {job['job_id']}")
        job_title_point[job['job_id']] = util.cos_sim(job['job_title_embedded'], job_title_embed).item() + 1

    max_job_title_point = max(job_title_point.values())
    max_salary = max([job['salary'] for job in job_batch])

    job_points = []
    for job in job_batch:
        job_point = dict()
        job_point['_id'] = job['job_id']
        job_point['company_id'] = job['company_id']
        job_point['job_title'] = job['job_title']
        job_point['experience'] = job['years_of_experience']
        job_point['salary'] = job['salary']
        job_point['real_distance'] = real_distance[job['company_id']]

        # Tính điểm cho từng yếu tố
        job_point['location_point'] = location_point[job['company_id']]
        job_point['company_size_point'] = company_size_point[job['company_id']]
        job_point['job_title_point'] = job_title_point[job['job_id']] / max_job_title_point
        job_point['experience_point'] = 1 if job['years_of_experience'] <= experience else 0
        job_point['salary_point'] = job['salary'] / max_salary

        # Áp dụng trọng số cho từng yếu tố và tính tổng điểm
        job_point['weighted_location_point'] = location_weight * job_point['location_point']
        job_point['weighted_company_size_point'] = company_size_weight * job_point['company_size_point']
        job_point['weighted_job_title_point'] = job_title_weight * job_point['job_title_point']
        job_point['weighted_experience_point'] = experience_weight * job_point['experience_point']
        job_point['weighted_salary_point'] = salary_weight * job_point['salary_point']
        job_points.append(job_point)

    weighted_ideal_solution = {
        'weighted_location_point': max(job_point['weighted_location_point'] for job_point in job_points),
        'weighted_company_size_point': max(job_point['weighted_company_size_point'] for job_point in job_points),
        'weighted_job_title_point': max(job_point['weighted_job_title_point'] for job_point in job_points),
        'weighted_experience_point': max(job_point['weighted_experience_point'] for job_point in job_points),
        'weighted_salary_point': max(job_point['weighted_salary_point'] for job_point in job_points),
    }

    weighted_negative_ideal_solution = {
        'weighted_location_point': min(job_point['weighted_location_point'] for job_point in job_points),
        'weighted_company_size_point': min(job_point['weighted_company_size_point'] for job_point in job_points),
        'weighted_job_title_point': min(job_point['weighted_job_title_point'] for job_point in job_points),
        'weighted_experience_point': min(job_point['weighted_experience_point'] for job_point in job_points),
        'weighted_salary_point': min(job_point['weighted_salary_point'] for job_point in job_points),
    }

    for job_point in job_points:
        job_point['distance_to_weighted_ideal'] = sum((job_point[factor] - weighted_ideal_solution[factor]) ** 2 for factor in weighted_ideal_solution) ** 0.5
        job_point['distance_to_weighted_negative_ideal'] = sum((job_point[factor] - weighted_negative_ideal_solution[factor]) ** 2 for factor in weighted_negative_ideal_solution) ** 0.5
        # Tính tổng điểm (similarity to the ideal solution)
        job_point['point'] = job_point['distance_to_weighted_negative_ideal'] / (job_point['distance_to_weighted_ideal'] + job_point['distance_to_weighted_negative_ideal'])

    mongo_db.insert_point(job_points)

    # Sắp xếp các công việc theo điểm từ cao đến thấp
    sorted_job_points = sorted(job_points, key=lambda x: x['point'], reverse=True)
    return sorted_job_points, weighted_ideal_solution, weighted_negative_ideal_solution

@calculate_bp.route('')
@openapi.definition(
    summary="Calculate jobs' point",
    tag="Calculate"
)
@openapi.parameter("userLatitude", description="User Latitude", schema=float, location="query", required=True)
@openapi.parameter("userLongtitude", description="User Longtitude", schema=float, location="query", required=True)
@openapi.parameter("jobTitle", description="Job Title", location="query", required=True)
@openapi.parameter("experience", description="Experience", schema=int, location="query", required=True)
@openapi.parameter("locationWeight", description="Location Weight", schema=float, location="query", required=True)
@openapi.parameter("companySizeWeight", description="Company Size Weight", schema=float, location="query", required=True)
@openapi.parameter("jobTitleWeight", description="Job Title Weight", schema=float, location="query", required=True)
@openapi.parameter("experienceWeight", description="Experience Weight", schema=float, location="query", required=True)
@openapi.parameter("salaryWeight", description="Salary Weight", schema=float, location="query", required=True)
@validate(query=CalculateQuery)
async def calculate(request: Request, query: CalculateQuery):
    user_latitude = float(query.userLatitude)
    user_longtitude = float(query.userLongtitude)
    job_title = query.jobTitle
    experience = int(query.experience)

    location_weight = float(query.locationWeight)
    company_size_weight = float(query.companySizeWeight)
    job_title_weight = float(query.jobTitleWeight)
    experience_weight = float(query.experienceWeight)
    salary_weight = float(query.salaryWeight)

    _mongo_db: MongoDB = request.app.ctx.mongo_db
    company_list = _mongo_db.get_company_list()
    job_list = _mongo_db.get_job_list()

    # Calculate company point
    try:
        real_distance, location_point, company_size_point = calculate_company_point(user_latitude, user_longtitude, company_list)
    except Exception as e:
        logger.error(f"Error calculating company point: {e}")
        raise exceptions.ServerError("Error calculating company point")

    # Calculate job point
    all_job_points = []  # Biến lưu tất cả điểm công việc
    try:
      _mongo_db.delete_point({})
    except Exception as e:
      logger.error(f"Error deleting point: {e}")
      raise exceptions.ServerError("Error deleting point")
    
    try:
        job_batches = divide_jobs(job_list, WORKER_NUM)

        model = SentenceTransformer('all-MiniLM-L6-v2')
        job_title_embeded = model.encode(job_title)

        job_batches_with_args = [(job_batch, job_title_embeded, experience, real_distance, location_point, company_size_point, location_weight, company_size_weight, job_title_weight, experience_weight, salary_weight) for job_batch in job_batches]

        with ThreadPoolExecutor(max_workers=WORKER_NUM) as executor:
            futures = [executor.submit(job_worker_process, args) for args in job_batches_with_args]
        
        all_sorted_job_points = []
        weighted_ideal_solution = None
        weighted_negative_ideal_solution = None
        for future in as_completed(futures):
            try:
                sorted_job_points, weighted_ideal_solution, weighted_negative_ideal_solution = future.result()
                all_sorted_job_points.extend(sorted_job_points)
            except Exception as e:
                logger.error(f"Error in one of the worker jobs: {e}")
                raise exceptions.ServerError("Error occurred during job execution")
        
        # Select top 50 jobs
        all_sorted_job_points = sorted(all_sorted_job_points, key=lambda x: x['point'], reverse=True)
        top_50_jobs = all_sorted_job_points[:50]

    except Exception as e:
        logger.error(f"Error calculating job point: {e}")
        raise exceptions.ServerError("Error calculating job point")

    return json({
        'result': 'success',
        'top_50_jobs': top_50_jobs,
        'weighted_ideal_solution': weighted_ideal_solution,
        'weighted_negative_ideal_solution': weighted_negative_ideal_solution
    })
