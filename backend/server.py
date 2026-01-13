"""
Flask API Server for Hyperchaotic Cryptography System
"""

from flask import Flask, request, jsonify, send_from_directory

from flask_cors import CORS
from chaotic_crypto import ChaoticCrypto
from image_analysis import ImageAnalyzer
import numpy as np
from PIL import Image
import io
import base64
import json
import plotly.graph_objects as go
import plotly.io as pio
import os

app = Flask(
    __name__,
    static_folder="../frontend/build",
    static_url_path=""
)

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
    if app.debug:
        print(f"Request Method: {request.method}")
        print(f"Request Path: {request.path}")
        print(f"Request Headers: {dict(request.headers)}")



# Global crypto instance and analyzer
crypto_instance = None
analyzer = ImageAnalyzer()


@app.route("/api/test")
def test():
    return {"status": "ok", "success":True}

@app.route("/")
@app.route("/<path:path>")
def serve_react(path=""):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

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
        
        # Get keys (first 32 bytes for display, plus total length info)
        keys = {
            'key1': list(crypto_instance.key1[:32]),
            'key2': list(crypto_instance.key2[:32]),
            'key3': list(crypto_instance.key3[:32]),
            'key1_length': len(crypto_instance.key1),
            'key2_length': len(crypto_instance.key2),
            'key3_length': len(crypto_instance.key3),
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
    """Generate 3D visualization plots for the chaotic systems"""
    global crypto_instance

    if crypto_instance is None:
        return jsonify({
            'success': False,
            'error': 'Crypto system not initialized'
        }), 400

    try:
        print("[+] Generating 3D visualization plots...")

        # Helper function to generate an interactive 3D plot with Plotly
        def generate_3d_plot(solution, coord_indices, title, color):
            """
            Generate an interactive 3D Plotly plot and return as HTML
            coord_indices: tuple of 3 integers (0-3) for x,y,z,w coordinates
            """
            # Downsample for performance
            step = 10
            data = solution[::step]

            # Get the three coordinates
            coord1 = data[:, coord_indices[0]]
            coord2 = data[:, coord_indices[1]]
            coord3 = data[:, coord_indices[2]]

            # Create the 3D scatter/line plot
            labels = ['X', 'Y', 'Z', 'W']

            fig = go.Figure(data=[go.Scatter3d(
                x=coord1,
                y=coord2,
                z=coord3,
                mode='lines',
                line=dict(
                    color=color,
                    width=2
                ),
                name=title,
                hovertemplate=f'{labels[coord_indices[0]]}: %{{x:.2f}}<br>' +
                              f'{labels[coord_indices[1]]}: %{{y:.2f}}<br>' +
                              f'{labels[coord_indices[2]]}: %{{z:.2f}}<extra></extra>'
            )])

            # Update layout with dark cyberpunk theme
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=16, color=color, family='monospace')
                ),
                scene=dict(
                    xaxis=dict(
                        title=dict(text=labels[coord_indices[0]], font=dict(color=color)),
                        backgroundcolor='#0a0a0a',
                        gridcolor='#333333',
                        showbackground=True
                    ),
                    yaxis=dict(
                        title=dict(text=labels[coord_indices[1]], font=dict(color=color)),
                        backgroundcolor='#0a0a0a',
                        gridcolor='#333333',
                        showbackground=True
                    ),
                    zaxis=dict(
                        title=dict(text=labels[coord_indices[2]], font=dict(color=color)),
                        backgroundcolor='#0a0a0a',
                        gridcolor='#333333',
                        showbackground=True
                    ),
                    bgcolor='#0a0a0a'
                ),
                paper_bgcolor='#0a0a0a',
                plot_bgcolor='#0a0a0a',
                font=dict(color='#ffffff', family='monospace'),
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
                height=500
            )

            # Return as HTML with embedded JavaScript for interactivity
            html_str = pio.to_html(
                fig,
                include_plotlyjs='cdn',
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['toImage'],
                    'modeBarButtonsToAdd': ['downloadSVG']
                }
            )

            return html_str

        # Generate plots for Rössler system
        print("    ↳ Generating Rössler plots...")
        rossler_xyz = generate_3d_plot(
            crypto_instance.system1.solution,
            (0, 1, 2),
            'Rössler Hyperchaos (X, Y, Z)',
            '#00ffff'
        )
        rossler_xyw = generate_3d_plot(
            crypto_instance.system1.solution,
            (0, 1, 3),
            'Rössler Hyperchaos (X, Y, W)',
            '#00ffff'
        )
        rossler_xzw = generate_3d_plot(
            crypto_instance.system1.solution,
            (0, 2, 3),
            'Rössler Hyperchaos (X, Z, W)',
            '#00ffff'
        )

        # Generate plots for Chen system
        print("    ↳ Generating Chen plots...")
        chen_xyz = generate_3d_plot(
            crypto_instance.system2.solution,
            (0, 1, 2),
            'Chen Hyperchaos (X, Y, Z)',
            '#ff00ff'
        )
        chen_xyw = generate_3d_plot(
            crypto_instance.system2.solution,
            (0, 1, 3),
            'Chen Hyperchaos (X, Y, W)',
            '#ff00ff'
        )
        chen_xzw = generate_3d_plot(
            crypto_instance.system2.solution,
            (0, 2, 3),
            'Chen Hyperchaos (X, Z, W)',
            '#ff00ff'
        )

        # Generate plots for Lorenz system
        print("    ↳ Generating Lorenz plots...")
        lorenz_xyz = generate_3d_plot(
            crypto_instance.system3.solution,
            (0, 1, 2),
            'Lorenz Hyperchaos (X, Y, Z)',
            '#ffff00'
        )
        lorenz_xyw = generate_3d_plot(
            crypto_instance.system3.solution,
            (0, 1, 3),
            'Lorenz Hyperchaos (X, Y, W)',
            '#ffff00'
        )
        lorenz_xzw = generate_3d_plot(
            crypto_instance.system3.solution,
            (0, 2, 3),
            'Lorenz Hyperchaos (X, Z, W)',
            '#ffff00'
        )

        print("[+] All plots generated successfully")

        return jsonify({
            'success': True,
            'plots': {
                'rossler': {
                    'xyz': rossler_xyz,
                    'xyw': rossler_xyw,
                    'xzw': rossler_xzw
                },
                'chen': {
                    'xyz': chen_xyz,
                    'xyw': chen_xyw,
                    'xzw': chen_xzw
                },
                'lorenz': {
                    'xyz': lorenz_xyz,
                    'xyw': lorenz_xyw,
                    'xzw': lorenz_xzw
                }
            }
        })

    except Exception as e:
        import traceback
        print(f"Visualization error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chaos-analysis', methods=['GET'])
def chaos_analysis():
    """Compute Lyapunov exponents to prove hyperchaotic behavior"""
    global crypto_instance

    if crypto_instance is None:
        return jsonify({
            'success': False,
            'error': 'Crypto system not initialized'
        }), 400

    try:
        print("[+] Computing chaos analysis...")

        # Compute Lyapunov exponents for all three systems
        lyap1 = crypto_instance.system1.compute_lyapunov_spectrum(n_iterations=5000, dt=0.01)
        lyap2 = crypto_instance.system2.compute_lyapunov_spectrum(n_iterations=5000, dt=0.01)
        lyap3 = crypto_instance.system3.compute_lyapunov_spectrum(n_iterations=5000, dt=0.01)


        print("[+] Chaos analysis complete")

        return jsonify({
            'success': True,
            'lyapunov': {
                'rossler': {
                    'exponents': lyap1.tolist(),
                    'lambda1': float(lyap1[0]),
                    'lambda2': float(lyap1[1]),
                    'is_hyperchaotic': bool(lyap1[0] > 0 and lyap1[1] > 0)
                },
                'chen': {
                    'exponents': lyap2.tolist(),
                    'lambda1': float(lyap2[0]),
                    'lambda2': float(lyap2[1]),
                    'is_hyperchaotic': bool(lyap2[0] > 0 and lyap2[1] > 0)
                },
                'lorenz': {
                    'exponents': lyap3.tolist(),
                    'lambda1': float(lyap3[0]),
                    'lambda2': float(lyap3[1]),
                    'is_hyperchaotic': bool(lyap3[0] > 0 and lyap3[1] > 0)
                }
            },
         
        })

    except Exception as e:
        import traceback
        print(f"Chaos analysis error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bifurcation-diagrams', methods=['GET'])
def get_bifurcation_diagrams():
    try:
        diagrams = {}
        for i, system in enumerate(crypto_instance.systems):
            diagrams[f"system{i+1}"] = system.compute_bifurcation_diagram(param_index=0)
        
        return jsonify({
            "success": True,
            "bifurcation_diagrams": diagrams
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
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
