"""
Hyperchaotic Cryptography System
Implements three different hyperchaotic systems for image encryption
"""

import numpy as np
from scipy.integrate import odeint
import hashlib
from PIL import Image
import io
import base64

class HyperchaosSystem:
    """Base class for hyperchaotic systems"""
    
    def __init__(self, initial_conditions, parameters, time_points=100000):
        self.ic = np.array(initial_conditions)
        self.params = parameters
        self.t = np.linspace(0, 100, time_points)
        self.solution = None
        
    def solve(self):
        """Solve the differential equations"""
        self.solution = odeint(self.equations, self.ic, self.t, args=(self.params,))
        return self.solution
    
    def to_bitstream(self):
        """Convert solution to bit-stream using threshold method"""
        if self.solution is None:
            self.solve()

        # Normalize the selected variable
        result_bits = np.zeros(len(self.solution), dtype=int)
        for variable_index in range(3):
            data = self.solution[:, variable_index]
            normalized = (data - np.min(data)) / (np.max(data) - np.min(data))
            median = np.median(normalized)
            bits = (normalized > median).astype(int)
            result_bits = np.bitwise_xor(result_bits, bits) 
        print("Bitstream length:", len(bits), " 1s:", np.sum(bits), " 0s:", len(bits)-np.sum(bits))
        return result_bits


    def equations(self, state, t, params):
        """Override in subclasses"""
        raise NotImplementedError


class RosslerHyperchaos(HyperchaosSystem):
    """4D Rössler Hyperchaotic System"""
    
    def equations(self, state, t, params):
        x, y, z, w = state
        a, b, c, d = params
        
        dx = -y - z
        dy = x + a * y + w
        dz = b + x * z
        dw = -c * z + d * w
        
        return [dx, dy, dz, dw]


class ChenHyperchaos(HyperchaosSystem):
    """4D Chen Hyperchaotic System"""
    
    def equations(self, state, t, params):
        x, y, z, w = state
        a, b, c, d, r = params
        
        dx = a * (y - x) + w
        dy = d * x - x * z + c * y
        dz = x * y - b * z
        dw = x * z + r * w
        
        return [dx, dy, dz, dw]


class LorenzHyperchaos(HyperchaosSystem):
    """4D Hyperchaotic Lorenz System"""
    
    def equations(self, state, t, params):
        x, y, z, w = state
        sigma, r, b, k = params
        
        dx = sigma * (y - x) + w
        dy = r * x - y - x * z
        dz = x * y - b * z
        dw = -x * z + k * w
        
        return [dx, dy, dz, dw]


