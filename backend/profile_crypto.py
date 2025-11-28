import time
import numpy as np
from chaotic_crypto import ChaoticCrypto

print("=" * 60)
print("Performance Profiling")
print("=" * 60)

# Profile initialization (this includes solving ODEs)
print("\n1. INITIALIZATION (includes ODE solving)")
start = time.time()
crypto = ChaoticCrypto(seed="my_secret_seed")
init_time = time.time() - start
print(f"   Total initialization time: {init_time:.2f} seconds")

# Create test image
test_image = np.zeros((100, 100, 3), dtype=np.uint8)
for i in range(100):
    for j in range(100):
        test_image[i, j] = [i * 255 // 100, j * 255 // 100, 128]

# Profile encryption
print("\n2. ENCRYPTION (3 rounds)")
start = time.time()
encrypted = crypto.encrypt_image(test_image, rounds=3)
encrypt_time = time.time() - start
print(f"   Encryption time: {encrypt_time:.2f} seconds")

# Profile decryption
print("\n3. DECRYPTION (3 rounds)")
start = time.time()
decrypted = crypto.decrypt_image(encrypted, test_image.shape, rounds=3)
decrypt_time = time.time() - start
print(f"   Decryption time: {decrypt_time:.2f} seconds")

print("\n" + "=" * 60)
print("BREAKDOWN:")
print("=" * 60)
print(f"Initialization (ODE solving): {init_time:.2f}s ({init_time/(init_time+encrypt_time+decrypt_time)*100:.1f}%)")
print(f"Encryption:                    {encrypt_time:.2f}s ({encrypt_time/(init_time+encrypt_time+decrypt_time)*100:.1f}%)")
print(f"Decryption:                    {decrypt_time:.2f}s ({decrypt_time/(init_time+encrypt_time+decrypt_time)*100:.1f}%)")
print(f"TOTAL:                         {init_time+encrypt_time+decrypt_time:.2f}s")
print("=" * 60)

print("\nKEY INSIGHT:")
print("The time_points parameter in line 18 is set to 100000.")
print("This means each of the 3 hyperchaotic systems solves")
print("100,000 differential equation steps during initialization.")
print("This is the main bottleneck!")
