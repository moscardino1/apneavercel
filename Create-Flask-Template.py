import os

def create_flask_project():
    # Directories to create
    folder_name = os.path.basename(os.getcwd())

    dirs = [
        os.path.join(folder_name, 'static', 'css'),
        os.path.join(folder_name, 'static', 'js'),
        os.path.join(folder_name, 'templates'),
        os.path.join(folder_name, 'venv')
    ]

    # Create directories
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

    # File contents
    app_py_content = '''from flask import Flask, render_template, jsonify, request, abort
import os
import logging
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime
import qrcode
import base64
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/donate')
def donate():
    USDT_ADDRESS = "0xDC92534Be92780c87f232CD525D99e26892E15f7"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(USDT_ADDRESS)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return render_template('donate.html', usdt_address=USDT_ADDRESS, qr_image=qr_image)

@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

@app.after_request
def log_response_info(response):
    logger.debug('Response Status: %s', response.status)
    logger.debug('Response Headers: %s', response.headers)
    return response

if __name__ == '__main__':
    logger.info("Starting application")
    app.run(debug=True)
'''

    requirements_txt_content = '''Flask
python-dotenv
qrcode
requests
pillow
'''

    info_content= f'''start
cd {folder_name}
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

cd {folder_name}
source venv/bin/activate
python app.py

to dev test
    vercel dev

to deploy
    vercel deploy

to prod:
    vercel --prod 

python app.py
pip freeze > requirements.txt

Prompt
I am creating a flask webapp to be deployed on vercel, structured like the following.  
    static
        css
            styles.css
        js
            main.js
    templates
        index.html
    app.py

Please create ......
based on a  modern, responsive css which emobodies creativity and usability. The webapp should feature:
1. Clean and Intuitive Layout: Use a grid-based structure for easy navigation and organization of content.
2. High-Quality Visuals: Incorporate striking images and animations that enhance the user experience without overwhelming the content.
3. Bold Typography: Utilize a mix of bold headlines and readable body text to create a clear hierarchy.
4. Interactive Elements: Include hover effects, transitions, and animations to engage users and provide feedback.
5. Color Palette: Choose a harmonious color scheme that aligns with the brand identity while ensuring good contrast for readability.
6. Responsive Design: Ensure the layout adapts seamlessly across devices, providing a great experience on both desktop and mobile.
7. Unique Features: Integrate innovative elements such as parallax scrolling, micro-interactions, or custom illustrations to differentiate the design.
8. User-Centric Navigation: Design an intuitive navigation system that allows users to easily find information and explore the site.
Focus on creating a visually appealing and functional website that can stand out in the competitive landscape of award-winning designs."I just need you to help me change index.html, style.css, main.js to match the style in a website like https://www.awwwards.com.
'''

    vercel_json_content = '''{
    "version": 2,
    "builds": [
      {
        "src": "app.py",
        "use": "@vercel/python"
      }
    ],
    "routes": [
      {
        "src": "/(.*)",
        "dest": "app.py"
      }
    ]
    }'''

    gitignore_content = '''venv/
__pycache__/
instance/
.webassets-cache
.env
'''

    env_content = '''env_var = test '''
    index_html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>foldername</title>
    <link rel="icon" href="image" type="image/svg">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">

    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="/contact" class="footer-link">Contact</a>
                <a href="/info" class="footer-link">How It Works</a>
                <a href="/donate" class="footer-link">Support Us</a>
            </div>
        </div>
    </footer>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''

    contact_html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold text-center mb-4">Contact Us</h1>
        <div class="text-center mb-4">
            <p>If you have any questions or feedback, feel free to reach out to us!</p>
            <p>Email: <a href="mailto:cronispherenews@gmail.com" class="text-blue-500">cronispherenews@gmail.com</a></p>
        </div>
    </div>
