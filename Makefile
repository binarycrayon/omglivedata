ingest:
	python ingestion.py

runserver:
	gunicorn -k flask_sockets.worker omglivedata:app  --log-level debug --workers 2
