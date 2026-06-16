import unittest
import os
import sys
import pathlib

# Ensure project root is importable when running tests directly
ROOT = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.insert(0, ROOT)

from image_hash import generate_image_hash, image_to_hex, check_difficulty
from block import Block
from chain import IGoWChain


class TestIGoWCore(unittest.TestCase):
    def test_generate_and_hex(self):
        img1 = generate_image_hash('DATA', 1, 5, 5)
        img2 = generate_image_hash('DATA', 1, 5, 5)
        self.assertTrue((img1 == img2).all())
        h = image_to_hex(img1)
        self.assertIsInstance(h, str)

    def test_check_difficulty(self):
        img = generate_image_hash('DATA', 2, 3, 3)
        # difficulty larger than pixels should return False
        self.assertFalse(check_difficulty(img, 100))
        # difficulty 0 should pass
        self.assertTrue(check_difficulty(img, 0))

    def test_block_and_chain(self):
        chain = IGoWChain(difficulty=1)
        b = chain.add_block('Tx Test')
        self.assertTrue(b.verify())
        # save and load
        p = chain.save_snapshot('snapshots_test')
        self.assertTrue(os.path.exists(p))
        loaded = IGoWChain.load_from_file(p)
        self.assertEqual(len(loaded.chain), len(chain.chain))
        self.assertTrue(loaded.verify_chain()['valid'])


if __name__ == '__main__':
    unittest.main()
