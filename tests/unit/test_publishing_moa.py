import unittest
from kindlemint.agents.publishing_moa import PublishingMoA

class TestPublishingMoA(unittest.TestCase):
    def test_create_book_pipeline(self):
        moa = PublishingMoA()
        result = moa.create_book("A cyborg poet in a post-apocalyptic rainforest")
        self.assertIn("Plot designed around concept", result)
        self.assertIn("Characters created based on plot", result)
        self.assertIn("Dialogue written for characters", result)
        self.assertIn("Stylistically refined content", result)
        self.assertIn("Market-optimized content", result)

if __name__ == "__main__":
    unittest.main()