"""
Tests for Code Intelligence Module
"""

import pytest
from modules.code_intelligence import CodeIntelligence


class TestCodeIntelligence:
    
    @pytest.mark.asyncio
    async def test_analyze_python_code(self, sample_code):
        """Test Python code analysis"""
        ci = CodeIntelligence()
        result = await ci.analyze_code_quality(sample_code, "python")
        
        assert result["success"] is True
        assert "metrics" in result
        assert "issues" in result
        assert "quality_score" in result
        assert result["metrics"]["functions"] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_javascript_code(self, sample_javascript):
        """Test JavaScript code analysis"""
        ci = CodeIntelligence()
        result = await ci.analyze_code_quality(sample_javascript, "javascript")
        
        assert result["success"] is True
        assert "metrics" in result
        assert result["metrics"]["functions"] > 0
    
    @pytest.mark.asyncio
    async def test_detect_long_method(self):
        """Test detection of long methods"""
        ci = CodeIntelligence()
        
        # Create a long function
        long_code = "def long_function():\n" + "    pass\n" * 60
        
        result = await ci.analyze_code_quality(long_code, "python")
        
        assert result["success"] is True
        # Should detect long method
        long_method_issues = [i for i in result["issues"] if i["type"] == "long_method"]
        assert len(long_method_issues) > 0
    
    @pytest.mark.asyncio
    async def test_detect_too_many_parameters(self):
        """Test detection of too many parameters"""
        ci = CodeIntelligence()
        
        code = """
def many_params(a, b, c, d, e, f, g):
    return a + b + c
"""
        
        result = await ci.analyze_code_quality(code, "python")
        
        assert result["success"] is True
        param_issues = [i for i in result["issues"] if i["type"] == "too_many_parameters"]
        assert len(param_issues) > 0
    
    @pytest.mark.asyncio
    async def test_detect_bare_except(self):
        """Test detection of bare except clauses"""
        ci = CodeIntelligence()
        
        code = """
def risky_function():
    try:
        dangerous_operation()
    except:
        pass
"""
        
        result = await ci.analyze_code_quality(code, "python")
        
        assert result["success"] is True
        bare_except_issues = [i for i in result["issues"] if i["type"] == "bare_except"]
        assert len(bare_except_issues) > 0
    
    @pytest.mark.asyncio
    async def test_quality_score_calculation(self, sample_code):
        """Test quality score calculation"""
        ci = CodeIntelligence()
        
        result = await ci.analyze_code_quality(sample_code, "python")
        
        assert result["success"] is True
        assert 0 <= result["quality_score"] <= 100
    
    @pytest.mark.asyncio
    async def test_suggest_refactoring(self, sample_code):
        """Test refactoring suggestions"""
        ci = CodeIntelligence()
        
        result = await ci.suggest_refactoring(sample_code, "python")
        
        assert result["success"] is True
        assert "refactorings" in result
        assert "analysis" in result
    
    @pytest.mark.asyncio
    async def test_invalid_syntax(self):
        """Test handling of invalid syntax"""
        ci = CodeIntelligence()
        
        invalid_code = "def invalid( syntax error"
        result = await ci.analyze_code_quality(invalid_code, "python")
        
        assert result["success"] is False
        assert "error" in result
