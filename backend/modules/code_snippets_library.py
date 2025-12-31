"""
Code Snippets Library Module
Extended snippet functionality with templates and patterns
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CodeSnippetsLibrary:
    """Extended code snippets library with common patterns"""
    
    def __init__(self):
        self.snippet_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict:
        """Initialize snippet template library"""
        return {
            # Python Templates
            'python': {
                'class_basic': {
                    'name': 'Basic Class',
                    'description': 'Python class with __init__',
                    'prefix': 'class',
                    'template': '''class ${1:ClassName}:
    """${2:Class description}"""
    
    def __init__(self, ${3:params}):
        """Initialize"""
        ${4:pass}''',
                    'placeholders': ['ClassName', 'Class description', 'params', 'pass']
                },
                'fastapi_endpoint': {
                    'name': 'FastAPI Endpoint',
                    'description': 'API endpoint with error handling',
                    'prefix': 'api',
                    'template': '''@app.${1|get,post,put,delete|}("${2:/endpoint}")
async def ${3:handler}(${4:params}):
    """${5:Description}"""
    try:
        ${6:pass}
        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})''',
                    'placeholders': ['method', 'endpoint', 'handler', 'params', 'Description', 'pass']
                },
                'dataclass': {
                    'name': 'Dataclass',
                    'description': 'Python dataclass',
                    'prefix': 'dc',
                    'template': '''from dataclasses import dataclass

@dataclass
class ${1:ClassName}:
    """${2:Description}"""
    ${3:field}: ${4:type}''',
                    'placeholders': ['ClassName', 'Description', 'field', 'type']
                },
            },
            # React Templates
            'react': {
                'component_full': {
                    'name': 'Full React Component',
                    'description': 'Component with state and effects',
                    'prefix': 'rfc',
                    'template': '''import React, { useState, useEffect } from 'react';

interface ${1:Component}Props {
  ${2:prop}: ${3:type};
}

export const ${1:Component}: React.FC<${1:Component}Props> = ({ ${2:prop} }) => {
  const [${4:state}, set${4/(.*)/${1:/capitalize}/}] = useState(${5:initial});

  useEffect(() => {
    ${6:// Effect}
  }, [${7:deps}]);

  return (
    <div className="${8:container}">
      ${9:// JSX}
    </div>
  );
};''',
                    'placeholders': ['Component', 'prop', 'type', 'state', 'initial', 'Effect', 'deps', 'container', 'JSX']
                },
                'custom_hook': {
                    'name': 'Custom Hook',
                    'description': 'React custom hook',
                    'prefix': 'hook',
                    'template': '''import { useState, useEffect } from 'react';

export const use${1:HookName} = (${2:params}) => {
  const [${3:state}, set${3/(.*)/${1:/capitalize}/}] = useState(${4:initial});

  useEffect(() => {
    ${5:// Effect}
  }, [${6:deps}]);

  return { ${3:state}, set${3/(.*)/${1:/capitalize}/} };
};''',
                    'placeholders': ['HookName', 'params', 'state', 'initial', 'Effect', 'deps']
                },
            },
            # SQL Templates
            'sql': {
                'create_table': {
                    'name': 'CREATE TABLE',
                    'description': 'Create table with common fields',
                    'prefix': 'table',
                    'template': '''CREATE TABLE ${1:table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ${2:column} ${3:type} ${4:constraints},
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''',
                    'placeholders': ['table_name', 'column', 'type', 'constraints']
                },
            }
        }
    
    def get_template(self, language: str, template_name: str) -> Optional[Dict]:
        """Get a specific template"""
        lang_templates = self.snippet_templates.get(language, {})
        return lang_templates.get(template_name)
    
    def list_templates(self, language: Optional[str] = None) -> Dict:
        """List all available templates"""
        if language:
            return {language: self.snippet_templates.get(language, {})}
        return self.snippet_templates
    
    def get_languages(self) -> List[str]:
        """Get all supported languages"""
        return list(self.snippet_templates.keys())


# Global instance
code_snippets_library = None


def get_snippets_library():
    """Get or create snippets library instance"""
    global code_snippets_library
    if code_snippets_library is None:
        code_snippets_library = CodeSnippetsLibrary()
    return code_snippets_library
