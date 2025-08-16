from flask import Flask, request, jsonify, send_file
import requests
import base64
import json
import os
import tempfile
import google.auth
import google.auth.transport.requests

# --- Project Configuration ---
# Load configuration from environment variables for security.
# IMPORTANT: Set these variables in your environment before running the app.
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
MODEL_ID = os.environ.get("GCP_MODEL_ID", "imagen-4.0-fast-generate-preview-06-06")

# Validate that the Project ID is set
if not PROJECT_ID:
    raise ValueError("🔴 CRITICAL: The GCP_PROJECT_ID environment variable is not set.")

app = Flask(__name__)

def get_auth_token():
    """
    Get authentication token using the google-auth library.
    This method is secure and supports both local development (via gcloud)
    and production environments (via service accounts).
    """
    try:
        # Get the default credentials from the environment
        credentials, project_id = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        # Refresh the credentials to get an access token
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials.token
    except google.auth.exceptions.DefaultCredentialsError:
        app.logger.error("❌ Authentication failed. Could not find default credentials.")
        app.logger.error("➡️ Please run 'gcloud auth application-default login' for local development,")
        app.logger.error("   or set the GOOGLE_APPLICATION_CREDENTIALS environment variable for production.")
        return None
    except Exception as e:
        app.logger.error(f"❌ An unexpected error occurred during authentication: {e}")
        return None


def blend_parent_images(father_bytes, mother_bytes, gender):
    """Generate baby image with Imagen 4 API using a detailed prompt."""
    auth_token = get_auth_token()
    if not auth_token:
        return None, "Authentication failed. Could not get auth token."

    endpoint_url = (
        f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/"
        f"locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predict"
    )

    # --- Enhanced Prompt ---
    text_prompt = f"""
        A photorealistic, high-definition image of a 5-month-old Indian {gender} baby.
        The baby's appearance must be a clear and natural genetic blend of the two Indian parents
        in the provided reference images.

        Pay close attention to blending the following features from the parents:
        - **Eye color and shape:** Combine the eye characteristics of both parents.
        - **Hair color and texture:** Create a realistic mix of the parents' hair.
        - **Nose shape:** The baby's nose should be a believable combination of the parents' noses.
        - **Face shape and jawline:** Blend the overall facial structure, including cheeks and chin.
        - **Skin tone:** The baby's skin tone should be an authentic and natural blend of the parents' complexions.

        The final image must be indistinguishable from a real photograph, with realistic skin texture,
        subtle lighting, and intricate details. Avoid all cartoonish, artistic, or CGI effects.
        The baby should have a neutral or slightly happy expression and be looking towards the camera.
    """

    request_body = {
        "instances": [
            {
                "prompt": text_prompt,
                "images": [
                    {"bytesBase64Encoded": base64.b64encode(father_bytes).decode("utf-8")},
                    {"bytesBase64Encoded": base64.b64encode(mother_bytes).decode("utf-8")},
                ]
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "mimeType": "image/png"
        }
    }

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    try:
        response = requests.post(endpoint_url, headers=headers, data=json.dumps(request_body), timeout=300)
        response.raise_for_status()

        response_json = response.json()
        if "predictions" in response_json and response_json["predictions"]:
            image_b64 = response_json["predictions"][0].get("bytesBase64Encoded")
            if image_b64:
                return base64.b64decode(image_b64), None
            else:
                return None, "API response did not contain image data."
        else:
            return None, f"API Error: No predictions found in response. Full response: {response.text}"

    except requests.exceptions.HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err} - Response: {response.text}"
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"


@app.route("/generate-baby", methods=["POST"])
def generate_baby_endpoint():
    """API endpoint to generate baby image."""
    try:
        father_file = request.files.get("father_image")
        mother_file = request.files.get("mother_image")
        gender = request.form.get("gender")

        if not father_file or not mother_file or not gender:
            return jsonify({"error": "Please provide 'father_image', 'mother_image', and 'gender'"}), 400
        
        if gender.lower() not in ['male', 'female', 'boy', 'girl']:
             return jsonify({"error": "Gender must be one of 'male', 'female', 'boy', or 'girl'"}), 400

        father_bytes = father_file.read()
        mother_bytes = mother_file.read()

        image_bytes, error = blend_parent_images(father_bytes, mother_bytes, gender)

        if error:
            app.logger.error(f"Error from blend_parent_images: {error}")
            return jsonify({"error": f"Image generation failed. Details: {error}"}), 500

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(image_bytes)
            temp_filename = temp_file.name
        
        return send_file(temp_filename, mimetype="image/png")

    except Exception as e:
        app.logger.error(f"An error occurred in /generate-baby: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
