"""
Flask API Server for Hyperchaotic Cryptography System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from chaotic_crypto import ChaoticCrypto
from image_analysis import ImageAnalyzer
import numpy as np
from PIL import Image
import io
import base64
import json

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

@app.before_request
def before_request():
    print(f"Request Method: {request.method}")
    print(f"Request Path: {request.path}")
    print(f"Request Headers: {dict(request.headers)}")

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    print(f"Response Status: {response.status}")
    print(f"Response Headers: {dict(response.headers)}")
    return response

# Global crypto instance and analyzer
crypto_instance = None
analyzer = ImageAnalyzer()


@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize the crypto system with a seed"""
    global crypto_instance

    data = request.json
    seed = data.get('seed', 'default_seed')
    initial_conditions = data.get('initial_conditions', None)

    try:
        crypto_instance = ChaoticCrypto(
            seed=seed,
            initial_conditions=initial_conditions
        )
        
        # Get system information
        system_info = crypto_instance.get_system_info()
        
        # Get first few bits of each bitstream for visualization
        bitstreams = {
            'system1': crypto_instance.bitstream1[:100].tolist(),
            'system2': crypto_instance.bitstream2[:100].tolist(),
            'system3': crypto_instance.bitstream3[:100].tolist(),
        }
        
        # Get keys (first 32 bytes for display)
        keys = {
            'key1': crypto_instance.key1[:32].tolist(),
            'key2': crypto_instance.key2[:32].tolist(),
            'key3': crypto_instance.key3[:32].tolist(),
        }
        
        # Get S-boxes (first 32 values for display)
        sboxes = {
            'sbox1': crypto_instance.sbox1[:32].tolist(),
            'sbox2': crypto_instance.sbox2[:32].tolist(),
            'sbox3': crypto_instance.sbox3[:32].tolist(),
        }
        
        return jsonify({
            'success': True,
            'systems': system_info,
            'bitstreams': bitstreams,
            'keys': keys,
            'sboxes': sboxes
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    """Encrypt an image"""
    global crypto_instance
    
    if crypto_instance is None:
        return jsonify({
            'success': False,
            'error': 'Crypto system not initialized'
        }), 400
    
    try:
        # Get image from request
        data = request.json
        image_data = data.get('image')
        rounds = data.get('rounds', 3)
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Encrypt
        encrypted = crypto_instance.encrypt_image(img_array, rounds=rounds)
        
        # Convert encrypted array back to image
        encrypted_image = Image.fromarray(encrypted.astype(np.uint8))
        
        # Convert to base64
        buffer = io.BytesIO()
        encrypted_image.save(buffer, format='PNG')
        encrypted_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'encrypted_image': f'data:image/png;base64,{encrypted_base64}',
            'original_shape': img_array.shape
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    """Decrypt an image"""
    global crypto_instance
    
    if crypto_instance is None:
        return jsonify({
            'success': False,
            'error': 'Crypto system not initialized'
        }), 400
    
    try:
        # Get encrypted image from request
        data = request.json
        encrypted_data = data.get('encrypted_image')
        original_shape = tuple(data.get('original_shape'))
        rounds = data.get('rounds', 3)
        
        # Decode base64 image
        image_bytes = base64.b64decode(encrypted_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        encrypted_array = np.array(image)
        
        # Decrypt
        decrypted = crypto_instance.decrypt_image(encrypted_array, original_shape, rounds=rounds)

        # Convert decrypted array back to image
        decrypted_image = Image.fromarray(decrypted.astype(np.uint8))

        # Convert to base64
        buffer = io.BytesIO()
        decrypted_image.save(buffer, format='PNG')
        decrypted_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            'success': True,
            'decrypted_image': f'data:image/png;base64,{decrypted_base64}'
        })

    except Exception as e:
        import traceback
        print(f"Decryption error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/visualize', methods=['GET'])
def visualize():
    """Get visualization data for the chaotic systems"""
    global crypto_instance

    if crypto_instance is None:
        return jsonify({
            'success': False,
            'error': 'Crypto system not initialized'
        }), 400

    try:
        # Get trajectories (downsample for performance)
        step = 10

        trajectories = {
            'system1': {
                'x': crypto_instance.system1.solution[::step, 0].tolist(),
                'y': crypto_instance.system1.solution[::step, 1].tolist(),
                'z': crypto_instance.system1.solution[::step, 2].tolist(),
                'w': crypto_instance.system1.solution[::step, 3].tolist(),
            },
            'system2': {
                'x': crypto_instance.system2.solution[::step, 0].tolist(),
                'y': crypto_instance.system2.solution[::step, 1].tolist(),
                'z': crypto_instance.system2.solution[::step, 2].tolist(),
                'w': crypto_instance.system2.solution[::step, 3].tolist(),
            },
            'system3': {
                'x': crypto_instance.system3.solution[::step, 0].tolist(),
                'y': crypto_instance.system3.solution[::step, 1].tolist(),
                'z': crypto_instance.system3.solution[::step, 2].tolist(),
                'w': crypto_instance.system3.solution[::step, 3].tolist(),
            }
        }

        return jsonify({
            'success': True,
            'trajectories': trajectories
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Perform comprehensive analysis on encrypted images"""
    global crypto_instance, analyzer

    if crypto_instance is None:
        return jsonify({
            'success': False,
            'error': 'Crypto system not initialized'
        }), 400

    try:
        # Get images from request
        data = request.json
        original_data = data.get('original_image')
        encrypted_data = data.get('encrypted_image')
        decrypted_data = data.get('decrypted_image')
        original_shape = tuple(data.get('original_shape'))
        rounds = data.get('rounds', 3)

        # Decode images
        print("Decoding images...")
        original_bytes = base64.b64decode(original_data.split(',')[1])
        original_image = Image.open(io.BytesIO(original_bytes))
        if original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
        original_array = np.array(original_image)

        encrypted_bytes = base64.b64decode(encrypted_data.split(',')[1])
        encrypted_image = Image.open(io.BytesIO(encrypted_bytes))
        if encrypted_image.mode != 'RGB':
            encrypted_image = encrypted_image.convert('RGB')
        encrypted_array = np.array(encrypted_image)

        decrypted_bytes = base64.b64decode(decrypted_data.split(',')[1])
        decrypted_image = Image.open(io.BytesIO(decrypted_bytes))
        if decrypted_image.mode != 'RGB':
            decrypted_image = decrypted_image.convert('RGB')
        decrypted_array = np.array(decrypted_image)

        print("Running comprehensive analysis...")
        # Perform comprehensive analysis
        report = analyzer.comprehensive_analysis(
            original_array,
            encrypted_array,
            decrypted_array,
            crypto_instance,
            original_shape,
            rounds
        )

        print("Analysis complete!")
        return jsonify({
            'success': True,
            'analysis': report
        })

    except Exception as e:
        import traceback
        print(f"Analysis error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
