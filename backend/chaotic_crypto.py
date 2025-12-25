"""
Hyperchaotic Cryptography System (Corrected & Stabilized)
Academic-grade reference implementation
"""

import numpy as np
from scipy.integrate import odeint
import hashlib
from PIL import Image


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

        ones = np.sum(stream)
        zeros = len(stream) - ones

        print(f"    ↳ Bitstream length: {len(stream)}")
        print(f"    ↳ Balance: 1s={ones} | 0s={zeros} | bias={abs(ones-zeros)/len(stream):.4f}")

        return stream

    def equations(self, state, t, *params):
        raise NotImplementedError


# =========================================================
# Hyperchaotic Systems (Validated Forms)
# =========================================================

class RosslerHyperchaos(HyperchaosSystem):
    def equations(self, s, t, a, b, c, d):
        x, y, z, w = s
        return [
            -y - z,
            x + a*y + w,
            b + z*(x - c),
            -d*z
        ]


class ChenHyperchaos(HyperchaosSystem):
    def equations(self, s, t, a, b, c, d):
        x, y, z, w = s
        return [
            a*(y - x),
            (c - a)*x - x*z + c*y + w,
            x*y - b*z,
            -d*z
        ]


class LorenzHyperchaos(HyperchaosSystem):
    def equations(self, s, t, sigma, r, b, k):
        x, y, z, w = s
        return [
            sigma*(y - x) + w,
            r*x - y - x*z,
            x*y - b*z,
            -k*y
        ]


# =========================================================
# Cryptographic Core
# =========================================================

class ChaoticCrypto:
    def __init__(self, seed="secure-seed"):

        seed_int = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % 2**32
        np.random.seed(seed_int)

        self.systems = [
            RosslerHyperchaos(
                "Rössler Hyperchaos",
                [0.1, 0.0, 0.1, 0.0],
                [0.25, 3.0, 5.7, 0.05]
            ),
            ChenHyperchaos(
                "Chen Hyperchaos",
                [0.2, 0.1, 0.1, 0.0],
                [35, 3, 28, 5]
            ),
            LorenzHyperchaos(
                "Lorenz Hyperchaos",
                [0.1, 0.0, 0.0, 0.1],
                [10, 28, 8/3, 1.0]
            )
        ]

        self.bitstreams = []
        self.keys = []
        self.sboxes = []

        for sys in self.systems:
            sys.solve()
            bits = sys.to_bitstream()
            self.bitstreams.append(bits)
            self.keys.append(self.generate_key(bits))
            self.sboxes.append(self.generate_sbox(bits))

    def generate_key(self, bits):
        bits = bits[:len(bits)//8 * 8]
        key = np.packbits(bits)
        digest = hashlib.sha256(key).digest()
        print(f"    ↳ Key SHA-256: {digest.hex()[:32]}...")
        return digest

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
        out = bytearray()
        ctr = 0
        while len(out) < n:
            h = hashlib.sha256(key + ctr.to_bytes(8, "big")).digest()
            out.extend(h)
            ctr += 1
        return bytes(out[:n])

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