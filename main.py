from flask import Flask, request, jsonify
import requests
import base64
import logging
import os
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# JIRA Configuration from environment variables
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://alfakher.atlassian.net')
JIRA_USERNAME = os.environ.get('JIRA_USERNAME')
JIRA_TOKEN = os.environ.get('JIRA_TOKEN')

@app.route('/', methods=['GET'])
def home():
    """Home endpoint to confirm API is running"""
    return jsonify({
        "service": "AIR JIRA Attachment API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "JIRA Attachment API is running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/attach-to-jira', methods=['POST'])
def attach_to_jira():
    """Main endpoint to attach files to JIRA tickets"""
    try:
        # Check if credentials are configured
        if not JIRA_USERNAME or not JIRA_TOKEN:
            return jsonify({"error": "JIRA credentials not configured"}), 500
        
        # Log incoming request
        logging.info("Received attachment request")
        
        # Get data from Power Automate
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        issue_key = data.get('issueKey')
        file_content_b64 = data.get('fileContent')
        filename = data.get('fileName', 'screenshot.png')
        
        # Validate required fields
        if not issue_key:
            return jsonify({"error": "issueKey is required"}), 400
        if not file_content_b64:
            return jsonify({"error": "fileContent is required"}), 400
        
        logging.info(f"Processing attachment for ticket: {issue_key}")
        logging.info(f"Filename: {filename}")
        
        try:
            # Convert base64 to binary
            file_data = base64.b64decode(file_content_b64)
            logging.info(f"File size after decoding: {len(file_data)} bytes")
        except Exception as e:
            return jsonify({"error": f"Invalid base64 content: {str(e)}"}), 400
        
        # Prepare JIRA API call
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/attachments"

        # Create base64 encoded credentials for explicit Basic auth
        credentials = base64.b64encode(f"{JIRA_USERNAME}:{JIRA_TOKEN}".encode()).decode()
        
        headers = {
            'X-Atlassian-Token': 'no-check',
            'Authorization': f'Basic {credentials}'
        }
        
        files = {
            'file': (filename, file_data, 'image/png')
        }
        
        logging.info(f"Calling JIRA API: {url}")
        
        # Make request to JIRA
        response = requests.post(
            url, 
            files=files, 
            headers=headers,
            auth=(JIRA_USERNAME, JIRA_TOKEN),
            timeout=30
        )
        
        logging.info(f"JIRA API response status: {response.status_code}")
        
        if response.status_code == 200:
            return jsonify({
                "status": response.status_code,
                "success": True,
                "message": "Attachment uploaded successfully",
                "issue_key": issue_key,
                "filename": filename,
                "timestamp": datetime.now().isoformat()
            })
        else:
            logging.error(f"JIRA API error: {response.text}")
            return jsonify({
                "status": response.status_code,
                "success": False,
                "message": "Failed to upload attachment",
                "error": response.text,
                "issue_key": issue_key,
                "timestamp": datetime.now().isoformat()
            }), 500
        
    except requests.exceptions.Timeout:
        logging.error("JIRA API request timeout")
        return jsonify({"error": "Request to JIRA API timed out"}), 500
    except requests.exceptions.RequestException as e:
        logging.error(f"JIRA API request failed: {str(e)}")
        return jsonify({"error": f"Request to JIRA API failed: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Test endpoint to verify API connectivity"""
    try:
        data = request.get_json()
        return jsonify({
            "message": "Test successful",
            "received_data": data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)