class ChaoticCrypto:
    """Main encryption system using hyperchaotic systems"""

    def __init__(self, seed="default_seed", initial_conditions=None ):
        """
        Initialize with three hyperchaotic systems

        Args:
            seed (str): Seed for random initialization
            initial_conditions (dict): Custom initial conditions for each system
            bitstream_method (str): Method for bitstream generation
                - 'single_var': Legacy single-variable threshold method
                - 'pairwise_xor': Multi-variable pairwise XOR [recommended, default]
                - 'full_xor': All variables XORed together
                - 'selective_xor': XOR first 3 variables
        """
        # Use seed to generate initial conditions
        np.random.seed(int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32))

        # Default initial conditions
        if initial_conditions is None:
            initial_conditions = {
                'system1': [0.1, 0.1, 0.1, 0.1],
                'system2': [1.0, 1.0, 1.0, 1.0],
                'system3': [1.0, 1.0, 1.0, 1.0]
            }

        # System 1: Rössler Hyperchaos
        self.system1 = RosslerHyperchaos(
            initial_conditions=initial_conditions.get('system1', [0.1, 0.1, 0.1, 0.1]),
            parameters=[0.25, 3.0, 0.5, 0.05]
        )

        # System 2: Chen Hyperchaos
        self.system2 = ChenHyperchaos(
            initial_conditions=initial_conditions.get('system2', [1.0, 1.0, 1.0, 1.0]),
            parameters=[36, 3, 28, -16, -0.7]
        )

        # System 3: Lorenz Hyperchaos
        self.system3 = LorenzHyperchaos(
            initial_conditions=initial_conditions.get('system3', [1.0, 1.0, 1.0, 1.0]),
            parameters=[10, 28, 8/3, -1]
        )
        
        # Solve all systems
        print("Solving hyperchaotic systems...")
        self.system1.solve()
        self.system2.solve()
        self.system3.solve()
        print("Systems solved!")
        
        # Generate bit-streams
        self.bitstream1 = self.system1.to_bitstream()
        self.bitstream2 = self.system2.to_bitstream()
        self.bitstream3 = self.system3.to_bitstream()

        # Generate encryption keys
        self.key1 = self.generate_key(self.bitstream1)
        self.key2 = self.generate_key(self.bitstream2)
        self.key3 = self.generate_key(self.bitstream3)
        
        # Generate S-boxes
        self.sbox1 = self.generate_sbox(self.bitstream1)
        self.sbox2 = self.generate_sbox(self.bitstream2)
        self.sbox3 = self.generate_sbox(self.bitstream3)
        
    def generate_key(self, bitstream):
        """Generate encryption key from bit-stream"""
        # Take key_length bits and convert to bytes

        key_bits = bitstream[:len(bitstream)//8*8]

        key_bytes = np.packbits(key_bits)
        print("Key length (bytes):", len(key_bytes), " bytes sum:", np.sum(key_bytes))
        print("Key sample (first 16 bytes):", key_bytes[:70])
        return key_bytes
    
    def extend_key(self, key, length):
        """Extend key to desired length using a stream cipher approach"""
        # Ensure key is bytes
        if isinstance(key, np.ndarray):
            key_bytes = key.tobytes()
        else:
            key_bytes = bytes(key)

        # Use SHA256 in counter mode to generate a stream
        extended = bytearray()
        counter = 0

        while len(extended) < length:
            # Hash key + counter to generate pseudo-random bytes
            h = hashlib.sha256()
            h.update(key_bytes)
            h.update(counter.to_bytes(8, 'big'))
            h.update(b"key-expansion")
            extended.extend(h.digest())
            counter += 1

        return bytes(extended[:length])
    
    def generate_sbox(self, bitstream, size=256):
        """Generate S-box from bit-stream using Fisher-Yates shuffle"""
        # Create initial permutation
        sbox = np.arange(size)
        
        # Use bitstream to generate pseudo-random indices
        bit_index = 0
        for i in range(size - 1, 0, -1):
            # Take enough bits to represent index
            bits_needed = int(np.ceil(np.log2(i + 1)))
            if bit_index + bits_needed > len(bitstream):
                bit_index = 0  # Wrap around
            
            # Convert bits to integer
            bits = bitstream[bit_index:bit_index + bits_needed]
            j = int(''.join(map(str, bits)), 2) % (i + 1)
            bit_index += bits_needed
            
            # Swap
            sbox[i], sbox[j] = sbox[j], sbox[i]
        
        return sbox
    
    def apply_sbox(self, data, sbox):
        """Apply S-box substitution"""
        return np.array([sbox[byte] for byte in data], dtype=np.uint8)
    
    def apply_inverse_sbox(self, data, sbox):
        """Apply inverse S-box substitution"""
        inverse_sbox = np.argsort(sbox)
        return np.array([inverse_sbox[byte] for byte in data], dtype=np.uint8)
    
    def xor_with_key(self, data, key):
        """XOR data with key (key is repeated if needed)"""
        print("expanding the xor key...")
        key_expanded = np.frombuffer(self.extend_key(key, len(data)), dtype=np.uint8)
        return np.bitwise_xor(data, key_expanded)
    
    def encrypt_image(self, image_data, rounds=3):
        """
        Encrypt image using successive application of keys and S-boxes
        
        Encryption process for each round:
        1. XOR with key
        2. Apply S-box substitution
        """
        # Convert image to numpy array
        img_array = np.array(image_data).flatten()
        encrypted = img_array.copy()
        
        keys = [self.key1, self.key2, self.key3]
        sboxes = [self.sbox1, self.sbox2, self.sbox3]
        
        print(f"Encrypting with {rounds} rounds...")
        for round_num in range(rounds):
            key_idx = round_num % 3
            print(f"  Round {round_num + 1}: Using system {key_idx + 1}")
            
            # XOR with key
            print("Xoring....")
            encrypted = self.xor_with_key(encrypted, keys[key_idx])
            
            
            # Apply S-box
            print("subsituting....")
            encrypted = self.apply_sbox(encrypted, sboxes[key_idx])
        
        # Reshape back to original image shape
        original_shape = np.array(image_data).shape
        encrypted_img = encrypted.reshape(original_shape)
        
        return encrypted_img
    
    def decrypt_image(self, encrypted_data, original_shape, rounds=3):
        """
        Decrypt image by reversing the encryption process
        """
        encrypted = np.array(encrypted_data).flatten()
        decrypted = encrypted.copy()
        
        keys = [self.key1, self.key2, self.key3]
        sboxes = [self.sbox1, self.sbox2, self.sbox3]
        
        print(f"Decrypting with {rounds} rounds...")
        # Decrypt in reverse order
        for round_num in range(rounds - 1, -1, -1):
            key_idx = round_num % 3
            print(f"  Round {rounds - round_num}: Reversing system {key_idx + 1}")
            
            # Apply inverse S-box
            decrypted = self.apply_inverse_sbox(decrypted, sboxes[key_idx])
            
            # XOR with key (XOR is its own inverse)
            decrypted = self.xor_with_key(decrypted, keys[key_idx])
        
        # Reshape back to original image shape
        decrypted_img = decrypted.reshape(original_shape)
        
        return decrypted_img
    
    def get_system_info(self):
        """Get information about the three systems"""
        return {
            "system1": {
                "name": "Rössler Hyperchaos",
                "dimensions": 4,
                "parameters": self.system1.params,
                "initial_conditions": self.system1.ic.tolist()
            },
            "system2": {
                "name": "Chen Hyperchaos",
                "dimensions": 4,
                "parameters": self.system2.params,
                "initial_conditions": self.system2.ic.tolist()
            },
            "system3": {
                "name": "Hyperchaotic Lorenz",
                "dimensions": 4,
                "parameters": self.system3.params,
                "initial_conditions": self.system3.ic.tolist()
            }
        }


def demo():
    """Demonstration of the system"""
    print("=" * 60)
    print("Hyperchaotic Cryptography System Demo")
    print("=" * 60)
    
    # Initialize crypto system
    crypto = ChaoticCrypto(seed="my_secret_seed")
    
    # Display system information
    info = crypto.get_system_info()
    print("\n" + "=" * 60)
    print("HYPERCHAOTIC SYSTEMS")
    print("=" * 60)
    for system_name, system_info in info.items():
        print(f"\n{system_info['name']}:")
        print(f"  Dimensions: {system_info['dimensions']}")
        print(f"  Parameters: {system_info['parameters']}")
        print(f"  Initial Conditions: {system_info['initial_conditions']}")
    
    # Create a simple test image (gradient)
    print("\n" + "=" * 60)
    print("ENCRYPTION TEST")
    print("=" * 60)
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    for i in range(100):
        for j in range(100):
            test_image[i, j] = [i * 255 // 100, j * 255 // 100, 128]
    
    print("\nOriginal image shape:", test_image.shape)
    
    # Encrypt
    encrypted = crypto.encrypt_image(test_image, rounds=3)
    print(f"Encrypted image statistics:")
    print(f"  Min: {encrypted.min()}, Max: {encrypted.max()}")
    print(f"  Mean: {encrypted.mean():.2f}, Std: {encrypted.std():.2f}")
    
    # Decrypt
    decrypted = crypto.decrypt_image(encrypted, test_image.shape, rounds=3)
    print(f"\nDecrypted image statistics:")
    print(f"  Min: {decrypted.min()}, Max: {decrypted.max()}")
    print(f"  Mean: {decrypted.mean():.2f}, Std: {decrypted.std():.2f}")
    
    # Verify
    if np.array_equal(test_image, decrypted):
        print("\n✓ SUCCESS: Decryption perfectly recovered the original image!")
    else:
        print("\n✗ ERROR: Decryption failed!")
        diff = np.abs(test_image.astype(int) - decrypted.astype(int))
        print(f"  Max difference: {diff.max()}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
