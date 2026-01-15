import React, { useState } from "react";
import { Upload, Lock, Unlock, Zap, Activity, Code } from "lucide-react";

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
    const [chaosData, setChaosData] = useState(null);
    const [isComputingChaos, setIsComputingChaos] = useState(false);
    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5001";

    // Initialize the crypto system
    const initializeSystem = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/initialize`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ seed }),
            });
            const data = await response.json();

            if (data.success) {
                setSystemInfo(data);
                setInitialized(true);

                // Get visualization plots (matplotlib-generated images)
                const vizResponse = await fetch(`${API_BASE_URL}/api/visualize`);
                const vizData = await vizResponse.json();
                console.log("Visualization data received:", vizData);
                if (vizData.success) {
                    setVisualData(vizData.plots);
                    console.log("Visual plots set:", vizData.plots);
                } else {
                    console.error("Failed to get visualization data:", vizData);
                }
            }
        } catch (error) {
            console.error("Initialization error:", error);
            alert(
                "Failed to initialize. Make sure the Flask server is running on " +
                    API_BASE_URL
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
            const response = await fetch(`${API_BASE_URL}/api/encrypt`, {
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
            const response = await fetch(`${API_BASE_URL}/api/decrypt`, {
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
            const response = await fetch(`${API_BASE_URL}/api/analyze`, {
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

    const [bifurcationDiagrams, setBifurcationDiagrams] = useState({});
    const [isComputingBifurcation, setIsComputingBifurcation] = useState(false);

    const fetchBifurcationDiagrams = async () => {
        setIsComputingBifurcation(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/bifurcation-diagrams`);
            const data = await response.json();

            if (data.success) {
                const diagrams = {};
                Object.entries(data.bifurcation_diagrams).forEach(([key, base64]) => {
                    diagrams[key] = `data:image/png;base64,${base64}`;
                });
                setBifurcationDiagrams(diagrams);
                console.log("Bifurcation diagrams received:", diagrams);
            } else {
                alert("Failed to fetch bifurcation diagrams: " + data.error);
            }
        } catch (error) {
            console.error("Error fetching bifurcation diagrams:", error);
            alert("Error: " + error.message);
        } finally {
            setIsComputingBifurcation(false);
        }
    };

    // Compute chaos analysis (Lyapunov)
    const computeChaosAnalysis = async () => {
        setIsComputingChaos(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/chaos-analysis`);
            const data = await response.json();
            console.log("Chaos analysis data received:", data);
            if (data.success) {
                setChaosData(data);
                console.log("Chaos data set:", data);
            } else {
                console.error("Failed to get chaos analysis:", data);
                alert("Failed to compute chaos analysis: " + data.error);
            }
        } catch (error) {
            console.error("Chaos analysis error:", error);
            alert(
                "Failed to compute chaos analysis. Make sure the Flask server is running."
            );
        }
        setIsComputingChaos(false);
    };

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
                                { id: "chaos", icon: Activity, label: "CHAOS PROOF" },
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
                                            {isAnalyzing
                                                ? "ANALYZING..."
                                                : "ANALYZE PERFORMANCE"}
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
                                            {">"} INTERACTIVE PHASE SPACE TRAJECTORIES (3D
                                            plots - Drag to rotate, scroll to zoom)
                                        </h3>

                                        {/* Rössler System - 3 interactive plots */}
                                        <div style={{ marginBottom: "30px" }}>
                                            <h4
                                                style={{
                                                    color: "#00ffff",
                                                    marginBottom: "15px",
                                                }}
                                            >
                                                {">"} Rössler Hyperchaos (Drag to rotate,
                                                scroll to zoom)
                                            </h4>
                                            <div
                                                style={{
                                                    display: "flex",
                                                    gap: "15px",
                                                    flexWrap: "wrap",
                                                }}
                                            >
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.rossler.xyz}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #00ffff",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Rössler (X,Y,Z)"
                                                    />
                                                </div>
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.rossler.xyw}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #00ffff",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Rössler (X,Y,W)"
                                                    />
                                                </div>
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.rossler.xzw}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #00ffff",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Rössler (X,Z,W)"
                                                    />
                                                </div>
                                            </div>
                                        </div>

                                        {/* Chen System - 3 interactive plots */}
                                        <div style={{ marginBottom: "30px" }}>
                                            <h4
                                                style={{
                                                    color: "#ff00ff",
                                                    marginBottom: "15px",
                                                }}
                                            >
                                                {">"} Chen Hyperchaos (Drag to rotate,
                                                scroll to zoom)
                                            </h4>
                                            <div
                                                style={{
                                                    display: "flex",
                                                    gap: "15px",
                                                    flexWrap: "wrap",
                                                }}
                                            >
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.chen.xyz}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #ff00ff",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Chen (X,Y,Z)"
                                                    />
                                                </div>
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.chen.xyw}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #ff00ff",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Chen (X,Y,W)"
                                                    />
                                                </div>
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.chen.xzw}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #ff00ff",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Chen (X,Z,W)"
                                                    />
                                                </div>
                                            </div>
                                        </div>

                                        {/* Lorenz System - 3 interactive plots */}
                                        <div style={{ marginBottom: "10px" }}>
                                            <h4
                                                style={{
                                                    color: "#ffff00",
                                                    marginBottom: "15px",
                                                }}
                                            >
                                                {">"} Lorenz Hyperchaos (Drag to rotate,
                                                scroll to zoom)
                                            </h4>
                                            <div
                                                style={{
                                                    display: "flex",
                                                    gap: "15px",
                                                    flexWrap: "wrap",
                                                }}
                                            >
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.lorenz.xyz}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #ffff00",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Lorenz (X,Y,Z)"
                                                    />
                                                </div>
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.lorenz.xyw}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #ffff00",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Lorenz (X,Y,W)"
                                                    />
                                                </div>
                                                <div style={{ flex: "1 1 300px" }}>
                                                    <iframe
                                                        srcDoc={visualData.lorenz.xzw}
                                                        style={{
                                                            width: "100%",
                                                            height: "500px",
                                                            border: "2px solid #ffff00",
                                                            background: "#0a0a0a",
                                                        }}
                                                        title="Lorenz (X,Z,W)"
                                                    />
                                                </div>
                                            </div>
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

                        {/* Chaos Proof Tab */}
                        {activeTab === "chaos" && (
                            <div>
                                <div
                                    style={{
                                        marginBottom: "30px",
                                        padding: "30px",
                                        background: "rgba(0, 0, 0, 0.8)",
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
                                        {">"} HYPERCHAOS MATHEMATICAL PROOF
                                    </h3>
                                    <p
                                        style={{
                                            color: "#888",
                                            marginBottom: "20px",
                                            lineHeight: "1.8",
                                        }}
                                    >
                                        This section provides rigorous mathematical proof
                                        that all three systems exhibit hyperchaotic
                                        behavior. A system is hyperchaotic if it has at
                                        least two positive Lyapunov exponents (λ₁ {">"} 0
                                        and λ₂ {">"} 0).{" "}
                                    </p>
                                    <button
                                        onClick={computeChaosAnalysis}
                                        disabled={isComputingChaos}
                                        className="cyber-button"
                                        style={{
                                            width: "100%",
                                            padding: "15px",
                                            fontSize: "1.1rem",
                                            color: "#00ff00",
                                            borderColor: "#00ff00",
                                            cursor: isComputingChaos ? "wait" : "pointer",
                                            marginBottom: "30px",
                                        }}
                                    >
                                        {isComputingChaos
                                            ? "COMPUTING LYAPUNOV EXPONENTS..."
                                            : "COMPUTE CHAOS ANALYSIS"}
                                    </button>
                                    {chaosData && (
                                        <div>
                                            {/* Lyapunov Exponents */}
                                            <div style={{ marginBottom: "40px" }}>
                                                <h4
                                                    style={{
                                                        color: "#00ffff",
                                                        marginBottom: "20px",
                                                    }}
                                                >
                                                    {">"} LYAPUNOV EXPONENTS (Gold
                                                    Standard for Hyperchaos)
                                                </h4>

                                                <div
                                                    style={{
                                                        display: "grid",
                                                        gridTemplateColumns:
                                                            "repeat(auto-fit, minmax(350px, 1fr))",
                                                        gap: "20px",
                                                    }}
                                                >
                                                    {/* Rössler */}
                                                    <div
                                                        style={{
                                                            padding: "20px",
                                                            background:
                                                                "rgba(0, 255, 255, 0.1)",
                                                            border: "2px solid #00ffff",
                                                        }}
                                                    >
                                                        <h5
                                                            style={{
                                                                color: "#00ffff",
                                                                marginBottom: "15px",
                                                            }}
                                                        >
                                                            Rössler Hyperchaos
                                                        </h5>
                                                        <div
                                                            style={{
                                                                fontFamily: "monospace",
                                                                fontSize: "0.9rem",
                                                            }}
                                                        >
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₁ ={" "}
                                                                {chaosData.lyapunov.rossler.lambda1.toFixed(
                                                                    4
                                                                )}
                                                                <span
                                                                    style={{
                                                                        color:
                                                                            chaosData
                                                                                .lyapunov
                                                                                .rossler
                                                                                .lambda1 >
                                                                            0
                                                                                ? "#00ff00"
                                                                                : "#ff0000",
                                                                        marginLeft:
                                                                            "10px",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .rossler.lambda1 >
                                                                    0
                                                                        ? "✓ Positive"
                                                                        : "✗ Negative"}
                                                                </span>
                                                            </p>
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₂ ={" "}
                                                                {chaosData.lyapunov.rossler.lambda2.toFixed(
                                                                    4
                                                                )}
                                                                <span
                                                                    style={{
                                                                        color:
                                                                            chaosData
                                                                                .lyapunov
                                                                                .rossler
                                                                                .lambda2 >
                                                                            0
                                                                                ? "#00ff00"
                                                                                : "#ff0000",
                                                                        marginLeft:
                                                                            "10px",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .rossler.lambda2 >
                                                                    0
                                                                        ? "✓ Positive"
                                                                        : "✗ Negative"}
                                                                </span>
                                                            </p>
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₃ ={" "}
                                                                {chaosData.lyapunov.rossler.exponents[2].toFixed(
                                                                    4
                                                                )}
                                                            </p>
                                                            <p style={{ color: "#fff" }}>
                                                                λ₄ ={" "}
                                                                {chaosData.lyapunov.rossler.exponents[3].toFixed(
                                                                    4
                                                                )}
                                                            </p>
                                                            <div
                                                                style={{
                                                                    marginTop: "15px",
                                                                    padding: "10px",
                                                                    background: chaosData
                                                                        .lyapunov.rossler
                                                                        .is_hyperchaotic
                                                                        ? "rgba(0, 255, 0, 0.2)"
                                                                        : "rgba(255, 0, 0, 0.2)",
                                                                    border: `1px solid ${
                                                                        chaosData.lyapunov
                                                                            .rossler
                                                                            .is_hyperchaotic
                                                                            ? "#00ff00"
                                                                            : "#ff0000"
                                                                    }`,
                                                                }}
                                                            >
                                                                <strong
                                                                    style={{
                                                                        color: chaosData
                                                                            .lyapunov
                                                                            .rossler
                                                                            .is_hyperchaotic
                                                                            ? "#00ff00"
                                                                            : "#ff0000",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .rossler
                                                                        .is_hyperchaotic
                                                                        ? "✓ HYPERCHAOTIC"
                                                                        : "✗ NOT HYPERCHAOTIC"}
                                                                </strong>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Chen */}
                                                    <div
                                                        style={{
                                                            padding: "20px",
                                                            background:
                                                                "rgba(255, 0, 255, 0.1)",
                                                            border: "2px solid #ff00ff",
                                                        }}
                                                    >
                                                        <h5
                                                            style={{
                                                                color: "#ff00ff",
                                                                marginBottom: "15px",
                                                            }}
                                                        >
                                                            Chen Hyperchaos
                                                        </h5>
                                                        <div
                                                            style={{
                                                                fontFamily: "monospace",
                                                                fontSize: "0.9rem",
                                                            }}
                                                        >
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₁ ={" "}
                                                                {chaosData.lyapunov.chen.lambda1.toFixed(
                                                                    4
                                                                )}
                                                                <span
                                                                    style={{
                                                                        color:
                                                                            chaosData
                                                                                .lyapunov
                                                                                .chen
                                                                                .lambda1 >
                                                                            0
                                                                                ? "#00ff00"
                                                                                : "#ff0000",
                                                                        marginLeft:
                                                                            "10px",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .chen.lambda1 > 0
                                                                        ? "✓ Positive"
                                                                        : "✗ Negative"}
                                                                </span>
                                                            </p>
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₂ ={" "}
                                                                {chaosData.lyapunov.chen.lambda2.toFixed(
                                                                    4
                                                                )}
                                                                <span
                                                                    style={{
                                                                        color:
                                                                            chaosData
                                                                                .lyapunov
                                                                                .chen
                                                                                .lambda2 >
                                                                            0
                                                                                ? "#00ff00"
                                                                                : "#ff0000",
                                                                        marginLeft:
                                                                            "10px",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .chen.lambda2 > 0
                                                                        ? "✓ Positive"
                                                                        : "✗ Negative"}
                                                                </span>
                                                            </p>
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₃ ={" "}
                                                                {chaosData.lyapunov.chen.exponents[2].toFixed(
                                                                    4
                                                                )}
                                                            </p>
                                                            <p style={{ color: "#fff" }}>
                                                                λ₄ ={" "}
                                                                {chaosData.lyapunov.chen.exponents[3].toFixed(
                                                                    4
                                                                )}
                                                            </p>
                                                            <div
                                                                style={{
                                                                    marginTop: "15px",
                                                                    padding: "10px",
                                                                    background: chaosData
                                                                        .lyapunov.chen
                                                                        .is_hyperchaotic
                                                                        ? "rgba(0, 255, 0, 0.2)"
                                                                        : "rgba(255, 0, 0, 0.2)",
                                                                    border: `1px solid ${
                                                                        chaosData.lyapunov
                                                                            .chen
                                                                            .is_hyperchaotic
                                                                            ? "#00ff00"
                                                                            : "#ff0000"
                                                                    }`,
                                                                }}
                                                            >
                                                                <strong
                                                                    style={{
                                                                        color: chaosData
                                                                            .lyapunov.chen
                                                                            .is_hyperchaotic
                                                                            ? "#00ff00"
                                                                            : "#ff0000",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .chen
                                                                        .is_hyperchaotic
                                                                        ? "✓ HYPERCHAOTIC"
                                                                        : "✗ NOT HYPERCHAOTIC"}
                                                                </strong>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Lorenz */}
                                                    <div
                                                        style={{
                                                            padding: "20px",
                                                            background:
                                                                "rgba(255, 255, 0, 0.1)",
                                                            border: "2px solid #ffff00",
                                                        }}
                                                    >
                                                        <h5
                                                            style={{
                                                                color: "#ffff00",
                                                                marginBottom: "15px",
                                                            }}
                                                        >
                                                            Lorenz Hyperchaos
                                                        </h5>
                                                        <div
                                                            style={{
                                                                fontFamily: "monospace",
                                                                fontSize: "0.9rem",
                                                            }}
                                                        >
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₁ ={" "}
                                                                {chaosData.lyapunov.lorenz.lambda1.toFixed(
                                                                    4
                                                                )}
                                                                <span
                                                                    style={{
                                                                        color:
                                                                            chaosData
                                                                                .lyapunov
                                                                                .lorenz
                                                                                .lambda1 >
                                                                            0
                                                                                ? "#00ff00"
                                                                                : "#ff0000",
                                                                        marginLeft:
                                                                            "10px",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .lorenz.lambda1 >
                                                                    0
                                                                        ? "✓ Positive"
                                                                        : "✗ Negative"}
                                                                </span>
                                                            </p>
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₂ ={" "}
                                                                {chaosData.lyapunov.lorenz.lambda2.toFixed(
                                                                    4
                                                                )}
                                                                <span
                                                                    style={{
                                                                        color:
                                                                            chaosData
                                                                                .lyapunov
                                                                                .lorenz
                                                                                .lambda2 >
                                                                            0
                                                                                ? "#00ff00"
                                                                                : "#ff0000",
                                                                        marginLeft:
                                                                            "10px",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .lorenz.lambda2 >
                                                                    0
                                                                        ? "✓ Positive"
                                                                        : "✗ Negative"}
                                                                </span>
                                                            </p>
                                                            <p
                                                                style={{
                                                                    color: "#fff",
                                                                    marginBottom: "8px",
                                                                }}
                                                            >
                                                                λ₃ ={" "}
                                                                {chaosData.lyapunov.lorenz.exponents[2].toFixed(
                                                                    4
                                                                )}
                                                            </p>
                                                            <p style={{ color: "#fff" }}>
                                                                λ₄ ={" "}
                                                                {chaosData.lyapunov.lorenz.exponents[3].toFixed(
                                                                    4
                                                                )}
                                                            </p>
                                                            <div
                                                                style={{
                                                                    marginTop: "15px",
                                                                    padding: "10px",
                                                                    background: chaosData
                                                                        .lyapunov.lorenz
                                                                        .is_hyperchaotic
                                                                        ? "rgba(0, 255, 0, 0.2)"
                                                                        : "rgba(255, 0, 0, 0.2)",
                                                                    border: `1px solid ${
                                                                        chaosData.lyapunov
                                                                            .lorenz
                                                                            .is_hyperchaotic
                                                                            ? "#00ff00"
                                                                            : "#ff0000"
                                                                    }`,
                                                                }}
                                                            >
                                                                <strong
                                                                    style={{
                                                                        color: chaosData
                                                                            .lyapunov
                                                                            .lorenz
                                                                            .is_hyperchaotic
                                                                            ? "#00ff00"
                                                                            : "#ff0000",
                                                                    }}
                                                                >
                                                                    {chaosData.lyapunov
                                                                        .lorenz
                                                                        .is_hyperchaotic
                                                                        ? "✓ HYPERCHAOTIC"
                                                                        : "✗ NOT HYPERCHAOTIC"}
                                                                </strong>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Bifurcation Diagrams */}
                                    <div style={{ marginTop: "40px" }}>
                                        <h4
                                            style={{
                                                color: "#ff00ff",
                                                marginBottom: "20px",
                                            }}
                                        >
                                            {">"} BIFURCATION DIAGRAMS (Parameter Space
                                            Analysis)
                                        </h4>
                                        <p
                                            style={{
                                                color: "#888",
                                                marginBottom: "20px",
                                                lineHeight: "1.8",
                                            }}
                                        >
                                            Bifurcation diagrams visualize how the system
                                            behavior changes as parameters vary. These
                                            diagrams use the same numerical integration
                                            method as the Lyapunov exponent calculation
                                            (dt=0.01, optimized for fast computation).
                                        </p>
                                        <button
                                            onClick={fetchBifurcationDiagrams}
                                            disabled={isComputingBifurcation}
                                            className="cyber-button"
                                            style={{
                                                width: "100%",
                                                padding: "15px",
                                                fontSize: "1.1rem",
                                                color: "#ff00ff",
                                                borderColor: "#ff00ff",
                                                cursor: isComputingBifurcation
                                                    ? "wait"
                                                    : "pointer",
                                                marginBottom: "30px",
                                            }}
                                        >
                                            {isComputingBifurcation
                                                ? "COMPUTING BIFURCATION DIAGRAMS..."
                                                : "GENERATE BIFURCATION DIAGRAMS"}
                                        </button>

                                        {Object.keys(bifurcationDiagrams).length > 0 && (
                                            <div
                                                style={{
                                                    display: "grid",
                                                    gridTemplateColumns:
                                                        "repeat(auto-fit, minmax(350px, 1fr))",
                                                    gap: "20px",
                                                }}
                                            >
                                                {/* Rössler */}
                                                {bifurcationDiagrams.system1 && (
                                                    <div
                                                        style={{
                                                            padding: "20px",
                                                            background:
                                                                "rgba(0, 255, 255, 0.1)",
                                                            border: "2px solid #00ffff",
                                                        }}
                                                    >
                                                        <h5
                                                            style={{
                                                                color: "#00ffff",
                                                                marginBottom: "15px",
                                                            }}
                                                        >
                                                            Rössler Hyperchaos
                                                        </h5>
                                                        <img
                                                            src={
                                                                bifurcationDiagrams.system1
                                                            }
                                                            alt="Rössler Bifurcation Diagram"
                                                            style={{
                                                                width: "100%",
                                                                height: "auto",
                                                                borderRadius: "4px",
                                                            }}
                                                        />
                                                        <p
                                                            style={{
                                                                color: "#888",
                                                                fontSize: "0.85rem",
                                                                marginTop: "10px",
                                                            }}
                                                        >
                                                            Parameter sweep showing
                                                            chaotic transitions
                                                        </p>
                                                    </div>
                                                )}

                                                {/* Chen */}
                                                {bifurcationDiagrams.system2 && (
                                                    <div
                                                        style={{
                                                            padding: "20px",
                                                            background:
                                                                "rgba(255, 0, 255, 0.1)",
                                                            border: "2px solid #ff00ff",
                                                        }}
                                                    >
                                                        <h5
                                                            style={{
                                                                color: "#ff00ff",
                                                                marginBottom: "15px",
                                                            }}
                                                        >
                                                            Chen Hyperchaos
                                                        </h5>
                                                        <img
                                                            src={
                                                                bifurcationDiagrams.system2
                                                            }
                                                            alt="Chen Bifurcation Diagram"
                                                            style={{
                                                                width: "100%",
                                                                height: "auto",
                                                                borderRadius: "4px",
                                                            }}
                                                        />
                                                        <p
                                                            style={{
                                                                color: "#888",
                                                                fontSize: "0.85rem",
                                                                marginTop: "10px",
                                                            }}
                                                        >
                                                            Parameter sweep showing
                                                            chaotic transitions
                                                        </p>
                                                    </div>
                                                )}

                                                {/* Lorenz */}
                                                {bifurcationDiagrams.system3 && (
                                                    <div
                                                        style={{
                                                            padding: "20px",
                                                            background:
                                                                "rgba(255, 255, 0, 0.1)",
                                                            border: "2px solid #ffff00",
                                                        }}
                                                    >
                                                        <h5
                                                            style={{
                                                                color: "#ffff00",
                                                                marginBottom: "15px",
                                                            }}
                                                        >
                                                            Lorenz Hyperchaos
                                                        </h5>
                                                        <img
                                                            src={
                                                                bifurcationDiagrams.system3
                                                            }
                                                            alt="Lorenz Bifurcation Diagram"
                                                            style={{
                                                                width: "100%",
                                                                height: "auto",
                                                                borderRadius: "4px",
                                                            }}
                                                        />
                                                        <p
                                                            style={{
                                                                color: "#888",
                                                                fontSize: "0.85rem",
                                                                marginTop: "10px",
                                                            }}
                                                        >
                                                            Parameter sweep showing
                                                            chaotic transitions
                                                        </p>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
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
                                    {Object.entries(systemInfo.keys)
                                        .filter(
                                            ([key]) =>
                                                key.startsWith("key") &&
                                                !key.includes("_length")
                                        )
                                        .map(([key, keyBytes], idx) => {
                                            const lengthKey = `${key}_length`;
                                            const totalLength =
                                                systemInfo.keys[lengthKey];
                                            return (
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
                                                        KEY {idx + 1} (First 32 of{" "}
                                                        {totalLength} bytes):
                                                    </p>
                                                    <div
                                                        style={{
                                                            background:
                                                                "rgba(0, 0, 0, 0.8)",
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
                                            );
                                        })}
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
                            <div
                                style={{
                                    padding: "40px",
                                    textAlign: "center",
                                    background: "rgba(0, 0, 0, 0.6)",
                                    border: "2px solid #ffff00",
                                    borderRadius: "10px",
                                }}
                            >
                                <h3 style={{ color: "#ffff00", marginBottom: "20px" }}>
                                    {">"} NO ANALYSIS DATA
                                </h3>
                                <p style={{ color: "#888" }}>
                                    Please complete encryption and decryption first, then
                                    click "ANALYZE PERFORMANCE"
                                </p>
                            </div>
                        )}
                        {activeTab === "analysis" && analysisData && (
                            <div style={{ maxWidth: "1600px", margin: "0 auto" }}>
                                {/* Performance Metrics Summary */}
                                <div
                                    style={{
                                        display: "grid",
                                        gridTemplateColumns:
                                            "repeat(auto-fit, minmax(300px, 1fr))",
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
                                                value: analysisData.mse_plain_encrypted.toFixed(
                                                    2
                                                ),
                                                description:
                                                    "Higher is better (more different)",
                                            },
                                            {
                                                label: "Plain vs Decrypted",
                                                value: analysisData.mse_plain_decrypted.toFixed(
                                                    2
                                                ),
                                                description:
                                                    "Lower is better (0 = perfect)",
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
                                                value: analysisData.ssim_plain_encrypted.toFixed(
                                                    4
                                                ),
                                                description:
                                                    "Lower is better (0 = completely different)",
                                            },
                                            {
                                                label: "Plain vs Decrypted",
                                                value: analysisData.ssim_plain_decrypted.toFixed(
                                                    4
                                                ),
                                                description:
                                                    "Higher is better (1 = identical)",
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
                                                value: analysisData.key_space.key_space_bits.toFixed(
                                                    0
                                                ),
                                                description: `~${analysisData.key_space.comparison_aes256.toFixed(
                                                    1
                                                )}x stronger than AES-256`,
                                            },
                                            {
                                                label: "Total Parameters",
                                                value: analysisData.key_space
                                                    .total_parameters,
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
                                <CorrelationDisplay
                                    correlation={analysisData.correlation}
                                />

                                {/* Noise Resistance */}
                                <NoiseResistanceDisplay
                                    noiseData={analysisData.noise_resistance}
                                />

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
                <p
                    style={{
                        color,
                        fontSize: "1.5rem",
                        fontWeight: "bold",
                        marginBottom: "5px",
                    }}
                >
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
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "20px",
            }}
        >
            {["original", "encrypted", "decrypted"].map((type) => (
                <div key={type} style={{ textAlign: "center" }}>
                    <p
                        style={{
                            color: "#888",
                            fontSize: "0.9rem",
                            marginBottom: "10px",
                            textTransform: "uppercase",
                        }}
                    >
                        {type}
                    </p>
                    <p style={{ color: "#00ffff", fontSize: "2rem", fontWeight: "bold" }}>
                        {entropy[type].Overall.toFixed(4)}
                    </p>
                    <div style={{ marginTop: "10px", fontSize: "0.8rem" }}>
                        {entropy[type].Red !== undefined && (
                            <>
                                <p style={{ color: "#ff6666" }}>
                                    R: {entropy[type].Red.toFixed(3)}
                                </p>
                                <p style={{ color: "#66ff66" }}>
                                    G: {entropy[type].Green.toFixed(3)}
                                </p>
                                <p style={{ color: "#6666ff" }}>
                                    B: {entropy[type].Blue.toFixed(3)}
                                </p>
                            </>
                        )}
                    </div>
                </div>
            ))}
        </div>
        <p
            style={{
                color: "#666",
                fontSize: "0.85rem",
                marginTop: "20px",
                textAlign: "center",
            }}
        >
            Maximum entropy is 8.0 bits/pixel. Higher entropy = better randomness
        </p>
    </div>
);

const HistogramDisplay = ({ histograms }) => {
    const HistogramChart = ({ data, title, color }) => {
        // Calculate max per channel for better scaling
        const maxRed = Math.max(...data.Red.values);
        const maxGreen = Math.max(...data.Green.values);
        const maxBlue = Math.max(...data.Blue.values);

        // Use a reasonable sampling to show 64 bars (every 4th value)
        const sampleRate = 4;
        const sampledIndices = data.Red.values
            .map((_, idx) => idx)
            .filter((idx) => idx % sampleRate === 0);

        return (
            <div style={{ marginBottom: "30px" }}>
                <h4 style={{ color, marginBottom: "15px", fontSize: "1rem" }}>{title}</h4>
                {/* Red Channel */}
                <div style={{ marginBottom: "10px" }}>
                    <span style={{ color: "rgba(255, 100, 100, 0.9)", fontSize: "0.75rem" }}>Red</span>
                    <div
                        style={{
                            display: "flex",
                            height: "60px",
                            alignItems: "flex-end",
                            background: "rgba(0, 0, 0, 0.3)",
                            padding: "2px",
                            borderRadius: "2px",
                        }}
                    >
                        {sampledIndices.map((idx) => {
                            const height = maxRed > 0 ? (data.Red.values[idx] / maxRed) * 100 : 0;
                            return (
                                <div
                                    key={idx}
                                    style={{
                                        flex: 1,
                                        height: `${Math.max(height, 1)}%`,
                                        background: "rgba(255, 100, 100, 0.8)",
                                        marginRight: "1px",
                                    }}
                                />
                            );
                        })}
                    </div>
                </div>
                {/* Green Channel */}
                <div style={{ marginBottom: "10px" }}>
                    <span style={{ color: "rgba(100, 255, 100, 0.9)", fontSize: "0.75rem" }}>Green</span>
                    <div
                        style={{
                            display: "flex",
                            height: "60px",
                            alignItems: "flex-end",
                            background: "rgba(0, 0, 0, 0.3)",
                            padding: "2px",
                            borderRadius: "2px",
                        }}
                    >
                        {sampledIndices.map((idx) => {
                            const height = maxGreen > 0 ? (data.Green.values[idx] / maxGreen) * 100 : 0;
                            return (
                                <div
                                    key={idx}
                                    style={{
                                        flex: 1,
                                        height: `${Math.max(height, 1)}%`,
                                        background: "rgba(100, 255, 100, 0.8)",
                                        marginRight: "1px",
                                    }}
                                />
                            );
                        })}
                    </div>
                </div>
                {/* Blue Channel */}
                <div>
                    <span style={{ color: "rgba(100, 100, 255, 0.9)", fontSize: "0.75rem" }}>Blue</span>
                    <div
                        style={{
                            display: "flex",
                            height: "60px",
                            alignItems: "flex-end",
                            background: "rgba(0, 0, 0, 0.3)",
                            padding: "2px",
                            borderRadius: "2px",
                        }}
                    >
                        {sampledIndices.map((idx) => {
                            const height = maxBlue > 0 ? (data.Blue.values[idx] / maxBlue) * 100 : 0;
                            return (
                                <div
                                    key={idx}
                                    style={{
                                        flex: 1,
                                        height: `${Math.max(height, 1)}%`,
                                        background: "rgba(100, 100, 255, 0.8)",
                                        marginRight: "1px",
                                    }}
                                />
                            );
                        })}
                    </div>
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
            <HistogramChart
                data={histograms.original}
                title="Original Image"
                color="#00ffff"
            />
            <HistogramChart
                data={histograms.encrypted}
                title="Encrypted Image"
                color="#ff00ff"
            />
            <HistogramChart
                data={histograms.decrypted}
                title="Decrypted Image"
                color="#00ff00"
            />
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
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "20px",
            }}
        >
            {["horizontal", "vertical", "diagonal"].map((direction) => (
                <div key={direction} style={{ textAlign: "center" }}>
                    <p
                        style={{
                            color: "#888",
                            fontSize: "0.9rem",
                            marginBottom: "10px",
                            textTransform: "uppercase",
                        }}
                    >
                        {direction}
                    </p>
                    <div style={{ marginBottom: "15px" }}>
                        <p style={{ color: "#666", fontSize: "0.75rem" }}>Original</p>
                        <p
                            style={{
                                color: "#00ffff",
                                fontSize: "1.2rem",
                                fontWeight: "bold",
                            }}
                        >
                            {correlation.original[direction].correlation.toFixed(4)}
                        </p>
                    </div>
                    <div>
                        <p style={{ color: "#666", fontSize: "0.75rem" }}>Encrypted</p>
                        <p
                            style={{
                                color: "#ff00ff",
                                fontSize: "1.2rem",
                                fontWeight: "bold",
                            }}
                        >
                            {correlation.encrypted[direction].correlation.toFixed(4)}
                        </p>
                    </div>
                </div>
            ))}
        </div>
        <p
            style={{
                color: "#666",
                fontSize: "0.85rem",
                marginTop: "20px",
                textAlign: "center",
            }}
        >
            Encrypted images should have correlation close to 0 (no correlation between
            adjacent pixels)
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
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "20px",
            }}
        >
            {noiseData.map((result, idx) => (
                <div
                    key={idx}
                    style={{
                        padding: "15px",
                        background: "rgba(0, 0, 0, 0.4)",
                        border: "1px solid #00ff00",
                    }}
                >
                    <p
                        style={{
                            color: "#00ff00",
                            fontSize: "1rem",
                            marginBottom: "10px",
                            fontWeight: "bold",
                        }}
                    >
                        Noise: {result.noise_level}
                    </p>
                    {result.error ? (
                        <p style={{ color: "#ff6666", fontSize: "0.85rem" }}>
                            Error: {result.error}
                        </p>
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
                                MSE:{" "}
                                <span style={{ color: "#00ff00" }}>
                                    {result.mse.toFixed(2)}
                                </span>
                            </p>
                            <p style={{ color: "#888", fontSize: "0.75rem" }}>
                                SSIM:{" "}
                                <span style={{ color: "#00ff00" }}>
                                    {result.ssim.toFixed(4)}
                                </span>
                            </p>
                            <p style={{ color: "#888", fontSize: "0.75rem" }}>
                                PSNR:{" "}
                                <span style={{ color: "#00ff00" }}>
                                    {result.psnr.toFixed(2)} dB
                                </span>
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
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: "20px",
            }}
        >
            {["original", "encrypted", "decrypted"].map((type) => (
                <div
                    key={type}
                    style={{
                        padding: "20px",
                        background: "rgba(0, 0, 0, 0.4)",
                        border: "1px solid #00ffff",
                    }}
                >
                    <h4
                        style={{
                            color: "#00ffff",
                            marginBottom: "15px",
                            textTransform: "uppercase",
                        }}
                    >
                        {type}
                    </h4>
                    {Object.entries(stats[type]).map(([key, value]) => (
                        <p
                            key={key}
                            style={{
                                color: "#888",
                                fontSize: "0.8rem",
                                marginBottom: "5px",
                            }}
                        >
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
