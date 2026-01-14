"""
Hyperchaotic Cryptography System (Corrected & Stabilized)
Academic-grade reference implementation
"""

import numpy as np
from scipy.integrate import odeint
import hashlib
from PIL import Image
import os
import base64
import io
import matplotlib
matplotlib.use("Agg")   # must be BEFORE pyplot
import matplotlib.pyplot as plt



# =========================================================
# Base Hyperchaotic System
# =========================================================

class HyperchaosSystem:
    def __init__(self, name, initial_conditions, parameters,
                 t_max=100.0, points=60000, transient=5000):

        self.name = name
        self.ic = np.array(initial_conditions, dtype=np.float64)
        self.params = tuple(parameters)

        self.t = np.linspace(0, t_max, points)
        self.transient = transient
        self.solution = None

    def solve(self):
        print(f"[+] Solving {self.name} system...")
        sol = odeint(
            lambda s, t: self.equations(s, t, *self.params),
            self.ic,
            self.t,
            atol=1e-9,
            rtol=1e-9
        )

        self.solution = sol[self.transient:]  # remove transient
        print(f"    ↳ {self.solution.shape[0]} valid samples retained")
        return self.solution

    def to_bitstream(self):
        if self.solution is None:
            self.solve()

        print(f"[+] Generating bitstream from {self.name}...")

        stream = np.zeros(len(self.solution), dtype=np.uint8)

        for i in range(self.solution.shape[1]):
            x = self.solution[:, i]
            x = (x - x.min()) / (x.max() - x.min() + 1e-12)
            bytes_ = np.floor(x * 256).astype(np.uint8)
            stream ^= (bytes_ & 1)

        ones = int(np.sum(stream))
        zeros = len(stream) - ones

        print(f"    ↳ Bitstream length: {len(stream)}")
        print(f"    ↳ Balance: 1s={ones} | 0s={zeros} | bias={abs(ones-zeros)/len(stream):.4f}")

        return stream

    def equations(self, state, t, *params):
        raise NotImplementedError

    def jacobian(self, state, *params):
        """Compute Jacobian matrix for Lyapunov exponent calculation"""
        raise NotImplementedError

    def compute_lyapunov_spectrum(self, n_iterations=10000, dt=0.01):
        """
        Calculate Lyapunov exponents using the QR decomposition method.
        Returns: array of Lyapunov exponents sorted in descending order
        """
        print(f"[+] Computing Lyapunov spectrum for {self.name}...")

        dim = len(self.ic)
        state = self.ic.copy()

        # Initialize orthonormal basis
        Q = np.eye(dim)
        lyap_sum = np.zeros(dim)

        for i in range(n_iterations):
            # Integrate system
            sol = odeint(
                lambda s, t: self.equations(s, t, *self.params),
                state,
                [0, dt],
                atol=1e-9,
                rtol=1e-9
            )
            state = sol[-1]

            # Compute Jacobian at current state
            J = self.jacobian(state, *self.params)

            # Propagate tangent vectors
            Q = J @ Q

            # QR decomposition
            Q, R = np.linalg.qr(Q)

            # Accumulate Lyapunov exponents
            lyap_sum += np.log(np.abs(np.diag(R)))

        # Calculate Lyapunov exponents
        lyap_exp = lyap_sum / (n_iterations * dt)
        lyap_exp = np.sort(lyap_exp)[::-1]  # Sort descending

        print(f"    ↳ Lyapunov exponents: {lyap_exp}")
        print(f"    ↳ λ₁ = {lyap_exp[0]:.4f} (λ₁ > 0: {'✓' if lyap_exp[0] > 0 else '✗'})")
        print(f"    ↳ λ₂ = {lyap_exp[1]:.4f} (λ₂ > 0: {'✓' if lyap_exp[1] > 0 else '✗'})")
        print(f"    ↳ Hyperchaotic: {'YES ✓' if lyap_exp[0] > 0 and lyap_exp[1] > 0 else 'NO ✗'}")

        return lyap_exp
    
    def compute_bifurcation_diagram(self, param_index=0, param_range=None,
                                    samples=100, n_iterations=500, dt=0.01):
        """
        Compute bifurcation diagram by varying one parameter.
        Uses the same integration approach as Lyapunov exponent calculation.

        param_index: which parameter to vary (0, 1, 2, or 3)
        param_range: tuple of (min, max) for parameter sweep
        samples: number of parameter values to test
        n_iterations: number of iterations per parameter value
        dt: time step for integration (same as Lyapunov)
        Returns: matplotlib figure as base64 encoded image
        """

        print(f"[+] Computing bifurcation diagram for {self.name} (param {param_index})...")

        if param_range is None:
            # Default ranges for each system type
            param_range = (self.params[param_index] * 0.5, self.params[param_index] * 1.5)

        param_vals = np.linspace(param_range[0], param_range[1], samples)

        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

        for param_val in param_vals:
            # Update parameter
            params = list(self.params)
            params[param_index] = param_val
            params = tuple(params)

            # Start from initial conditions (same as Lyapunov)
            state = self.ic.copy()

            # Transient removal phase - discard first 50% of iterations
            transient = n_iterations // 2

            # Storage for bifurcation points
            bifurc_points = []

            # Integrate using same method as Lyapunov computation
            for i in range(n_iterations):
                sol = odeint(
                    lambda s, t: self.equations(s, t, *params),
                    state,
                    [0, dt],
                    atol=1e-9,
                    rtol=1e-9
                )
                state = sol[-1]

                # Collect points after transient (first state variable)
                if i >= transient:
                    bifurc_points.append(state[0])

            # Plot all collected points
            ax.plot([param_val] * len(bifurc_points), bifurc_points, ',k', alpha=0.3, markersize=0.5)

        ax.set_xlabel(f"Parameter {param_index} (nominal: {self.params[param_index]:.4f})")
        ax.set_ylabel(f"{self.name} - State Variable x")
        ax.set_title(f"Bifurcation Diagram: {self.name}")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        print(f"    ↳ Bifurcation diagram generated ({samples} parameter values, {n_iterations} iterations each)")
        return img_base64
    
