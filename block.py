import hashlib
import time
import json
from image_hash import generate_image_hash, check_difficulty, mine_block, image_to_hex


class Block:
    """Represent a mined IGoW block and the data needed to verify it."""

    def __init__(self, index: int, data: str, previous_fingerprint: str, difficulty: int = 2, width: int = 10, height: int = 10):
        """Create and mine a block from its blockchain inputs."""
        self.index = index
        self.data = data
        self.previous_fingerprint = previous_fingerprint
        self.difficulty = difficulty
        self.width = width
        self.height = height
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        self.block_data = json.dumps(
            {
                "index": self.index,
                "data": self.data,
                "previous_fingerprint": self.previous_fingerprint,
                "timestamp": self.timestamp,
            },
            sort_keys=True,
        )

        self.mine_result = mine_block(self.block_data, difficulty, width, height)
        self.nonce = self.mine_result["nonce"]
        self.attempts = self.mine_result["attempts"]
        self.elapsed = self.mine_result["elapsed"]
        self.pixels = self.mine_result["pixels"]
        self.image_hex = self.mine_result["image_hex"]

        # This is the compact on-chain identifier, SHA-256 of the image hex, not the image itself.
        self.fingerprint = hashlib.sha256(self.image_hex.encode()).hexdigest()

    def verify(self) -> bool:
        """Rebuild the image and confirm the block's proof-of-work is still valid."""
        # Verification proves the nonce produces a valid image without trusting stored data.
        regenerated = generate_image_hash(self.block_data, self.nonce, self.width, self.height)
        difficulty_ok = check_difficulty(regenerated, self.difficulty)
        regenerated_hex = image_to_hex(regenerated)
        hex_ok = regenerated_hex == self.image_hex

        # Recompute fingerprint from regenerated image hex and ensure it matches stored fingerprint.
        recomputed_fingerprint = hashlib.sha256(regenerated_hex.encode()).hexdigest()
        fingerprint_ok = recomputed_fingerprint == self.fingerprint

        return difficulty_ok and hex_ok and fingerprint_ok

    def to_dict(self) -> dict:
        """Return a display-friendly snapshot of the block state."""
        # image_hex truncated for display only, full hex is stored in self.image_hex.
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_fingerprint": self.previous_fingerprint,
            "nonce": self.nonce,
            "attempts": self.attempts,
            "elapsed": self.elapsed,
            "difficulty": self.difficulty,
            "image_hex": self.image_hex[:64] + "...",
            "fingerprint": self.fingerprint,
        }

    def to_serializable(self) -> dict:
        """Return a complete dict suitable for JSON serialization and persistence.

        Includes full `image_hex` and reconstruction parameters (width/height).
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_fingerprint": self.previous_fingerprint,
            "nonce": self.nonce,
            "attempts": self.attempts,
            "elapsed": self.elapsed,
            "difficulty": self.difficulty,
            "width": self.width,
            "height": self.height,
            "image_hex": self.image_hex,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_serializable(cls, obj: dict) -> "Block":
        """Reconstruct a Block instance from serialized data without re-mining.

        This creates the object directly and sets attributes. It does not call the
        mining constructor because the image and fingerprint are already provided.
        """
        block = object.__new__(cls)
        block.index = obj["index"]
        block.timestamp = obj["timestamp"]
        block.data = obj["data"]
        block.previous_fingerprint = obj["previous_fingerprint"]
        block.nonce = obj["nonce"]
        block.attempts = obj.get("attempts", 0)
        block.elapsed = obj.get("elapsed", 0)
        block.difficulty = obj.get("difficulty", 0)
        block.width = obj.get("width", 10)
        block.height = obj.get("height", 10)
        block.image_hex = obj.get("image_hex", "")
        block.fingerprint = obj.get("fingerprint", "")
        # pixels are not persisted to keep storage light; they can be regenerated
        block.pixels = None
        block.block_data = json.dumps(
            {
                "index": block.index,
                "data": block.data,
                "previous_fingerprint": block.previous_fingerprint,
                "timestamp": block.timestamp,
            },
            sort_keys=True,
        )
        return block

    def display(self) -> None:
        """Print a readable block summary for debugging and inspection."""
        block_info = self.to_dict()
        print("\n" + "=" * 70)
        print("BLOCK SUMMARY")
        print("=" * 70)
        print(f"Index               : {block_info['index']}")
        print(f"Timestamp           : {block_info['timestamp']}")
        print(f"Data                : {block_info['data']}")
        print(f"Previous fingerprint : {block_info['previous_fingerprint']}")
        print(f"Nonce               : {block_info['nonce']}")
        print(f"Attempts            : {block_info['attempts']}")
        print(f"Elapsed             : {block_info['elapsed']} seconds")
        print(f"Difficulty          : {block_info['difficulty']}")
        print(f"Image hex           : {block_info['image_hex']}")
        print(f"Fingerprint         : {block_info['fingerprint']}")
        print(f"Verification        : {'BLOCK VERIFIED' if self.verify() else 'BLOCK INVALID'}")
        print("=" * 70)


if __name__ == "__main__":
    """Build and display a short IGoW chain demonstration."""
    genesis = Block(index=0, data="IGOW_GENESIS", previous_fingerprint="0" * 64, difficulty=2)
    genesis.display()
    print(f"Genesis fingerprint: {genesis.fingerprint}")

    second_block = Block(index=1, data="IGOW_BLOCK_1", previous_fingerprint=genesis.fingerprint, difficulty=2)
    second_block.display()
    print(f"Second block fingerprint: {second_block.fingerprint}")

    print(f"Genesis verified: {genesis.verify()}")
    print(f"Second block verified: {second_block.verify()}")
