import json
import time
import os
import hashlib
from datetime import datetime
from block import Block
from security import generate_keypair, sign, verify


class IGoWChain:
    """Manage a linked sequence of mined IGoW blocks."""

    def __init__(self, difficulty: int = 2, width: int = 10, height: int = 10):
        """Initialize the chain and create the genesis block."""
        self.difficulty = difficulty
        self.width = width
        self.height = height
        # The chain is a list of Block objects linked by fingerprints, not a database or file.
        self.chain = []
        # optional node keypair for signing blocks/checkpoints
        self.node_privkey = None
        self.node_pubkey = None
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """Create the first block that anchors the chain."""
        # The genesis block is the foundation of the chain, and its previous_fingerprint is all zeros by convention, same as Bitcoin.
        genesis_block = Block(
            index=0,
            data="IGOW_GENESIS",
            previous_fingerprint="0" * 64,
            difficulty=self.difficulty,
            width=self.width,
            height=self.height,
        )
        self.chain.append(genesis_block)

        # If node keys are not set, generate a demo symmetric keypair (or Ed25519 if available)
        if not self.node_privkey:
            priv, pub = generate_keypair()
            self.node_privkey = priv
            self.node_pubkey = pub

    def add_block(self, data: str) -> Block:
        """Mine and append a new block that points to the current chain tip."""
        last_block = self.chain[-1]
        # Each block explicitly stores the previous block's fingerprint, this is what creates the chain link.
        new_block = Block(
            index=len(self.chain),
            data=data,
            previous_fingerprint=last_block.fingerprint,
            difficulty=self.difficulty,
            width=self.width,
            height=self.height,
        )
        self.chain.append(new_block)
        # Sign the block fingerprint if node keys are available
        try:
            sig = sign(new_block.fingerprint.encode(), self.node_privkey)
            new_block.signature = sig
            new_block.creator_pubkey = self.node_pubkey
        except Exception:
            new_block.signature = None
            new_block.creator_pubkey = None
        return new_block

    def verify_chain(self) -> dict:
        """Verify block proofs, link integrity, and index order across the full chain."""
        valid = True
        errors = []
        # Three checks run on every block, and any single failure marks the entire chain as corrupted.
        for i, current in enumerate(self.chain):
            if not current.verify():
                errors.append(f"Block {i}: image proof invalid")
                valid = False

            # Recompute fingerprint from the stored image_hex and ensure it matches the stored fingerprint
            recomputed_fp = hashlib.sha256(current.image_hex.encode()).hexdigest()
            if recomputed_fp != current.fingerprint:
                errors.append(f"Block {i}: fingerprint mismatch")
                valid = False

            if i > 0:
                previous = self.chain[i - 1]
                if current.previous_fingerprint != previous.fingerprint:
                    errors.append(f"Block {i}: fingerprint link broken")
                    valid = False

            if current.index != i:
                errors.append(f"Block {i}: index mismatch")
                valid = False

        return {
            "valid": valid,
            "blocks": len(self.chain),
            "errors": errors,
            "status": "CHAIN VALID" if valid else "CHAIN CORRUPTED",
        }

    def tamper_test(self, block_index: int) -> None:
        """Corrupt a block to show that chain verification detects modification."""
        print(f"\nTAMPER TEST — Block {block_index}")
        before = self.verify_chain()
        print(f"Before tampering: {before}")

        # This proves the chain is tamper-evident, because modifying any block breaks verification.
        self.chain[block_index].data = "TAMPERED_DATA"
        self.chain[block_index].image_hex = "ff" * 150

        after = self.verify_chain()
        print(f"After tampering: {after}")
        if before["valid"] and not after["valid"]:
            print("TAMPER DETECTED")
        else:
            print("TAMPER NOT DETECTED")

    def save_to_file(self, path: str) -> None:
        """Persist the full chain to a JSON file at `path`.

        The saved format includes the full `image_hex` for each block so the
        chain can be fully reconstructed without re-mining.
        """
        data = {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "difficulty": self.difficulty,
            "width": self.width,
            "height": self.height,
            "blocks": [b.to_serializable() for b in self.chain],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    @classmethod
    def load_from_file(cls, path: str) -> "IGoWChain":
        """Load a chain previously saved with `save_to_file`.

        This reconstructs `Block` instances without re-mining.
        """
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        chain = object.__new__(cls)
        chain.difficulty = data.get("difficulty", 2)
        chain.width = data.get("width", 10)
        chain.height = data.get("height", 10)
        chain.chain = [Block.from_serializable(b) for b in data.get("blocks", [])]
        return chain

    def save_snapshot(self, snapshots_dir: str = "snapshots") -> str:
        """Save a timestamped snapshot to the `snapshots_dir` and return the filepath."""
        os.makedirs(snapshots_dir, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"chain_snapshot_{ts}.json"
        path = os.path.join(snapshots_dir, filename)
        self.save_to_file(path)
        return path

    def save_checkpoint(self, path: str) -> None:
        """Save a simple checkpoint containing last fingerprint and signature."""
        if not self.chain:
            raise RuntimeError("Chain is empty")
        last_fp = self.chain[-1].fingerprint
        sig = sign(last_fp.encode(), self.node_privkey) if self.node_privkey else b""
        data = {
            "last_fingerprint": last_fp,
            "signature": sig.hex(),
            "pubkey": (self.node_pubkey.hex() if self.node_pubkey else ""),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def display_chain(self) -> None:
        """Print a readable summary of the chain and how each block links to the next."""
        print("\n" + "=" * 70)
        print("IGOW CHAIN SUMMARY")
        print("=" * 70)

        for i, block in enumerate(self.chain):
            block_fp = block.fingerprint[:16]
            prev_fp = block.previous_fingerprint[:16]
            print(f"Block {block.index}")
            print(f"  Timestamp           : {block.timestamp}")
            print(f"  Data                : {block.data}")
            print(f"  Fingerprint         : {block_fp}...")
            print(f"  Previous fingerprint: {prev_fp}...")
            print(f"  Attempts            : {block.attempts}")
            print(f"  Elapsed             : {block.elapsed} seconds")

            if i < len(self.chain) - 1:
                next_block = self.chain[i + 1]
                print(f"     [Block {block.index}] fingerprint: {block_fp}...")
                print("          |")
                print("          v")
                print(
                    f"     [Block {next_block.index}] prev: {next_block.previous_fingerprint[:16]}... current: {next_block.fingerprint[:16]}..."
                )
                print("          |")
                print("          v")

        status = self.verify_chain()
        print("-" * 70)
        print(f"Chain status: {status['status']}")
        print(f"Blocks      : {status['blocks']}")
        print(f"Valid       : {status['valid']}")
        if status["errors"]:
            print("Errors      :")
            for error in status["errors"]:
                print(f"  - {error}")
        print("=" * 70)


if __name__ == "__main__":
    """Run a small IGoW chain demo from genesis through tamper detection."""
    print("IGoW Chain — V1 Demo")
    build_start = time.time()

    chain = IGoWChain(difficulty=2)
    chain.add_block("Transaction: Meet -> Priya: 500 IGoW")
    chain.add_block("Transaction: Priya -> Arjun: 200 IGoW")

    build_end = time.time()
    chain.display_chain()

    result = chain.verify_chain()
    print(f"\nFull verify result: {json.dumps(result, indent=2)}")

    chain.tamper_test(1)

    total_build_time = round(build_end - build_start, 4)
    print(f"\nTotal chain build time: {total_build_time} seconds")
