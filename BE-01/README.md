# BE-01 - Smallest Possible Backend

Two JSON endpoints. Run locally, test with curl and browser.

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Test

Browser: http://127.0.0.1:8000/ and http://127.0.0.1:8000/status

Curl:
```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/status
```

## Screenshots

Server running and both endpoints returning `200 OK`:

![VS Code terminal logs showing successful server start and requests](./Screenshots/3%20vs_code_logs_successful_200.JPG)

Root endpoint response:

![Result after running server](./Screenshots/1%20result_after_running_server.JPG)

Status endpoint response:

![Status endpoint returning ok](./Screenshots/2%20status_service_ok.JPG)