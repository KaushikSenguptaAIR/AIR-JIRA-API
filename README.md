# AIR JIRA Attachment API

Flask API service to handle file attachments for JIRA tickets from Power Automate flows.

## Endpoints

### Health Check
- **GET** `/health` - Returns API health status

### Attach File to JIRA
- **POST** `/attach-to-jira`
- **Body**: 
```json
  {
    "issueKey": "DITSD-123",
    "fileContent": "base64_encoded_file",
    "fileName": "screenshot.png"
  }
```

### Test Endpoint
- **POST** `/test` - Echo test for connectivity

## Deployment

This API is designed to be deployed on Railway.app with automatic GitHub integration.

## Environment

- Python 3.11
- Flask 2.3.3
- Gunicorn for production server