</body>
</html>
'''

    donate_html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Donate USDT</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container mx-auto px-4 py-8 max-w-2xl">
        <h1 class="text-3xl font-bold mb-4 text-center">Support Us with USDT 💵</h1>
        <p class="mb-4 text-center">If you appreciate our work and would like to support us, you can donate Tether (USDT) to the address below:</p>
        <div class="bg-white shadow-md rounded-lg p-6 mb-4">
            <h2 class="text-lg font-semibold text-center">USDT Address:</h2>
            <p class="text-gray-600 break-all text-center">{{ usdt_address }}</p>
        </div>
        <h2 class="text-lg font-semibold mb-2 text-center">Scan to Donate:</h2>
        <img src="data:image/png;base64,{{ qr_image }}" alt="QR Code" class="mb-4 mx-auto" />
    </div>
</body>
</html>
'''

    info_html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>How It Works</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold text-center mb-4">How It Works</h1>
        <div class="mb-4">
            <h2 class="text-xl font-semibold">Overview</h2>
            <p>description of the app</p>
        </div>
        <div class="mb-4">
            <h2 class="text-xl font-semibold">APIs Used</h2>
            <ul class="list-disc pl-5">
                <li><strong> API:</strong> Used to fetch data.</li>
            </ul>
        </div>
        <div class="mb-4">
            <h2 class="text-xl font-semibold">Legal Considerations</h2>
            <p>All API usage complies with the respective terms of service.</p>
        </div>
    </div>
</body>
</html>
'''

    style_css_content = '''/* style.css */
:root {
    --primary-color: #2D3436;
    --accent-color: #6C5CE7;
    --text-color: #2D3436;
    --background-color: #FFFFFF;
    --overlay-color: rgba(45, 52, 54, 0.8);
    --spacing-unit: 1rem;
}
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
    overflow-x: hidden;
}

.footer {
    background: white;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding: 2rem;
    margin-top: 4rem;
}

.footer-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: center;
}

.footer-links {
    display: flex;
    gap: 2rem;
}

.footer-link {
    color: var(--text-color);
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer-link:hover {
    color: var(--accent-color);
}
'''

    main_js_content = '''// main.js
console.log("JavaScript loaded");
'''

    readme_content = '''# Project Title

This is a basic Flask project to demonstrate project structure.

## Features
- Home page
- Contact page
- Donate page with USDT QR code
- Information page
## License

This project is licensed under the MIT License.
'''

    # Write content to files
    with open(os.path.join(folder_name, 'app.py'), 'w') as f:
        f.write(app_py_content)

    with open(os.path.join(folder_name, 'requirements.txt'), 'w') as f:
        f.write(requirements_txt_content)

    with open(os.path.join(folder_name, 'vercel.json'), 'w') as f:
        f.write(vercel_json_content)
    with open(os.path.join(folder_name, 'info'), 'w') as f:
        f.write(info_content)
    with open(os.path.join(folder_name, '.gitignore'), 'w') as f:
        f.write(gitignore_content)
    with open(os.path.join(folder_name, '.env'), 'w') as f:
        f.write(env_content)
    with open(os.path.join(folder_name, 'README.md'), 'w') as f:
        f.write(readme_content)

    with open(os.path.join(folder_name, 'templates', 'index.html'), 'w') as f:
        f.write(index_html_content)

    with open(os.path.join(folder_name, 'templates', 'contact.html'), 'w') as f:
        f.write(contact_html_content)

    with open(os.path.join(folder_name, 'templates', 'donate.html'), 'w') as f:
        f.write(donate_html_content)

    with open(os.path.join(folder_name, 'templates', 'info.html'), 'w') as f:
        f.write(info_html_content)

    with open(os.path.join(folder_name, 'static', 'css', 'style.css'), 'w') as f:
        f.write(style_css_content)

    with open(os.path.join(folder_name, 'static', 'js', 'main.js'), 'w') as f:
        f.write(main_js_content)

    print(f"Flask project created in {folder_name}")

# Example usage
create_flask_project()
