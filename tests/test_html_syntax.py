import pytest
import os
import glob
from html.parser import HTMLParser

class StrictHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        
    def handle_starttag(self, tag, attrs):
        # We ignore void elements that don't require closing tags in HTML5
        void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr', '!doctype'}
        if tag not in void_elements:
            self.tags.append(tag)
            
    def handle_endtag(self, tag):
        if not self.tags:
            pytest.fail(f"Closing tag </{tag}> found without matching opening tag.")
        
        last_tag = self.tags.pop()
        if last_tag != tag:
            pytest.fail(f"Mismatched HTML tags: Expected </{last_tag}> but found </{tag}>.")

def test_html_syntax_integrity():
    # Retrieve all HTML files from the repository
    base_dir = os.path.dirname(os.path.dirname(__file__))
    html_files = glob.glob(os.path.join(base_dir, "**/*.html"), recursive=True)
    
    # Assert that all HTML templates are structurally sound
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parser = StrictHTMLParser()
        try:
            parser.feed(content)
            # If tags are left unclosed at EOF (ignoring void elements)
            if parser.tags:
                pytest.fail(f"Unclosed HTML tags in {os.path.basename(file_path)}: {parser.tags}")
        except Exception as e:
            pytest.fail(f"HTML Parsing error in {os.path.basename(file_path)}: {e}")
