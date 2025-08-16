👶 AI Baby Image Generator
This project is a Flask-based web application that uses Google's Imagen 4 AI model to generate a photorealistic image of a baby by blending the features of two parent images.

✨ Features
🤖 AI-Powered Image Generation: Leverages Google's Imagen 4 model to create a unique baby image.

🧬 Genetic Feature Blending: Intelligently combines facial traits such as eye color, hair texture, nose shape, and skin tone from both parents.

🚻 Gender Specification: Option to specify the baby’s gender (boy or girl).

🌐 Simple REST API: Exposes a /generate-baby endpoint that accepts parent images and returns the generated baby image.

📋 Prerequisites
Python 3.6+

Flask

Requests

Google Cloud SDK

You will also need:

A Google Cloud Platform (GCP) project

AI Platform API enabled

Authentication configured via gcloud CLI (local) or a Service Account (production)

⚙️ Installation
1. Clone the repository
git clone <your-repository-url>
cd <your-repository-name>

2. Create and activate a virtual environment
python -m venv venv
```bash
# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Configure Google Cloud SDK
# Initialize gcloud
gcloud init

# Log in to your account
gcloud auth login

# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

🔧 Configuration
Open the generate_baby.py file and update the following variables with your GCP project details:

PROJECT_ID = "your-gcp-project-id"
LOCATION   = "us-central1"  # or your chosen region
MODEL_ID   = "imagen-4.0-fast-generate-preview-06-06" # Or your preferred model

🚀 Usage
1. Run the Flask app
python generate_baby.py

The application will start and be accessible at http://0.0.0.0:5000.

2. Generate a baby image
Send a POST request to the /generate-baby endpoint using a tool like curl or Postman. The generated image will be saved to the specified output file.

curl -X POST \
  -F "father_image=@/path/to/father.jpg" \
  -F "mother_image=@/path/to/mother.jpg" \
  -F "gender=girl" \
  [http://127.0.0.1:5000/generate-baby](http://127.0.0.1:5000/generate-baby) --output generated_baby.png

🔒 Security
IMPORTANT: Do not commit your service account JSON file to your Git repository, especially if it's public. This file contains sensitive credentials.

It is highly recommended to add the JSON file name to your .gitignore file to prevent it from being tracked by Git. For production environments, use a secure method for handling credentials, such as setting them as environment variables or using a secret management service.

📂 Project Structure
.
├── generate_baby.py     # Flask app with baby image generation logic
├── requirements.txt     # Project dependencies
├── LICENSE              # License file
├── .gitignore           # Git ignored files (include your GCP keys here!)
└── README.md            # Project documentation

🧰 Tech Stack

Flask – Web framework

Google Imagen 4 – AI model for image generation

Requests – For API requests

Google Cloud SDK – Authentication & project configuration

🔒 Security

❌ Do not commit your service account JSON file to GitHub.

Add it to .gitignore:

*.json


For production: use environment variables or a secret manager to securely manage credentials.

📜 License

This project is licensed under the MIT License.

🙋 Maintainer

Name: Shikhar Jaglan

GitHub: @Shikhar-glich