class RosslerHyperchaos(HyperchaosSystem):
    def equations(self, s, t, a, b, c, d):
        x, y, z, w = s
        return [
            -y - z,
            x + a*y + w,
            b + z*x,
            -c*z + d*w
        ]

    def jacobian(self, state, *params):
        a, b, c, d = params
        x, y, z, w = state
        return np.array([
            [0,  -1,  -1,   0],
            [1,   a,   0,   1],
            [z,   0,   x,   0],
            [0,   0,  -c,   d]
        ])
class ShakirEtal(HyperchaosSystem):
    def equations(self, s, t, a, b, c, d, e, f, g, h, i, j):
        x, y, z, w = s

        dx = -a * x - b * w + c * y * z + z * np.exp(y)
        dy = d * y + e * x - f * x * z - x * np.exp(z)
        dz = -g * z + h * x * y
        dw = -b * w + i * x * z + j * y * z

        return [dx, dy, dz, dw]

    def jacobian(self, state, *params):
        a, b, c, d, e, f, g, h, i, j = params
        x, y, z, w = state

        # Compute Jacobian matrix J where J[i,j] = ∂f_i/∂x_j
        # f = [dx, dy, dz, dw]
        # state = [x, y, z, w]

        return np.array([
            [-a,                c*z + np.exp(y),     c*y + np.exp(y),    -b],
            [e - np.exp(z),     d,                   -f*x - x*np.exp(z), 0],
            [h*y,               h*x,                 -g,                 0],
            [i*z,               j*z,                 i*x + j*y,          -b]
        ])

class ChenHyperchaos(HyperchaosSystem):
    """
    Fractional-order 4D Chen system
    Equations:
        D^α x = a(y - x) + u
        D^α y = γx - xz + cy
        D^α z = xy - bz
        D^α u = yz + du

    Parameters from literature: a=35, b=3, c=12, γ=28, d=0.5, α=0.97
    Initial conditions: {x,y,z,u} = 0.3
    """
    def equations(self, s, t, a, b, c, gamma, d):
        x, y, z, u = s
        return [
            a*(y - x) + u,           # D^α x
            gamma*x - x*z + c*y,     # D^α y
            x*y - b*z,               # D^α z
            y*z + d*u                # D^α u
        ]

    def jacobian(self, state, *params):
        a, b, c, gamma, d = params
        x, y, z, u = state
        return np.array([
            [-a,      a,      0,   1],
            [gamma-z, c,     -x,   0],
            [y,       x,     -b,   0],
            [0,       z,      y,   d]
        ])


