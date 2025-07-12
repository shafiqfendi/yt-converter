import os
import yt_dlp
from flask import Flask, request, send_file, jsonify, render_template
from threading import Lock

# --- Configuration ---
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# --- Flask App Initialization ---
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
download_lock = Lock()

# --- yt-dlp Options ---
YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
}

# --- Route Definitions ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    with download_lock:
        try:
            with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                sanitized_title = "".join([c for c in info_dict.get('title', 'video') if c.isalnum() or c in (' ', '-')]).rstrip()
                output_template = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{sanitized_title}.mp3")
                
                ydl.params['outtmpl'] = output_template
                ydl.download([url])

            return send_file(
                output_template,
                as_attachment=True,
                download_name=f"{sanitized_title}.mp3"
            )
        except yt_dlp.utils.DownloadError as e:
            return jsonify({'error': f"Failed to download or convert video. Please check the URL."}), 500
        except Exception as e:
            return jsonify({'error': f'An unexpected error occurred.'}), 500
        finally:
            if 'output_template' in locals() and os.path.exists(output_template):
                try:
                    os.remove(output_template)
                except OSError as e:
                    print(f"Error deleting file {output_template}: {e}")

# This part is for local testing and will not be used by Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)