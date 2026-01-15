"""
Browser Automation with Playwright
E2E testing and web scraping capabilities
"""
from typing import Dict, List, Optional
import asyncio

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Run: pip install playwright && playwright install")

class BrowserAutomation:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    async def start_browser(self, headless: bool = True) -> bool:
        """Start browser instance"""
        if not PLAYWRIGHT_AVAILABLE:
            return False
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=headless)
            self.page = await self.browser.new_page()
            return True
        except Exception as e:
            print(f"Browser start error: {e}")
            return False
    
    async def navigate(self, url: str) -> Dict:
        """Navigate to URL"""
        if not self.page:
            return {'error': 'Browser not started'}
        
        try:
            await self.page.goto(url)
            return {
                'success': True,
                'url': self.page.url,
                'title': await self.page.title()
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def click(self, selector: str) -> Dict:
        """Click element"""
        if not self.page:
            return {'error': 'Browser not started'}
        
        try:
            await self.page.click(selector)
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def type_text(self, selector: str, text: str) -> Dict:
        """Type text into element"""
        if not self.page:
            return {'error': 'Browser not started'}
        
        try:
            await self.page.fill(selector, text)
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def screenshot(self, path: str = 'screenshot.png') -> Dict:
        """Take screenshot"""
        if not self.page:
            return {'error': 'Browser not started'}
        
        try:
            await self.page.screenshot(path=path)
            return {'success': True, 'path': path}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_text(self, selector: str) -> Optional[str]:
        """Get text content"""
        if not self.page:
            return None
        
        try:
            return await self.page.text_content(selector)
        except Exception:
            return None
    
    async def run_test(self, test_steps: List[Dict]) -> Dict:
        """Run automated test"""
        if not self.page:
            return {'error': 'Browser not started'}
        
        results = []
        for step in test_steps:
            action = step.get('action')
            
            try:
                if action == 'navigate':
                    result = await self.navigate(step['url'])
                elif action == 'click':
                    result = await self.click(step['selector'])
                elif action == 'type':
                    result = await self.type_text(step['selector'], step['text'])
                elif action == 'screenshot':
                    result = await self.screenshot(step.get('path', 'screenshot.png'))
                elif action == 'wait':
                    await asyncio.sleep(step.get('seconds', 1))
                    result = {'success': True}
                else:
                    result = {'error': f'Unknown action: {action}'}
                
                results.append({
                    'step': step,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'step': step,
                    'result': {'error': str(e)}
                })
        
        return {'results': results}
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
