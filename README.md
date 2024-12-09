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

## Documentation
Access swagger document via [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)

## MongoDB
Database: job_db

Collection: job, company, point (empty)