class LorenzHyperchaos(HyperchaosSystem):
    def equations(self, s, t, sigma, r, b, k):
        x, y, z, w = s
        return [
            sigma*(y - x) + w,
            r*x - y - x*z,
            x*y - b*z,
            -k*y
        ]

    def jacobian(self, state, *params):
        sigma, r, b, k = params
        x, y, z, w = state
        return np.array([
            [-sigma,  sigma,   0,   1],
            [r-z,     -1,     -x,   0],
            [y,        x,     -b,   0],
            [0,       -k,      0,   0]
        ])


# =========================================================
# Cryptographic Core
# =========================================================

class ChaoticCrypto:
    def __init__(self, seed="secure-seed", initial_conditions=None):

        seed_int = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % 2**32
        np.random.seed(seed_int)
        # Use custom initial conditions if provided
        if initial_conditions is None:
            # Rössler hyperchaos: proven parameters from literature
            # Reference: Rössler (1979), a=0.25, b=3.0, c=0.5, d=0.05

            ic1 = [-10, -6, 0, 10]          # Rössler
            ic2 = [0.3, 0.3, 0.3, 0.3]      # Chen: {x,y,z,u} = 0.3
            ic3 = [0.1, 0.0, 0.0, 0.1]      # Lorenz: works well
        else:
            ic1 = initial_conditions.get('system1', [0.25, 3.0, 5.7, 0.05])
            ic2 = initial_conditions.get('system2', [0.2, 0.1, 0.1, 0.0])
            ic3 = initial_conditions.get('system3', [0.1, 0.0, 0.0, 0.1])

        self.system1 = RosslerHyperchaos(
            "Rössler Hyperchaos",
            ic1,
            [0.25, 3.0, 0.5, 0.05]  # Classic Rössler hyperchaos parameters
        )

        # Fractional-order 4D Chen system
        # Parameters: a=35, b=3, c=12, γ=28, d=0.5, α=0.97
        # Initial conditions: {x,y,z,u} = 0.3
        self.system2 = ChenHyperchaos(
            "Chen Hyperchaos",
            ic2,
            [35, 3, 12, 28, 0.5]  # a, b, c, gamma, d
        )

        # Commented out - replaced by Chen system
        # self.system2 = ShakirEtal("Shakir et al.",
        #                           ic2,[
        #     3.1,
        #     2.1,
        #     15.8,
        #     1.1,
        #     16.5,
        #     1.5,
        #     2.4,
        #     26.6,
        #     5.1,
        #     12.9
        # ])
        self.system3 = LorenzHyperchaos(
            "Lorenz Hyperchaos",
            ic3,
            [10, 28, 8/3, 1.0]
        )

        self.systems = [self.system1, self.system2, self.system3]

        # Solve systems and generate crypto materials
        self.system1.solve()
        self.system2.solve()
        self.system3.solve()

        self.bitstream1 = self.system1.to_bitstream()
        self.bitstream2 = self.system2.to_bitstream()
        self.bitstream3 = self.system3.to_bitstream()

        self.bitstreams = [self.bitstream1, self.bitstream2, self.bitstream3]

        # Convert bitstreams to byte arrays (keys are the bitstreams themselves)
        self.key1 = self.bitstream_to_bytes(self.bitstream1)
        self.key2 = self.bitstream_to_bytes(self.bitstream2)
        self.key3 = self.bitstream_to_bytes(self.bitstream3)

        self.keys = [self.key1, self.key2, self.key3]

        print(f"    ↳ Key 1 length: {len(self.key1)} bytes ({len(self.bitstream1)} bits)")
        print(f"    ↳ Key 2 length: {len(self.key2)} bytes ({len(self.bitstream2)} bits)")
        print(f"    ↳ Key 3 length: {len(self.key3)} bytes ({len(self.bitstream3)} bits)")

        self.sbox1 = self.generate_sbox(self.bitstream1)
        self.sbox2 = self.generate_sbox(self.bitstream2)
        self.sbox3 = self.generate_sbox(self.bitstream3)

        self.sboxes = [self.sbox1, self.sbox2, self.sbox3]

    def bitstream_to_bytes(self, bits):
        """Convert bitstream to bytes by packing every 8 bits"""
        # Trim to multiple of 8
        bits = bits[:len(bits)//8 * 8]
        # Pack bits into bytes
        byte_array = np.packbits(bits)
        return bytes(byte_array)

    def generate_sbox(self, bits, size=256):
        sbox = np.arange(size, dtype=np.uint8)
        idx = 0

        for i in range(size-1, 0, -1):
            b = bits[idx:idx+8]
            idx = (idx + 8) % len(bits)
            j = int("".join(map(str, b)), 2) % (i+1)
            sbox[i], sbox[j] = sbox[j], sbox[i]

        return sbox

    def extend_key(self, key, n):
        """Extend or truncate the chaotic keystream to match data length using hash chaining"""
        if len(key) >= n:
            # If key is longer than needed, just use the first n bytes
            return key[:n]
        else:
            # If key is shorter, use hash chaining to extend it
            # This prevents predictable patterns from simple repetition
            extended = bytearray(key)
            counter = 0

            while len(extended) < n:
                # Create a hash from: original key + current extended portion + counter
                # This ensures each block depends on all previous blocks
                hash_input = key + bytes(extended[-min(32, len(extended)):]) + counter.to_bytes(4, 'big')
                hash_output = hashlib.sha256(hash_input).digest()
                extended.extend(hash_output)
                counter += 1

            return bytes(extended[:n])

    def xor(self, data, key):
        k = np.frombuffer(self.extend_key(key, len(data)), dtype=np.uint8)
        return np.bitwise_xor(data, k)

    def encrypt(self, img, rounds=3):
        data = img.flatten()
        for r in range(rounds):
            i = r % 3
            print(f"[+] Encryption round {r+1} → {self.systems[i].name}")
            data = self.xor(data, self.keys[i])
            data = self.sboxes[i][data]
        return data.reshape(img.shape)

    def decrypt(self, img, shape, rounds=3):
        data = img.flatten()
        for r in reversed(range(rounds)):
            i = r % 3
            inv = np.argsort(self.sboxes[i])
            data = inv[data]
            data = self.xor(data, self.keys[i])
        return data.reshape(shape)

    def get_system_info(self):
        """Return information about the chaotic systems"""
        return {
            'system1': {
                'name': self.system1.name,
                'initial_conditions': self.system1.ic.tolist(),
                'parameters': list(self.system1.params)
            },
            'system2': {
                'name': self.system2.name,
                'initial_conditions': self.system2.ic.tolist(),
                'parameters': list(self.system2.params)
            },
            'system3': {
                'name': self.system3.name,
                'initial_conditions': self.system3.ic.tolist(),
                'parameters': list(self.system3.params)
            }
        }

    def encrypt_image(self, img, rounds=3):
        """Encrypt an image (alias for encrypt method)"""
        return self.encrypt(img, rounds)

    def decrypt_image(self, img, shape, rounds=3):
        """Decrypt an image (alias for decrypt method)"""
        return self.decrypt(img, shape, rounds)


# =========================================================
# Demo
# =========================================================

def demo():
    print("="*70)
    print("HYPERCHAOTIC IMAGE ENCRYPTION DEMO")
    print("="*70)

    crypto = ChaoticCrypto(seed="academic-test-seed")

    img = np.zeros((128, 128, 3), dtype=np.uint8)
    for i in range(128):
        for j in range(128):
            img[i, j] = [i, j, (i+j)//2]

    enc = crypto.encrypt(img)
    dec = crypto.decrypt(enc, img.shape)

    print("\n[+] Verification:")
    print("    Encrypted stats → mean:", enc.mean(), "std:", enc.std())
    print("    Decryption correct:", np.array_equal(img, dec))


if __name__ == "__main__":
    demo()