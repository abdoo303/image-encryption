import React, { useState, useEffect, useRef } from "react";
import { Upload, Lock, Unlock, Zap, Activity, Code, Layers } from "lucide-react";

// Main App Component
export default function App() {
    const [initialized, setInitialized] = useState(false);
    const [loading, setLoading] = useState(false);
    const [seed, setSeed] = useState("quantum_entropy_2025");
    const [systemInfo, setSystemInfo] = useState(null);
    const [originalImage, setOriginalImage] = useState(null);
    const [encryptedImage, setEncryptedImage] = useState(null);
    const [decryptedImage, setDecryptedImage] = useState(null);
    const [originalShape, setOriginalShape] = useState(null);
    const [rounds, setRounds] = useState(3);
    const [activeTab, setActiveTab] = useState("encrypt");
    const [visualData, setVisualData] = useState(null);
    const [analysisData, setAnalysisData] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const canvasRef = useRef(null);

    // Initialize the crypto system
    const initializeSystem = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://localhost:5001/api/initialize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ seed }),
            });
            const data = await response.json();

            if (data.success) {
                setSystemInfo(data);
                setInitialized(true);

                // Get visualization data
                const vizResponse = await fetch("http://localhost:5001/api/visualize");
                const vizData = await vizResponse.json();
                if (vizData.success) {
                    setVisualData(vizData.trajectories);
                }
            }
        } catch (error) {
            console.error("Initialization error:", error);
            alert(
                "Failed to initialize. Make sure the Flask server is running on port 5001."
            );
        }
        setLoading(false);
    };

    // Handle image upload
    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setOriginalImage(event.target.result);
                setEncryptedImage(null);
                setDecryptedImage(null);
            };
            reader.readAsDataURL(file);
        }
    };

    // Encrypt image
    const encryptImage = async () => {
        if (!originalImage) return;

        setLoading(true);
        try {
            const response = await fetch("http://localhost:5001/api/encrypt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    image: originalImage,
                    rounds: rounds,
                }),
            });
            const data = await response.json();

            if (data.success) {
                setEncryptedImage(data.encrypted_image);
                setOriginalShape(data.original_shape);
            }
        } catch (error) {
            console.error("Encryption error:", error);
        }
        setLoading(false);
    };

    // Decrypt image
    const decryptImage = async () => {
        if (!encryptedImage || !systemInfo || !originalShape) return;

        setLoading(true);
        try {
            const response = await fetch("http://localhost:5001/api/decrypt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    encrypted_image: encryptedImage,
                    original_shape: originalShape,
                    rounds: rounds,
                }),
            });
            const data = await response.json();

            if (data.success) {
                setDecryptedImage(data.decrypted_image);
            }
        } catch (error) {
            console.error("Decryption error:", error);
        }
        setLoading(false);
    };

    // Analyze images
    const analyzeImages = async () => {
        if (!originalImage || !encryptedImage || !decryptedImage || !originalShape) {
            alert("Please complete encryption and decryption first!");
            return;
        }

        console.log("Starting analysis...");
        setIsAnalyzing(true);
        try {
            console.log("Sending analysis request to server...");
            const response = await fetch("http://localhost:5001/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    original_image: originalImage,
                    encrypted_image: encryptedImage,
                    decrypted_image: decryptedImage,
                    original_shape: originalShape,
                    rounds: rounds,
                }),
            });
            console.log("Response received:", response.status);
            const data = await response.json();
            console.log("Analysis data:", data);

            if (data.success) {
                console.log("Analysis successful, setting data and switching tab");
                setAnalysisData(data.analysis);
                setActiveTab("analysis");
            } else {
                console.error("Analysis failed:", data.error);
                alert("Analysis failed: " + data.error);
            }
        } catch (error) {
            console.error("Analysis error:", error);
            alert("Failed to analyze images. Error: " + error.message);
        }
        setIsAnalyzing(false);
    };

    // Draw chaos visualization
    useEffect(() => {
        if (!visualData || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        const width = canvas.width;
        const height = canvas.height;

        ctx.fillStyle = "#000000";
        ctx.fillRect(0, 0, width, height);

        // Draw all three systems with different colors
        const systems = [
            { data: visualData.system1, color: "#00ffff" },
            { data: visualData.system2, color: "#ff00ff" },
            { data: visualData.system3, color: "#ffff00" },
        ];

        systems.forEach((system, idx) => {
            const x = system.data.x;
            const y = system.data.y;

            // Normalize coordinates
            const xMin = Math.min(...x);
            const xMax = Math.max(...x);
            const yMin = Math.min(...y);
            const yMax = Math.max(...y);

            ctx.strokeStyle = system.color;
            ctx.lineWidth = 1;
            ctx.globalAlpha = 0.3;
            ctx.beginPath();

            for (let i = 0; i < x.length; i++) {
                const px = ((x[i] - xMin) / (xMax - xMin)) * (width - 40) + 20;
                const py = ((y[i] - yMin) / (yMax - yMin)) * (height - 40) + 20;

                if (i === 0) {
                    ctx.moveTo(px, py);
                } else {
                    ctx.lineTo(px, py);
                }
            }
            ctx.stroke();
        });
    }, [visualData]);

    return (
        <div
            style={{
                minHeight: "100vh",
                background:
                    "linear-gradient(135deg, #0a0a0a 0%, #1a0a1a 50%, #0a1a1a 100%)",
                color: "#ffffff",
                fontFamily: '"Courier New", monospace',
                overflow: "hidden",
                position: "relative",
            }}
        >
            {/* Animated Grid Background */}
            <div
                style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundImage: `
          linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255, 0, 255, 0.03) 1px, transparent 1px)
        `,
                    backgroundSize: "50px 50px",
                    animation: "gridMove 20s linear infinite",
                    pointerEvents: "none",
                    zIndex: 0,
                }}
            />

            <style>{`
        @keyframes gridMove {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @keyframes glitch {
          0% { transform: translate(0); }
          20% { transform: translate(-2px, 2px); }
          40% { transform: translate(-2px, -2px); }
          60% { transform: translate(2px, 2px); }
          80% { transform: translate(2px, -2px); }
          100% { transform: translate(0); }
        }
        .glow {
          text-shadow: 0 0 10px currentColor, 0 0 20px currentColor;
        }
        .cyber-button {
          background: linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(255, 0, 255, 0.2));
          border: 2px solid;
          border-image: linear-gradient(135deg, #00ffff, #ff00ff) 1;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }
        .cyber-button:before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
          transition: left 0.5s;
        }
        .cyber-button:hover:before {
          left: 100%;
        }
        .cyber-button:hover {
          box-shadow: 0 0 20px rgba(0, 255, 255, 0.5), 0 0 40px rgba(255, 0, 255, 0.3);
          transform: translateY(-2px);
        }
        .bitstream {
          font-family: 'Courier New', monospace;
          font-size: 10px;
          line-height: 1.2;
          animation: pulse 2s infinite;
        }
      `}</style>

            <div style={{ position: "relative", zIndex: 1, padding: "40px 20px" }}>
                {/* Header */}
                <header style={{ textAlign: "center", marginBottom: "60px" }}>
                    <h1
                        style={{
                            fontSize: "4rem",
                            fontWeight: "bold",
                            letterSpacing: "0.1em",
                            marginBottom: "10px",
                            background:
                                "linear-gradient(135deg, #00ffff, #ff00ff, #ffff00)",
                            WebkitBackgroundClip: "text",
                            WebkitTextFillColor: "transparent",
                            animation: "glitch 5s infinite",
                        }}
                        className="glow"
                    >
                        HYPERCHAOS
                    </h1>
                    <p
                        style={{
                            fontSize: "1.2rem",
                            color: "#00ffff",
                            letterSpacing: "0.3em",
                            opacity: 0.8,
                        }}
                    >
                        {">"} QUANTUM ENCRYPTION PROTOCOL {"<"}
                    </p>
                </header>

                {/* Initialization Section */}
                {!initialized && (
                    <div
                        style={{
                            maxWidth: "600px",
                            margin: "0 auto",
                            padding: "40px",
                            background: "rgba(0, 0, 0, 0.6)",
                            border: "2px solid #00ffff",
                            boxShadow: "0 0 30px rgba(0, 255, 255, 0.3)",
                            backdropFilter: "blur(10px)",
                        }}
                    >
                        <h2
                            style={{
                                color: "#00ffff",
                                marginBottom: "20px",
                                fontSize: "1.5rem",
                            }}
                        >
                            {"[ SYSTEM INITIALIZATION ]"}
                        </h2>
                        <div style={{ marginBottom: "20px" }}>
                            <label
                                style={{
                                    display: "block",
                                    marginBottom: "10px",
                                    color: "#00ffff",
                                }}
                            >
                                ENTROPY SEED:
                            </label>
                            <input
                                type="text"
                                value={seed}
                                onChange={(e) => setSeed(e.target.value)}
                                style={{
                                    width: "100%",
                                    padding: "12px",
                                    background: "rgba(0, 0, 0, 0.8)",
                                    border: "1px solid #00ffff",
                                    color: "#00ffff",
                                    fontFamily: '"Courier New", monospace',
                                    fontSize: "1rem",
                                }}
                                placeholder="Enter your quantum seed..."
                            />
                        </div>
                        <button
                            onClick={initializeSystem}
                            disabled={loading}
                            className="cyber-button"
                            style={{
                                width: "100%",
                                padding: "15px",
                                fontSize: "1.1rem",
                                color: "#00ffff",
                                cursor: loading ? "wait" : "pointer",
                                fontFamily: '"Courier New", monospace',
                                fontWeight: "bold",
                                letterSpacing: "0.2em",
                            }}
                        >
                            {loading ? "[ INITIALIZING... ]" : "[ INITIALIZE SYSTEMS ]"}
                        </button>
                    </div>
                )}

                {/* Main Interface */}
                {initialized && systemInfo && (
                    <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
                        {/* Tab Navigation */}
                        <div
                            style={{
                                display: "flex",
                                gap: "10px",
                                marginBottom: "30px",
                                justifyContent: "center",
                            }}
                        >
                            {[
                                { id: "encrypt", icon: Lock, label: "ENCRYPT" },
                                { id: "systems", icon: Activity, label: "SYSTEMS" },
                                { id: "keys", icon: Code, label: "KEYS" },
                                { id: "analysis", icon: Zap, label: "ANALYSIS" },
                            ].map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className="cyber-button"
                                    style={{
                                        padding: "12px 30px",
                                        fontSize: "1rem",
                                        color:
                                            activeTab === tab.id ? "#ffff00" : "#00ffff",
                                        borderColor:
                                            activeTab === tab.id ? "#ffff00" : "#00ffff",
                                        fontFamily: '"Courier New", monospace',
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "10px",
                                        cursor: "pointer",
                                    }}
                                >
                                    <tab.icon size={18} />
                                    {tab.label}
                                </button>
                            ))}
                        </div>

                        {/* Encrypt Tab */}
                        {activeTab === "encrypt" && (
                            <div
                                style={{
                                    display: "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit, minmax(300px, 1fr))",
                                    gap: "20px",
                                }}
                            >
                                {/* Upload Section */}
                                <div
                                    style={{
                                        padding: "30px",
                                        background: "rgba(0, 0, 0, 0.6)",
                                        border: "2px solid #00ffff",
                                        backdropFilter: "blur(10px)",
                                    }}
                                >
                                    <h3
                                        style={{ color: "#00ffff", marginBottom: "20px" }}
                                    >
                                        {">"} UPLOAD IMAGE
                                    </h3>
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleImageUpload}
                                        style={{ display: "none" }}
                                        id="imageUpload"
                                    />
                                    <label
                                        htmlFor="imageUpload"
                                        className="cyber-button"
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            gap: "10px",
                                            padding: "15px",
                                            cursor: "pointer",
                                            marginBottom: "20px",
                                        }}
                                    >
                                        <Upload size={20} />
                                        SELECT IMAGE
                                    </label>

                                    {originalImage && (
                                        <div>
                                            <img
                                                src={originalImage}
                                                alt="Original"
                                                style={{
                                                    width: "100%",
                                                    border: "1px solid #00ffff",
                                                    marginBottom: "15px",
                                                }}
                                            />
                                            <div style={{ marginBottom: "15px" }}>
                                                <label
                                                    style={{
                                                        color: "#00ffff",
                                                        display: "block",
                                                        marginBottom: "8px",
                                                    }}
                                                >
                                                    ENCRYPTION ROUNDS: {rounds}
                                                </label>
                                                <input
                                                    type="range"
                                                    min="1"
                                                    max="10"
                                                    value={rounds}
                                                    onChange={(e) =>
                                                        setRounds(
                                                            parseInt(e.target.value)
                                                        )
                                                    }
                                                    style={{ width: "100%" }}
                                                />
                                            </div>
                                            <button
                                                onClick={encryptImage}
                                                disabled={loading}
                                                className="cyber-button"
                                                style={{
                                                    width: "100%",
                                                    padding: "12px",
                                                    color: "#ff00ff",
                                                    borderColor: "#ff00ff",
                                                    cursor: loading ? "wait" : "pointer",
                                                    marginBottom: "10px",
                                                }}
                                            >
                                                <Lock
                                                    size={16}
                                                    style={{
                                                        display: "inline",
                                                        marginRight: "8px",
                                                    }}
                                                />
                                                {loading ? "ENCRYPTING..." : "ENCRYPT"}
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {/* Encrypted Image */}
                                {encryptedImage && (
                                    <div
                                        style={{
                                            padding: "30px",
                                            background: "rgba(0, 0, 0, 0.6)",
                                            border: "2px solid #ff00ff",
                                            backdropFilter: "blur(10px)",
                                        }}
                                    >
                                        <h3
                                            style={{
                                                color: "#ff00ff",
                                                marginBottom: "20px",
                                            }}
                                        >
                                            {">"} ENCRYPTED DATA
                                        </h3>
                                        <img
                                            src={encryptedImage}
                                            alt="Encrypted"
                                            style={{
                                                width: "100%",
                                                border: "1px solid #ff00ff",
                                                marginBottom: "15px",
                                                filter: "brightness(1.2) contrast(1.5)",
                                            }}
                                        />
                                        <button
                                            onClick={decryptImage}
                                            disabled={loading}
                                            className="cyber-button"
                                            style={{
                                                width: "100%",
                                                padding: "12px",
                                                color: "#ffff00",
                                                borderColor: "#ffff00",
                                                cursor: loading ? "wait" : "pointer",
                                            }}
                                        >
                                            <Unlock
                                                size={16}
                                                style={{
                                                    display: "inline",
                                                    marginRight: "8px",
                                                }}
                                            />
                                            {loading ? "DECRYPTING..." : "DECRYPT"}
                                        </button>
                                    </div>
                                )}

                                {/* Decrypted Image */}
                                {decryptedImage && (
                                    <div
                                        style={{
                                            padding: "30px",
                                            background: "rgba(0, 0, 0, 0.6)",
                                            border: "2px solid #00ff00",
                                            backdropFilter: "blur(10px)",
                                        }}
                                    >
                                        <h3
                                            style={{
                                                color: "#00ff00",
                                                marginBottom: "20px",
                                            }}
                                        >
                                            {">"} DECRYPTED IMAGE
                                        </h3>
                                        <img
                                            src={decryptedImage}
                                            alt="Decrypted"
                                            style={{
                                                width: "100%",
                                                border: "1px solid #00ff00",
                                                marginBottom: "15px",
                                            }}
                                        />
                                        <button
                                            onClick={analyzeImages}
                                            disabled={isAnalyzing}
                                            className="cyber-button"
                                            style={{
                                                width: "100%",
                                                padding: "12px",
                                                color: "#ffff00",
                                                borderColor: "#ffff00",
                                                cursor: isAnalyzing ? "wait" : "pointer",
                                            }}
                                        >
                                            <Zap
                                                size={16}
                                                style={{
                                                    display: "inline",
                                                    marginRight: "8px",
                                                }}
                                            />
                                            {isAnalyzing ? "ANALYZING..." : "ANALYZE PERFORMANCE"}
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Systems Tab */}
                        {activeTab === "systems" && (
                            <div>
                                {/* Visualization Canvas */}
                                {visualData && (
                                    <div
                                        style={{
                                            marginBottom: "30px",
                                            padding: "30px",
                                            background: "rgba(0, 0, 0, 0.8)",
                                            border: "2px solid #00ffff",
                                            backdropFilter: "blur(10px)",
                                        }}
                                    >
                                        <h3
                                            style={{
                                                color: "#00ffff",
                                                marginBottom: "20px",
                                            }}
                                        >
                                            {">"} PHASE SPACE TRAJECTORIES
                                        </h3>
                                        <canvas
                                            ref={canvasRef}
                                            width={1200}
                                            height={400}
                                            style={{
                                                width: "100%",
                                                border: "1px solid #00ffff",
                                            }}
                                        />
                                        <div
                                            style={{
                                                display: "flex",
                                                gap: "20px",
                                                marginTop: "15px",
                                                justifyContent: "center",
                                            }}
                                        >
                                            <span style={{ color: "#00ffff" }}>
                                                ■ Rössler
                                            </span>
                                            <span style={{ color: "#ff00ff" }}>
                                                ■ Chen
                                            </span>
                                            <span style={{ color: "#ffff00" }}>
                                                ■ Lorenz
                                            </span>
                                        </div>
                                    </div>
                                )}

                                {/* System Information */}
                                <div
                                    style={{
                                        display: "grid",
                                        gridTemplateColumns:
                                            "repeat(auto-fit, minmax(350px, 1fr))",
                                        gap: "20px",
                                    }}
                                >
                                    {Object.entries(systemInfo.systems).map(
                                        ([key, system], idx) => {
                                            const colors = [
                                                "#00ffff",
                                                "#ff00ff",
                                                "#ffff00",
                                            ];
                                            const color = colors[idx];

                                            return (
                                                <div
                                                    key={key}
                                                    style={{
                                                        padding: "25px",
                                                        background: "rgba(0, 0, 0, 0.6)",
                                                        border: `2px solid ${color}`,
                                                        backdropFilter: "blur(10px)",
                                                    }}
                                                >
                                                    <h3
                                                        style={{
                                                            color,
                                                            marginBottom: "15px",
                                                            fontSize: "1.2rem",
                                                        }}
                                                    >
                                                        {system.name}
                                                    </h3>
                                                    <div
                                                        style={{
                                                            fontSize: "0.9rem",
                                                            lineHeight: "1.8",
                                                        }}
                                                    >
                                                        <p style={{ color: "#888" }}>
                                                            DIMENSIONS:{" "}
                                                            <span style={{ color }}>
                                                                {system.dimensions}D
                                                            </span>
                                                        </p>
                                                        <p
                                                            style={{
                                                                color: "#888",
                                                                marginTop: "10px",
                                                            }}
                                                        >
                                                            PARAMETERS:
                                                        </p>
                                                        <code
                                                            style={{
                                                                display: "block",
                                                                background:
                                                                    "rgba(0, 0, 0, 0.6)",
                                                                padding: "10px",
                                                                color,
                                                                fontSize: "0.85rem",
                                                                marginTop: "5px",
                                                            }}
                                                        >
                                                            {JSON.stringify(
                                                                system.parameters,
                                                                null,
                                                                2
                                                            )}
                                                        </code>
                                                        <p
                                                            style={{
                                                                color: "#888",
                                                                marginTop: "10px",
                                                            }}
                                                        >
                                                            INITIAL CONDITIONS:
                                                        </p>
                                                        <code
                                                            style={{
                                                                display: "block",
                                                                background:
                                                                    "rgba(0, 0, 0, 0.6)",
                                                                padding: "10px",
                                                                color,
                                                                fontSize: "0.85rem",
                                                                marginTop: "5px",
                                                            }}
                                                        >
                                                            {JSON.stringify(
                                                                system.initial_conditions,
                                                                null,
                                                                2
                                                            )}
                                                        </code>
                                                    </div>
                                                </div>
                                            );
                                        }
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Keys Tab */}
                        {activeTab === "keys" && (
                            <div
                                style={{
                                    display: "grid",
                                    gridTemplateColumns:
                                        "repeat(auto-fit, minmax(400px, 1fr))",
                                    gap: "20px",
                                }}
                            >
                                {/* Bit-streams */}
                                <div
                                    style={{
                                        padding: "25px",
                                        background: "rgba(0, 0, 0, 0.6)",
                                        border: "2px solid #00ffff",
                                        backdropFilter: "blur(10px)",
                                    }}
                                >
                                    <h3
                                        style={{ color: "#00ffff", marginBottom: "15px" }}
                                    >
                                        {">"} BIT-STREAMS
                                    </h3>
                                    {Object.entries(systemInfo.bitstreams).map(
                                        ([key, bits], idx) => (
                                            <div
                                                key={key}
                                                style={{ marginBottom: "15px" }}
                                            >
                                                <p
                                                    style={{
                                                        color: "#888",
                                                        fontSize: "0.85rem",
                                                        marginBottom: "5px",
                                                    }}
                                                >
                                                    SYSTEM {idx + 1}:
                                                </p>
                                                <div
                                                    className="bitstream"
                                                    style={{
                                                        background: "rgba(0, 0, 0, 0.8)",
                                                        padding: "10px",
                                                        color: "#00ffff",
                                                        wordBreak: "break-all",
                                                        maxHeight: "80px",
                                                        overflow: "hidden",
                                                    }}
                                                >
                                                    {bits.join("")}
                                                </div>
                                            </div>
                                        )
                                    )}
                                </div>

                                {/* Encryption Keys */}
                                <div
                                    style={{
                                        padding: "25px",
                                        background: "rgba(0, 0, 0, 0.6)",
                                        border: "2px solid #ff00ff",
                                        backdropFilter: "blur(10px)",
                                    }}
                                >
                                    <h3
                                        style={{ color: "#ff00ff", marginBottom: "15px" }}
                                    >
                                        {">"} ENCRYPTION KEYS
                                    </h3>
                                    {Object.entries(systemInfo.keys).map(
                                        ([key, keyBytes], idx) => (
                                            <div
                                                key={key}
                                                style={{ marginBottom: "15px" }}
                                            >
                                                <p
                                                    style={{
                                                        color: "#888",
                                                        fontSize: "0.85rem",
                                                        marginBottom: "5px",
                                                    }}
                                                >
                                                    KEY {idx + 1} (First 32 bytes):
                                                </p>
                                                <div
                                                    style={{
                                                        background: "rgba(0, 0, 0, 0.8)",
                                                        padding: "10px",
                                                        color: "#ff00ff",
                                                        fontSize: "0.75rem",
                                                        fontFamily:
                                                            '"Courier New", monospace',
                                                        wordBreak: "break-all",
                                                    }}
                                                >
                                                    {keyBytes
                                                        .map((b) =>
                                                            b
                                                                .toString(16)
                                                                .padStart(2, "0")
                                                        )
                                                        .join(" ")}
                                                </div>
                                            </div>
                                        )
                                    )}
                                </div>

                                {/* S-boxes */}
                                <div
                                    style={{
                                        padding: "25px",
                                        background: "rgba(0, 0, 0, 0.6)",
                                        border: "2px solid #ffff00",
                                        backdropFilter: "blur(10px)",
                                    }}
                                >
                                    <h3
                                        style={{ color: "#ffff00", marginBottom: "15px" }}
                                    >
                                        {">"} S-BOXES
                                    </h3>
                                    {Object.entries(systemInfo.sboxes).map(
                                        ([key, sbox], idx) => (
                                            <div
                                                key={key}
                                                style={{ marginBottom: "15px" }}
                                            >
                                                <p
                                                    style={{
                                                        color: "#888",
                                                        fontSize: "0.85rem",
                                                        marginBottom: "5px",
                                                    }}
                                                >
                                                    S-BOX {idx + 1} (First 32 values):
                                                </p>
                                                <div
                                                    style={{
                                                        background: "rgba(0, 0, 0, 0.8)",
                                                        padding: "10px",
                                                        color: "#ffff00",
                                                        fontSize: "0.75rem",
                                                        fontFamily:
                                                            '"Courier New", monospace',
                                                        display: "grid",
                                                        gridTemplateColumns:
                                                            "repeat(8, 1fr)",
                                                        gap: "5px",
                                                    }}
                                                >
                                                    {sbox.map((val, i) => (
                                                        <span key={i}>
                                                            {val
                                                                .toString(16)
                                                                .padStart(2, "0")}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Analysis Tab */}
                        {activeTab === "analysis" && !analysisData && (
                            <div style={{
                                padding: "40px",
                                textAlign: "center",
                                background: "rgba(0, 0, 0, 0.6)",
                                border: "2px solid #ffff00",
                                borderRadius: "10px"
                            }}>
                                <h3 style={{ color: "#ffff00", marginBottom: "20px" }}>
                                    {">"} NO ANALYSIS DATA
                                </h3>
                                <p style={{ color: "#888" }}>
                                    Please complete encryption and decryption first, then click "ANALYZE PERFORMANCE"
                                </p>
                            </div>
                        )}
                        {activeTab === "analysis" && analysisData && (
                            <div style={{ maxWidth: "1600px", margin: "0 auto" }}>
                                {/* Performance Metrics Summary */}
                                <div
                                    style={{
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                                        gap: "20px",
                                        marginBottom: "30px",
                                    }}
                                >
                                    {/* MSE Card */}
                                    <MetricCard
                                        title="MSE Analysis"
                                        color="#00ffff"
                                        metrics={[
                                            {
                                                label: "Plain vs Encrypted",
                                                value: analysisData.mse_plain_encrypted.toFixed(2),
                                                description: "Higher is better (more different)",
                                            },
                                            {
                                                label: "Plain vs Decrypted",
                                                value: analysisData.mse_plain_decrypted.toFixed(2),
                                                description: "Lower is better (0 = perfect)",
                                            },
                                        ]}
                                    />

                                    {/* SSIM Card */}
                                    <MetricCard
                                        title="SSIM Analysis"
                                        color="#ff00ff"
                                        metrics={[
                                            {
                                                label: "Plain vs Encrypted",
                                                value: analysisData.ssim_plain_encrypted.toFixed(4),
                                                description: "Lower is better (0 = completely different)",
                                            },
                                            {
                                                label: "Plain vs Decrypted",
                                                value: analysisData.ssim_plain_decrypted.toFixed(4),
                                                description: "Higher is better (1 = identical)",
                                            },
                                        ]}
                                    />

                                    {/* Key Space Card */}
                                    <MetricCard
                                        title="Key Space"
                                        color="#ffff00"
                                        metrics={[
                                            {
                                                label: "Key Space (bits)",
                                                value: analysisData.key_space.key_space_bits.toFixed(0),
                                                description: `~${analysisData.key_space.comparison_aes256.toFixed(1)}x stronger than AES-256`,
                                            },
                                            {
                                                label: "Total Parameters",
                                                value: analysisData.key_space.total_parameters,
                                                description: `${analysisData.key_space.initial_conditions} ICs + ${analysisData.key_space.system_parameters} params`,
                                            },
                                        ]}
                                    />
                                </div>

                                {/* Shannon Entropy */}
                                <EntropyDisplay entropy={analysisData.entropy} />

                                {/* Histograms */}
                                <HistogramDisplay histograms={analysisData.histograms} />

                                {/* Correlation Analysis */}
                                <CorrelationDisplay correlation={analysisData.correlation} />

                                {/* Noise Resistance */}
                                <NoiseResistanceDisplay noiseData={analysisData.noise_resistance} />

                                {/* Statistics */}
                                <StatisticsDisplay stats={analysisData.statistics} />
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

// Helper Components for Analysis Display

const MetricCard = ({ title, color, metrics }) => (
    <div
        style={{
            padding: "25px",
            background: "rgba(0, 0, 0, 0.6)",
            border: `2px solid ${color}`,
            backdropFilter: "blur(10px)",
        }}
    >
        <h3 style={{ color, marginBottom: "20px", fontSize: "1.2rem" }}>
            {">"} {title}
        </h3>
        {metrics.map((metric, idx) => (
            <div key={idx} style={{ marginBottom: "15px" }}>
                <p style={{ color: "#888", fontSize: "0.85rem", marginBottom: "5px" }}>
                    {metric.label}:
                </p>
                <p style={{ color, fontSize: "1.5rem", fontWeight: "bold", marginBottom: "5px" }}>
                    {metric.value}
                </p>
                <p style={{ color: "#666", fontSize: "0.75rem" }}>{metric.description}</p>
            </div>
        ))}
    </div>
);

const EntropyDisplay = ({ entropy }) => (
    <div
        style={{
            padding: "30px",
            background: "rgba(0, 0, 0, 0.6)",
            border: "2px solid #00ffff",
            backdropFilter: "blur(10px)",
            marginBottom: "30px",
        }}
    >
        <h3 style={{ color: "#00ffff", marginBottom: "20px", fontSize: "1.3rem" }}>
            {">"} SHANNON ENTROPY (bits/pixel)
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px" }}>
            {["original", "encrypted", "decrypted"].map((type) => (
                <div key={type} style={{ textAlign: "center" }}>
                    <p style={{ color: "#888", fontSize: "0.9rem", marginBottom: "10px", textTransform: "uppercase" }}>
                        {type}
                    </p>
                    <p style={{ color: "#00ffff", fontSize: "2rem", fontWeight: "bold" }}>
                        {entropy[type].Overall.toFixed(4)}
                    </p>
                    <div style={{ marginTop: "10px", fontSize: "0.8rem" }}>
                        {entropy[type].Red !== undefined && (
                            <>
                                <p style={{ color: "#ff6666" }}>R: {entropy[type].Red.toFixed(3)}</p>
                                <p style={{ color: "#66ff66" }}>G: {entropy[type].Green.toFixed(3)}</p>
                                <p style={{ color: "#6666ff" }}>B: {entropy[type].Blue.toFixed(3)}</p>
                            </>
                        )}
                    </div>
                </div>
            ))}
        </div>
        <p style={{ color: "#666", fontSize: "0.85rem", marginTop: "20px", textAlign: "center" }}>
            Maximum entropy is 8.0 bits/pixel. Higher entropy = better randomness
        </p>
    </div>
);

const HistogramDisplay = ({ histograms }) => {
    const HistogramChart = ({ data, title, color }) => {
        const maxValue = Math.max(...data.Red.values, ...data.Green.values, ...data.Blue.values);

        return (
            <div style={{ marginBottom: "20px" }}>
                <h4 style={{ color, marginBottom: "10px", fontSize: "1rem" }}>{title}</h4>
                <div style={{ display: "flex", gap: "10px", height: "150px", alignItems: "flex-end" }}>
                    {data.Red.values.map((val, idx) => {
                        if (idx % 8 !== 0) return null; // Sample every 8th value
                        const redHeight = (data.Red.values[idx] / maxValue) * 100;
                        const greenHeight = (data.Green.values[idx] / maxValue) * 100;
                        const blueHeight = (data.Blue.values[idx] / maxValue) * 100;

                        return (
                            <div key={idx} style={{ flex: 1, display: "flex", gap: "1px", alignItems: "flex-end" }}>
                                <div
                                    style={{
                                        flex: 1,
                                        height: `${redHeight}%`,
                                        background: "rgba(255, 100, 100, 0.7)",
                                        minHeight: "2px",
                                    }}
                                />
                                <div
                                    style={{
                                        flex: 1,
                                        height: `${greenHeight}%`,
                                        background: "rgba(100, 255, 100, 0.7)",
                                        minHeight: "2px",
                                    }}
                                />
                                <div
                                    style={{
                                        flex: 1,
                                        height: `${blueHeight}%`,
                                        background: "rgba(100, 100, 255, 0.7)",
                                        minHeight: "2px",
                                    }}
                                />
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    };

    return (
        <div
            style={{
                padding: "30px",
                background: "rgba(0, 0, 0, 0.6)",
                border: "2px solid #ff00ff",
                backdropFilter: "blur(10px)",
                marginBottom: "30px",
            }}
        >
            <h3 style={{ color: "#ff00ff", marginBottom: "20px", fontSize: "1.3rem" }}>
                {">"} HISTOGRAM ANALYSIS
            </h3>
            <HistogramChart data={histograms.original} title="Original Image" color="#00ffff" />
            <HistogramChart data={histograms.encrypted} title="Encrypted Image" color="#ff00ff" />
            <HistogramChart data={histograms.decrypted} title="Decrypted Image" color="#00ff00" />
            <p style={{ color: "#666", fontSize: "0.85rem", marginTop: "15px" }}>
                Encrypted images should have uniform (flat) histograms across all channels
            </p>
        </div>
    );
};

const CorrelationDisplay = ({ correlation }) => (
    <div
        style={{
            padding: "30px",
            background: "rgba(0, 0, 0, 0.6)",
            border: "2px solid #ffff00",
            backdropFilter: "blur(10px)",
            marginBottom: "30px",
        }}
    >
        <h3 style={{ color: "#ffff00", marginBottom: "20px", fontSize: "1.3rem" }}>
            {">"} CORRELATION ANALYSIS
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "20px" }}>
            {["horizontal", "vertical", "diagonal"].map((direction) => (
                <div key={direction} style={{ textAlign: "center" }}>
                    <p style={{ color: "#888", fontSize: "0.9rem", marginBottom: "10px", textTransform: "uppercase" }}>
                        {direction}
                    </p>
                    <div style={{ marginBottom: "15px" }}>
                        <p style={{ color: "#666", fontSize: "0.75rem" }}>Original</p>
                        <p style={{ color: "#00ffff", fontSize: "1.2rem", fontWeight: "bold" }}>
                            {correlation.original[direction].correlation.toFixed(4)}
                        </p>
                    </div>
                    <div>
                        <p style={{ color: "#666", fontSize: "0.75rem" }}>Encrypted</p>
                        <p style={{ color: "#ff00ff", fontSize: "1.2rem", fontWeight: "bold" }}>
                            {correlation.encrypted[direction].correlation.toFixed(4)}
                        </p>
                    </div>
                </div>
            ))}
        </div>
        <p style={{ color: "#666", fontSize: "0.85rem", marginTop: "20px", textAlign: "center" }}>
            Encrypted images should have correlation close to 0 (no correlation between adjacent pixels)
        </p>
    </div>
);

const NoiseResistanceDisplay = ({ noiseData }) => (
    <div
        style={{
            padding: "30px",
            background: "rgba(0, 0, 0, 0.6)",
            border: "2px solid #00ff00",
            backdropFilter: "blur(10px)",
            marginBottom: "30px",
        }}
    >
        <h3 style={{ color: "#00ff00", marginBottom: "20px", fontSize: "1.3rem" }}>
            {">"} NOISE RESISTANCE ANALYSIS
        </h3>
        <p style={{ color: "#888", fontSize: "0.9rem", marginBottom: "20px" }}>
            Salt & Pepper noise added to encrypted images, then decrypted
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px" }}>
            {noiseData.map((result, idx) => (
                <div
                    key={idx}
                    style={{
                        padding: "15px",
                        background: "rgba(0, 0, 0, 0.4)",
                        border: "1px solid #00ff00",
                    }}
                >
                    <p style={{ color: "#00ff00", fontSize: "1rem", marginBottom: "10px", fontWeight: "bold" }}>
                        Noise: {result.noise_level}
                    </p>
                    {result.error ? (
                        <p style={{ color: "#ff6666", fontSize: "0.85rem" }}>Error: {result.error}</p>
                    ) : (
                        <>
                            <div style={{ marginBottom: "10px" }}>
                                <img
                                    src={result.decrypted_image}
                                    alt={`Noisy ${result.noise_level}`}
                                    style={{ width: "100%", border: "1px solid #00ff00" }}
                                />
                            </div>
                            <p style={{ color: "#888", fontSize: "0.75rem" }}>
                                MSE: <span style={{ color: "#00ff00" }}>{result.mse.toFixed(2)}</span>
                            </p>
                            <p style={{ color: "#888", fontSize: "0.75rem" }}>
                                SSIM: <span style={{ color: "#00ff00" }}>{result.ssim.toFixed(4)}</span>
                            </p>
                            <p style={{ color: "#888", fontSize: "0.75rem" }}>
                                PSNR: <span style={{ color: "#00ff00" }}>{result.psnr.toFixed(2)} dB</span>
                            </p>
                        </>
                    )}
                </div>
            ))}
        </div>
    </div>
);

const StatisticsDisplay = ({ stats }) => (
    <div
        style={{
            padding: "30px",
            background: "rgba(0, 0, 0, 0.6)",
            border: "2px solid #00ffff",
            backdropFilter: "blur(10px)",
            marginBottom: "30px",
        }}
    >
        <h3 style={{ color: "#00ffff", marginBottom: "20px", fontSize: "1.3rem" }}>
            {">"} STATISTICAL PROPERTIES
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px" }}>
            {["original", "encrypted", "decrypted"].map((type) => (
                <div
                    key={type}
                    style={{
                        padding: "20px",
                        background: "rgba(0, 0, 0, 0.4)",
                        border: "1px solid #00ffff",
                    }}
                >
                    <h4 style={{ color: "#00ffff", marginBottom: "15px", textTransform: "uppercase" }}>{type}</h4>
                    {Object.entries(stats[type]).map(([key, value]) => (
                        <p key={key} style={{ color: "#888", fontSize: "0.8rem", marginBottom: "5px" }}>
                            {key.toUpperCase()}:{" "}
                            <span style={{ color: "#00ffff" }}>
                                {typeof value === "number" ? value.toFixed(2) : value}
                            </span>
                        </p>
                    ))}
                </div>
            ))}
        </div>
    </div>
);
