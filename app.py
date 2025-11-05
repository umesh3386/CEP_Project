import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request, render_template

# NO MORE FLASK_MARKDOWN
# from flask_markdown import Markdown  <-- GONE

# Load environment variables from .env
load_dotenv()

# --- Configure Google Generative AI ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Model Configuration ---
vis_model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# --- Flask App Setup ---
app = Flask(__name__)
# Markdown(app)  <-- GONE. No more crashes.

# --- Function to generate content from image + prompt ---
def gen_image(prompt, image):
    response = vis_model.generate_content([prompt, image])
    return response.text

# --- Function to validate the text ---
def validate(validation_prompt):
    vresponse = vis_model.generate_content(validation_prompt)
    return vresponse.text

# --- Main Page Route ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image_prompt = '''
                - Generate a very detailed medical description for the given image.
                - Identify and describe any relevant medical conditions, anomalies, or abnormalities present in the image.
                - Additionally, provide insights into any potential treatments or recommended actions based on the observed medical features.
                - Please ensure the generated content is accurate and clinically relevant.
                - Please don't provide false and misleading information.
                '''
        
        uploaded_file = request.files['file']
        if not uploaded_file:
            return render_template('index.html', response_text="No file uploaded. Please choose an image.")

        image = Image.open(uploaded_file)
        
        # 1. Generate the main description
        response_text = gen_image(image_prompt, image)

        # 2. Validate the description
        validation_prompt = f"Check if the following text is related to the medical field: '{response_text}'. Just Reply with 'Yes' or 'No'."
        vans = validate(validation_prompt)

        # .strip() removes whitespace/newlines just in case
        if "Yes" in vans.strip():
            # We just pass the raw response_text.
            return render_template('index.html', response_text=response_text)
        else:
            return render_template('index.html', response_text="This does not appear to be a medical image. Please try another.")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)