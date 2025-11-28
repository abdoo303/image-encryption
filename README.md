# Hyperchaotic Cryptography System

A sophisticated image encryption system using three different hyperchaotic dynamical systems. This project demonstrates the application of chaos theory to cryptography, featuring a Python backend and a stunning React frontend.

## 🌌 Overview

This system implements:

1. **Three Hyperchaotic Systems**: Rössler, Chen, and 4D Lorenz systems
2. **Bit-stream Generation**: Converting chaotic solutions to binary streams
3. **Encryption Key Generation**: Deriving cryptographic keys from chaos
4. **S-box Construction**: Creating substitution boxes for diffusion
5. **Image Encryption**: Multi-round encryption with successive key and S-box applications

## 📊 Mathematical Background

### Hyperchaotic Systems Implemented

#### 1. Rössler Hyperchaotic System (4D)

```
dx/dt = -y - z
dy/dt = x + a*y + w
dz/dt = b + x*z
dw/dt = -c*z + d*w
```

#### 2. Chen Hyperchaotic System (4D)

```
dx/dt = a*(y - x) + w
dy/dt = d*x - x*z + c*y
dz/dt = x*y - b*z
dw/dt = x*z + r*w
```

#### 3. Hyperchaotic Lorenz System (4D)

```
dx/dt = σ*(y - x) + w
dy/dt = r*x - y - x*z
dz/dt = x*y - b*z
dw/dt = -x*z + k*w
```

### Encryption Algorithm

For each round:

1. **XOR Operation**: Plaintext ⊕ Key → Intermediate
2. **S-box Substitution**: S(Intermediate) → Ciphertext

The process is repeated for multiple rounds, alternating between the three systems.

## 🚀 Installation

### Backend (Python)

1. **Install Python dependencies**:

```bash
pip install numpy scipy Pillow flask flask-cors
```

2. **Run the Flask server**:

```bash
python server.py
```

The server will start on `http://localhost:5001`

### Frontend (React)

1. **Create a new React project** (if you haven't already):

2. **Install dependencies**:

```bash
npm install lucide-react
```

3. **Replace `src/App.js`** with the contents of `chaos-crypto.jsx`

4. **Start the development server**:

```bash
npm start
```

The app will open at `http://localhost:3000`

## 💻 Usage

### Python Library

```python
from chaotic_crypto import ChaoticCrypto
import numpy as np

# Initialize with a seed
crypto = ChaoticCrypto(seed="my_secret_seed")

# Create or load an image
image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

# Encrypt
encrypted = crypto.encrypt_image(image, rounds=3)

# Decrypt
decrypted = crypto.decrypt_image(encrypted, image.shape, rounds=3)

# Verify
assert np.array_equal(image, decrypted)
```

### Web Interface

1. **Start the Flask server**: `python server.py`
2. **Start the React app**: `npm start`
3. **Initialize the system**:
    - Enter a seed phrase (this determines the chaotic systems' behavior)
    - Click "INITIALIZE SYSTEMS"
4. **Encrypt an image**:
    - Upload an image
    - Adjust encryption rounds (1-10)
    - Click "ENCRYPT"
5. **View the results**:
    - See the encrypted image (should look like random noise)
    - Click "DECRYPT" to recover the original
6. **Explore the systems**:
    - View phase space trajectories
    - Examine system parameters
    - Inspect bit-streams, keys, and S-boxes

## 🎨 Features

### Backend

-   ✅ Three different hyperchaotic systems solved numerically
-   ✅ Bit-stream extraction using threshold method
-   ✅ Cryptographic key generation (256-bit keys)
-   ✅ S-box generation using Fisher-Yates shuffle
-   ✅ Multi-round encryption/decryption
-   ✅ RESTful API with Flask

### Frontend

-   ✅ Retro-futuristic cyberpunk aesthetic
-   ✅ Real-time image encryption/decryption
-   ✅ Phase space trajectory visualization
-   ✅ System parameters display
-   ✅ Bit-stream, key, and S-box inspection
-   ✅ Adjustable encryption rounds
-   ✅ Responsive design with animations

## 📁 Project Structure

```
.
├── chaotic_crypto.py      # Core encryption library
├── server.py              # Flask API server
├── chaos-crypto.jsx       # React frontend
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔬 API Endpoints

### POST `/api/initialize`

Initialize the crypto system with a seed.

**Request:**

```json
{
    "seed": "my_secret_seed"
}
```

**Response:**

```json
{
  "success": true,
  "systems": { ... },
  "bitstreams": { ... },
  "keys": { ... },
  "sboxes": { ... }
}
```

### POST `/api/encrypt`

Encrypt an image.

**Request:**

```json
{
    "image": "data:image/png;base64,...",
    "rounds": 3
}
```

**Response:**

```json
{
    "success": true,
    "encrypted_image": "data:image/png;base64,...",
    "original_shape": [100, 100, 3]
}
```

### POST `/api/decrypt`

Decrypt an encrypted image.

### GET `/api/visualize`

Get trajectory data for visualization.

## 🔐 Security Notes

This is an **educational implementation** demonstrating the principles of chaotic cryptography. For production use:

-   Use established cryptographic libraries
-   Implement proper key management
-   Add authentication and authorization
-   Use secure random number generation
-   Consider side-channel attacks
-   Perform security audits

## 📚 Mathematical Properties

### Why Hyperchaos?

Hyperchaotic systems (with more than one positive Lyapunov exponent) offer:

-   **Higher complexity**: More unpredictable behavior
-   **Better key space**: Larger sensitivity to initial conditions
-   **Enhanced security**: More difficult to reconstruct from observations

### Lyapunov Exponents

The systems implemented have positive Lyapunov exponents, ensuring:

-   Exponential divergence of nearby trajectories
-   Sensitive dependence on initial conditions
-   Ergodic behavior over phase space

## 🎯 Performance

-   **System solving**: ~1-2 seconds (10,000 time points)
-   **Key generation**: < 100ms
-   **S-box generation**: < 50ms
-   **Encryption**: ~100-500ms (depending on image size and rounds)
-   **Decryption**: ~100-500ms (depending on image size and rounds)

## 🐛 Troubleshooting

### "Failed to initialize" error

-   Ensure Flask server is running on port 5000
-   Check that all Python dependencies are installed
-   Verify CORS is enabled

### "Module not found" errors

-   Install all required packages: `pip install -r requirements.txt`
-   For React: `npm install lucide-react`

### Image encryption fails

-   Ensure image is in RGB format
-   Check that system is initialized
-   Verify server is accessible

## 🌟 Future Enhancements

-   [ ] GPU acceleration for larger images
-   [ ] Additional chaotic systems (Qi, Liu, etc.)
-   [ ] Real-time encryption performance metrics
-   [ ] 3D phase space visualization
-   [ ] Video encryption support
-   [ ] Mobile app version

## 📖 References

1. Rössler, O. E. (1979). "An equation for hyperchaos"
2. Chen, G., & Ueta, T. (1999). "Yet another chaotic attractor"
3. Lorenz, E. N. (1963). "Deterministic nonperiodic flow"
4. Shannon, C. E. (1949). "Communication theory of secrecy systems"

## 📄 License

This project is for educational purposes. Feel free to use and modify.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

-   Additional chaotic systems
-   Performance optimizations
-   Security enhancements
-   UI/UX improvements

---

**Built with chaos, encrypted with mathematics** 🔐✨
