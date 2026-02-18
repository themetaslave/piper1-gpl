from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
import tempfile
import base64
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configuration
PIPER_MODEL = "/app/models/fr_FR-siwis-medium.onnx"
PORT = int(os.environ.get('PORT', 5000))

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({
        'status': 'ok',
        'service': 'Piper TTS',
        'model': 'fr_FR-siwis-medium'
    })

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """Convertit du texte en audio"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 10000:
            return jsonify({'error': 'Text too long (max 10000 characters)'}), 400
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as text_file:
            text_file.write(text)
            text_file_path = text_file.name
        
        output_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        output_file_path = output_file.name
        output_file.close()
        
        try:
            cmd = [
                'piper',
                '--model', PIPER_MODEL,
                '--output_file', output_file_path
            ]
            
            with open(text_file_path, 'r') as f:
                subprocess.run(cmd, stdin=f, check=True, capture_output=True)
            
            with open(output_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return jsonify({
                'success': True,
                'audio': audio_base64,
                'format': 'wav',
                'size': len(audio_data)
            })
        
        finally:
            if os.path.exists(text_file_path):
                os.unlink(text_file_path)
            if os.path.exists(output_file_path):
                os.unlink(output_file_path)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': 'Synthesis failed',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    print(f"Starting Piper TTS Service on port {PORT}")
    print(f"Using model: {PIPER_MODEL}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
