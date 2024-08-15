import unittest
from unittest.mock import MagicMock
from researcher.web_researcher import WebResearcher
import re

class TestWebResearcher(unittest.TestCase):
    def setUp(self):
        # Initialize the WebResearcher instance
        self.researcher = WebResearcher()

    def contains_markdown(self, text):
        # Simple heuristic checks for Markdown elements
        markdown_patterns = [
            r'^#',  # Header
            r'^##',  # Header
            r'^###',  # Header
            r'^####',  # Header
            r'^\* ',  # Unordered list
            r'^\- ',  # Unordered list
            r'\[.*\]\(.*\)',  # Link
            r'`.*`',  # Inline code
        ]
        return any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns)

    def test_perform_research(self):
        research_question = "Perform market research on the topic of electric vehicles in the United States."
        
        # Call the method
        result = self.researcher.perform_research(research_question)
        
        # Assert the result is a non-empty string
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        
        # Check if the result contains Markdown elements
        self.assertTrue(self.contains_markdown(result))



if __name__ == '__main__':
    unittest.main()