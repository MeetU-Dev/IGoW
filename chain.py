import json
import time
from block import Block


class IGoWChain:
    """Manage a linked sequence of mined IGoW blocks."""

    def __init__(self, difficulty: int = 2, width: int = 10, height: int = 10):
        """Initialize the chain and create the genesis block."""
        self.difficulty = difficulty
        self.width = width
        self.height = height
        # The chain is a list of Block objects linked by fingerprints, not a database or file.
        self.chain = []
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
