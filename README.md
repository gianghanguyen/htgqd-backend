## Setup variables environment
Copy `.env.example` file, then fill your config into the new `.env` file.
```shell
cp .env.example .env
```

## Local installation and development

Install dependencies
```shell
pip3 install -r requrements.txt
```

Run server with `python`
```shell
python3 main.py
```

## Deployment
```shell
docker compose up
```

## Documentation
Access swagger document via [http://0.0.0.0:8096/docs](http://0.0.0.0:8096/docs)

## MongoDB
Database: job_db
Collection: job, company, point (empty)
