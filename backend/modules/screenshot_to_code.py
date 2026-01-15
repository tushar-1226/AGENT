"""
Screenshot to Code Generator
Convert UI mockups to React components using Gemini Vision
"""
from typing import Dict, Optional
import base64
import os

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class ScreenshotToCode:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if GENAI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_screenshot(self, image_path: str) -> Dict:
        """Analyze screenshot and extract UI components"""
        if not GENAI_AVAILABLE:
            return {'error': 'Gemini not available'}
        
        try:
            # Read image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            prompt = """Analyze this UI screenshot and describe:
1. Layout structure (header, sidebar, main content, footer)
2. Components (buttons, inputs, cards, navigation)
3. Color scheme
4. Typography
5. Spacing and alignment

Be specific and detailed."""
            
            response = self.model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': image_data}])
            
            return {
                'success': True,
                'analysis': response.text
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_react_code(self, image_path: str, framework: str = 'react') -> Dict:
        """Generate React component code from screenshot"""
        if not GENAI_AVAILABLE:
            return {'error': 'Gemini not available'}
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            prompt = f"""Convert this UI screenshot to {framework} code with Tailwind CSS.

Requirements:
1. Create a functional component
2. Use Tailwind CSS for styling
3. Make it responsive
4. Include proper semantic HTML
5. Add placeholder content where needed
6. Use modern React patterns (hooks, etc.)

Return ONLY the code, no explanations."""
            
            response = self.model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': image_data}])
            
            # Extract code from response
            code = response.text
            
            # Clean up markdown code blocks if present
            if '```' in code:
                code = code.split('```')[1]
                if code.startswith('tsx') or code.startswith('jsx') or code.startswith('javascript'):
                    code = '\n'.join(code.split('\n')[1:])
            
            return {
                'success': True,
                'code': code.strip(),
                'framework': framework
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_html_css(self, image_path: str) -> Dict:
        """Generate HTML and CSS from screenshot"""
        if not GENAI_AVAILABLE:
            return {'error': 'Gemini not available'}
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            prompt = """Convert this UI screenshot to HTML and CSS.

Requirements:
1. Semantic HTML5
2. Modern CSS (flexbox/grid)
3. Responsive design
4. Clean, readable code
5. Inline CSS in <style> tag

Return complete HTML file."""
            
            response = self.model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': image_data}])
            
            return {
                'success': True,
                'html': response.text
            }
        except Exception as e:
            return {'error': str(e)}
