"""
IGoW (Image-Generated Proof-of-Work) - Image Hash Generator

This module provides cryptographic image generation for blockchain consensus.
Each block generates a deterministic pixel array from its data and nonce,
creating a unique visual fingerprint that can be verified by all nodes.
"""

import hashlib
import numpy as np


def generate_image_hash(data: str, nonce: int, width: int = 10, height: int = 10) -> np.ndarray:
    """
    Generate a deterministic pixel array from data and nonce.
    
    This function is core to IGoW consensus. Determinism is critical because:
    - All network nodes must independently generate IDENTICAL images for the same block
    - Any variation would break consensus and invalidate the block
    - The SHA-256 hash ensures the slightest change in data/nonce produces completely different pixels
    - This creates the Proof-of-Work: the difficulty is in finding data+nonce combinations
      that produce images meeting certain criteria (e.g., patterns, hash thresholds)
    
    Args:
        data: Block data string (e.g., "IGOW_BLOCK_0")
        nonce: Integer nonce for PoW iteration
        width: Pixel array width (default 10)
        height: Pixel array height (default 10)
    
    Returns:
        np.ndarray: Array of shape (height, width, 3) with uint8 RGB values (0-255)
    """
    # Combine data and nonce into a single string
    combined = f"{data}:{nonce}"
    
    # Compute SHA-256 hash
    hash_object = hashlib.sha256(combined.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert hex digest to integer for RNG seed
    seed_value = int(hash_hex, 16)
    
    # Create RNG with the deterministic seed
    rng = np.random.default_rng(seed_value)
    
    # Generate pixel array: (height, width, 3) RGB image with uint8 values
    pixel_array = rng.integers(0, 256, size=(height, width, 3), dtype=np.uint8)
    
    return pixel_array


def image_to_hex(pixels: np.ndarray) -> str:
    """
    Convert pixel array to compact hex string fingerprint.
    
    This hex fingerprint serves as the on-chain representation of the image.
    Instead of storing the full pixel array on-chain (expensive), we store this
    compressed hex representation. Nodes can verify by regenerating the image
    and computing its hex fingerprint independently.
    
    Args:
        pixels: np.ndarray of shape (height, width, 3) with uint8 values
    
    Returns:
        str: Hexadecimal string representation of the pixel array
    """
    # Convert array to bytes and return as hex string
    pixel_bytes = pixels.astype(np.uint8).tobytes()
    hex_string = pixel_bytes.hex()
    
    return hex_string


def verify_determinism(data: str, nonce: int) -> bool:
    """
    Verify that image generation is deterministic.
    
    Determinism is the foundation of blockchain consensus. This function
    validates that the same data+nonce always produces identical pixel arrays.
    If non-determinism is detected, it signals a critical bug that would
    break network consensus.
    
    Args:
        data: Block data string
        nonce: Integer nonce
    
    Returns:
        bool: True if both generations are identical, False otherwise
    """
    # Generate image twice with identical inputs
    image1 = generate_image_hash(data, nonce)
    image2 = generate_image_hash(data, nonce)
    
    # Compare arrays element-wise
    is_deterministic = np.array_equal(image1, image2)
    
    # Print result
    if is_deterministic:
        print("DETERMINISM CHECK: PASSED")
    else:
        print("DETERMINISM CHECK: FAILED")
    
    return is_deterministic


if __name__ == "__main__":
    # Test with sample block data
    print("=" * 50)
    print("IGoW Image Hash Generator - Test Run")
    print("=" * 50)
    
    # Verify determinism
    result = verify_determinism(data="IGOW_BLOCK_0", nonce=42)
    
    # Generate and display image properties
    print()
    image = generate_image_hash(data="IGOW_BLOCK_0", nonce=42)
    
    # Print hex fingerprint
    hex_fp = image_to_hex(image)
    print(f"Image Hex Fingerprint: {hex_fp[:64]}...")  # Print first 64 chars
    
    # Print array shape
    print(f"Pixel Array Shape: {image.shape}")
    
    print("=" * 50)
