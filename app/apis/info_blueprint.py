from sanic import Blueprint, Request
from sanic import exceptions
from sanic.response import json
from sanic_ext import openapi, validate

from app.models.project import PointQuery, JobQuery, CompanyQuery
from app.utils.logger_utils import get_logger

from app.databases.mongodb import MongoDB

logger = get_logger('Info blueprint')

info_bp = Blueprint('info', url_prefix='/info')


@info_bp.route('/point')
@openapi.definition(
    summary="Get job points",
    tag="Information"
)
@openapi.parameter("page", description="Page number", schema=int, location="query", required=True)
@openapi.parameter("size", description="Page size", schema=int, location="query", required=True)
@validate(query=PointQuery)
async def get_market_info(request: Request, query: PointQuery):

    page = int(query.page)
    size = int(query.size)

    _mongo_db: MongoDB = request.app.ctx.mongo_db
    points = _mongo_db.get_point_list(page_size=size, page=page)

    return json({
        'points': points
    })

@info_bp.route('/job')
@openapi.definition(
    summary="Get job information",
    tag="Information"
)
@openapi.parameter("jobId", description="Job Id", schema=int, location="query", required=True)
@validate(query=JobQuery)
async def get_job_info(request: Request, query: JobQuery):

    job_id = int(query.jobId)

    _mongo_db: MongoDB = request.app.ctx.mongo_db
    job_query = {"job_id": job_id}
    job = _mongo_db.get_job(job_query)
    job.pop('_id', None)

    return json({
        'job': job
    })

@info_bp.route('/company')
@openapi.definition(
    summary="Get company information",
    tag="Information"
)
@openapi.parameter("companyId", description="Company Id", location="query", required=True)
@validate(query=CompanyQuery)
async def get_company_info(request: Request, query: CompanyQuery):

    company_id = query.companyId

    _mongo_db: MongoDB = request.app.ctx.mongo_db
    company_query = {"company_id": company_id}
    company = _mongo_db.get_company(company_query)
    company.pop('_id', None)

    return json({
        'company': company
    })



