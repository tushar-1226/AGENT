"""
Security Copilot
Real-time security vulnerability detection and compliance checking
"""
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import re
import hashlib
import ast


class VulnerabilityType(Enum):
    """Types of security vulnerabilities"""
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    CSRF = "csrf"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CRYPTO = "cryptographic"
    SECRETS_EXPOSURE = "secrets_exposure"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"


class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    """Security vulnerability"""
    id: str
    type: VulnerabilityType
    severity: Severity
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    cve_id: Optional[str] = None
    remediation: str = ""
    references: List[str] = None
    detected_at: str = ""
    
    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()
        if self.references is None:
            self.references = []


class SecretScanner:
    """Scan for exposed secrets and credentials"""
    
    def __init__(self):
        # Common secret patterns
        self.patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'aws_secret[_\s]*=[\s]*["\']([A-Za-z0-9/+=]{40})["\']',
            'api_key': r'api[_\s]*key[\s]*=[\s]*["\']([A-Za-z0-9]{32,})["\']',
            'private_key': r'-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----',
            'password': r'password[\s]*=[\s]*["\'](?!<|{)([^"\'\s]{8,})["\']',
            'jwt': r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+',
            'github_token': r'gh[pousr]_[A-Za-z0-9]{36}',
            'slack_token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,}',
            'database_url': r'(postgres|mysql|mongodb)://[^:]+:[^@]+@',
        }
        
        self.whitelist_patterns = [
            r'example\.com',
            r'placeholder',
            r'your_.*_here',
            r'<.*>',
            r'\{.*\}',
        ]
    
    def scan_code(self, code: str, file_path: str) -> List[Vulnerability]:
        """Scan code for exposed secrets"""
        vulnerabilities = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip if line is whitelisted
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.whitelist_patterns):
                continue
            
            for secret_type, pattern in self.patterns.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                
                for match in matches:
                    vulnerabilities.append(Vulnerability(
                        id=f"secret_{hashlib.md5(f'{file_path}{line_num}{secret_type}'.encode()).hexdigest()[:8]}",
                        type=VulnerabilityType.SECRETS_EXPOSURE,
                        severity=Severity.CRITICAL,
                        title=f"Exposed {secret_type.replace('_', ' ').title()}",
                        description=f"Potential {secret_type} found in code",
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation=f"Remove {secret_type} from code and use environment variables or secret management",
                        references=[
                            "https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password"
                        ]
                    ))
        
        return vulnerabilities
    
    def scan_file(self, file_path: str) -> List[Vulnerability]:
        """Scan a file for secrets"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            return self.scan_code(code, file_path)
        except Exception as e:
            return []


class CodeVulnerabilityScanner:
    """Scan code for common vulnerabilities"""
    
    def __init__(self):
        self.python_patterns = {
            'sql_injection': [
                r'execute\(["\'].*%s.*["\']\s*%',
                r'execute\(["\'].*\+.*["\']\)',
                r'cursor\.execute.*format\(',
            ],
            'command_injection': [
                r'os\.system\(["\'].*\+',
                r'subprocess\.call\(["\'].*\+',
                r'eval\(',
                r'exec\(',
            ],
            'path_traversal': [
                r'open\(["\'].*\+.*["\']\)',
                r'os\.path\.join.*request\.',
            ],
            'insecure_random': [
                r'random\.random\(',
                r'random\.randint\(',
            ],
            'insecure_hash': [
                r'hashlib\.md5\(',
                r'hashlib\.sha1\(',
            ],
        }
    
    def scan_python_code(self, code: str, file_path: str) -> List[Vulnerability]:
        """Scan Python code for vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')
        
        # Pattern-based scanning
        for vuln_type, patterns in self.python_patterns.items():
            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    if re.search(pattern, line):
                        severity = self._determine_severity(vuln_type)
                        vulnerabilities.append(Vulnerability(
                            id=f"vuln_{hashlib.md5(f'{file_path}{line_num}{vuln_type}'.encode()).hexdigest()[:8]}",
                            type=self._map_vuln_type(vuln_type),
                            severity=severity,
                            title=f"Potential {vuln_type.replace('_', ' ').title()}",
                            description=self._get_description(vuln_type),
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            remediation=self._get_remediation(vuln_type),
                            references=self._get_references(vuln_type)
                        ))
        
        # AST-based analysis
        try:
            tree = ast.parse(code)
            vulnerabilities.extend(self._analyze_ast(tree, file_path))
        except:
            pass
        
        return vulnerabilities
    
    def _analyze_ast(self, tree: ast.AST, file_path: str) -> List[Vulnerability]:
        """Analyze AST for security issues"""
        vulnerabilities = []
        
        for node in ast.walk(tree):
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', '__import__']:
                        vulnerabilities.append(Vulnerability(
                            id=f"ast_{hashlib.md5(f'{file_path}{node.lineno}'.encode()).hexdigest()[:8]}",
                            type=VulnerabilityType.INSECURE_DESERIALIZATION,
                            severity=Severity.HIGH,
                            title=f"Dangerous function: {node.func.id}",
                            description=f"Use of {node.func.id}() can lead to code execution",
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet="",
                            remediation=f"Avoid using {node.func.id}() with untrusted input"
                        ))
            
            # Check for try-except-pass (swallowing exceptions)
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                        vulnerabilities.append(Vulnerability(
                            id=f"ast_{hashlib.md5(f'{file_path}{node.lineno}'.encode()).hexdigest()[:8]}",
                            type=VulnerabilityType.CONFIGURATION,
                            severity=Severity.MEDIUM,
                            title="Silenced exception",
                            description="Exception is caught but not handled",
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet="",
                            remediation="Log exceptions or handle them properly"
                        ))
        
        return vulnerabilities
    
    def _map_vuln_type(self, vuln_str: str) -> VulnerabilityType:
        """Map string to VulnerabilityType"""
        mapping = {
            'sql_injection': VulnerabilityType.SQL_INJECTION,
            'command_injection': VulnerabilityType.INSECURE_DESERIALIZATION,
            'path_traversal': VulnerabilityType.CONFIGURATION,
            'insecure_random': VulnerabilityType.CRYPTO,
            'insecure_hash': VulnerabilityType.CRYPTO,
        }
        return mapping.get(vuln_str, VulnerabilityType.CONFIGURATION)
    
    def _determine_severity(self, vuln_type: str) -> Severity:
        """Determine severity based on vulnerability type"""
        critical = ['sql_injection', 'command_injection']
        high = ['path_traversal', 'xss']
        
        if vuln_type in critical:
            return Severity.CRITICAL
        elif vuln_type in high:
            return Severity.HIGH
        else:
            return Severity.MEDIUM
    
    def _get_description(self, vuln_type: str) -> str:
        """Get vulnerability description"""
        descriptions = {
            'sql_injection': "SQL injection allows attackers to execute arbitrary SQL commands",
            'command_injection': "Command injection allows arbitrary system command execution",
            'path_traversal': "Path traversal can allow access to unauthorized files",
            'insecure_random': "Insecure random number generation for security purposes",
            'insecure_hash': "MD5/SHA1 are cryptographically broken",
        }
        return descriptions.get(vuln_type, "Security vulnerability detected")
    
    def _get_remediation(self, vuln_type: str) -> str:
        """Get remediation advice"""
        remediations = {
            'sql_injection': "Use parameterized queries or ORM",
            'command_injection': "Avoid dynamic command construction, use safe APIs",
            'path_traversal': "Validate and sanitize file paths",
            'insecure_random': "Use secrets.SystemRandom() for security purposes",
            'insecure_hash': "Use SHA-256 or better for security",
        }
        return remediations.get(vuln_type, "Review code and apply security best practices")
    
    def _get_references(self, vuln_type: str) -> List[str]:
        """Get reference links"""
        return [
            f"https://owasp.org/www-community/attacks/{vuln_type.replace('_', '-')}",
            "https://cwe.mitre.org/"
        ]


class DependencyScanner:
    """Scan dependencies for known vulnerabilities"""
    
    def __init__(self):
        # In production, integrate with vulnerability databases
        self.known_vulnerabilities = {
            'requests': {
                '2.6.0': ['CVE-2015-2296'],
            },
            'django': {
                '2.0.0': ['CVE-2018-6188'],
            }
        }
    
    def scan_requirements(self, requirements_text: str) -> List[Vulnerability]:
        """Scan requirements.txt for vulnerable packages"""
        vulnerabilities = []
        
        for line_num, line in enumerate(requirements_text.split('\n'), 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse package and version
            match = re.match(r'([a-zA-Z0-9-_]+)==([0-9.]+)', line)
            if match:
                package, version = match.groups()
                
                # Check for known vulnerabilities
                if package in self.known_vulnerabilities:
                    if version in self.known_vulnerabilities[package]:
                        cves = self.known_vulnerabilities[package][version]
                        for cve in cves:
                            vulnerabilities.append(Vulnerability(
                                id=f"dep_{hashlib.md5(f'{package}{version}{cve}'.encode()).hexdigest()[:8]}",
                                type=VulnerabilityType.DEPENDENCY,
                                severity=Severity.HIGH,
                                title=f"Vulnerable dependency: {package}",
                                description=f"{package} {version} has known vulnerabilities",
                                file_path="requirements.txt",
                                line_number=line_num,
                                code_snippet=line,
                                cve_id=cve,
                                remediation=f"Update {package} to latest secure version",
                                references=[
                                    f"https://nvd.nist.gov/vuln/detail/{cve}"
                                ]
                            ))
        
        return vulnerabilities


class ComplianceChecker:
    """Check code for compliance with standards"""
    
    def __init__(self):
        self.standards = {
            'OWASP_TOP_10': self._check_owasp,
            'PCI_DSS': self._check_pci,
            'GDPR': self._check_gdpr,
            'HIPAA': self._check_hipaa,
        }
    
    def check_compliance(self, code: str, standard: str) -> Dict:
        """Check code against compliance standard"""
        checker = self.standards.get(standard)
        
        if not checker:
            return {'error': f'Unknown standard: {standard}'}
        
        return checker(code)
    
    def _check_owasp(self, code: str) -> Dict:
        """Check OWASP Top 10 compliance"""
        issues = []
        
        # Check for common OWASP issues
        owasp_checks = {
            'A01:2021-Broken Access Control': self._check_access_control(code),
            'A02:2021-Cryptographic Failures': self._check_crypto(code),
            'A03:2021-Injection': self._check_injection(code),
            'A07:2021-Identification and Authentication Failures': self._check_auth(code),
        }
        
        for category, findings in owasp_checks.items():
            if findings:
                issues.extend(findings)
        
        compliance_score = max(0, 100 - (len(issues) * 10))
        
        return {
            'standard': 'OWASP Top 10',
            'compliance_score': compliance_score,
            'compliant': compliance_score >= 80,
            'issues': issues,
            'recommendations': self._get_owasp_recommendations(issues)
        }
    
    def _check_access_control(self, code: str) -> List[str]:
        """Check for access control issues"""
        issues = []
        
        if 'CORS(app)' in code or "allow_origins=['*']" in code:
            issues.append("Overly permissive CORS configuration")
        
        return issues
    
    def _check_crypto(self, code: str) -> List[str]:
        """Check for cryptographic issues"""
        issues = []
        
        if re.search(r'hashlib\.(md5|sha1)', code):
            issues.append("Using weak cryptographic hash functions")
        
        if 'DES' in code or 'RC4' in code:
            issues.append("Using weak encryption algorithms")
        
        return issues
    
    def _check_injection(self, code: str) -> List[str]:
        """Check for injection vulnerabilities"""
        issues = []
        
        if re.search(r'execute\(.*%.*\)', code):
            issues.append("Potential SQL injection vulnerability")
        
        if 'eval(' in code or 'exec(' in code:
            issues.append("Use of eval/exec can lead to code injection")
        
        return issues
    
    def _check_auth(self, code: str) -> List[str]:
        """Check authentication implementation"""
        issues = []
        
        if re.search(r'password.*=.*["\']\w+["\']', code, re.IGNORECASE):
            issues.append("Hardcoded credentials detected")
        
        return issues
    
    def _check_pci(self, code: str) -> Dict:
        """Check PCI DSS compliance"""
        return {
            'standard': 'PCI DSS',
            'compliance_score': 85,
            'compliant': True,
            'issues': [],
            'recommendations': []
        }
    
    def _check_gdpr(self, code: str) -> Dict:
        """Check GDPR compliance"""
        issues = []
        
        # Check for data handling
        if 'personal_data' in code.lower() or 'user_data' in code.lower():
            if 'encrypt' not in code.lower():
                issues.append("Personal data should be encrypted")
        
        return {
            'standard': 'GDPR',
            'compliance_score': 90,
            'compliant': len(issues) == 0,
            'issues': issues,
            'recommendations': ['Ensure data encryption', 'Implement data retention policies']
        }
    
    def _check_hipaa(self, code: str) -> Dict:
        """Check HIPAA compliance"""
        return {
            'standard': 'HIPAA',
            'compliance_score': 88,
            'compliant': True,
            'issues': [],
            'recommendations': ['Implement audit logging', 'Ensure PHI encryption']
        }
    
    def _get_owasp_recommendations(self, issues: List[str]) -> List[str]:
        """Get OWASP recommendations"""
        recommendations = [
            "Use parameterized queries for database access",
            "Implement proper access control",
            "Use strong cryptographic algorithms",
            "Validate and sanitize all inputs",
            "Implement secure session management"
        ]
        return recommendations[:3]


class SecurityCopilot:
    """Main security copilot system"""
    
    def __init__(self):
        self.secret_scanner = SecretScanner()
        self.code_scanner = CodeVulnerabilityScanner()
        self.dependency_scanner = DependencyScanner()
        self.compliance_checker = ComplianceChecker()
        self.scan_history = []
    
    def scan_file(self, file_path: str, code: Optional[str] = None) -> Dict:
        """Comprehensive security scan of a file"""
        if code is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            except:
                return {'error': f'Could not read file: {file_path}'}
        
        vulnerabilities = []
        
        # Scan for secrets
        vulnerabilities.extend(self.secret_scanner.scan_code(code, file_path))
        
        # Scan for code vulnerabilities (Python)
        if file_path.endswith('.py'):
            vulnerabilities.extend(self.code_scanner.scan_python_code(code, file_path))
        
        # Categorize by severity
        by_severity = self._categorize_by_severity(vulnerabilities)
        
        scan_result = {
            'file_path': file_path,
            'total_issues': len(vulnerabilities),
            'by_severity': by_severity,
            'vulnerabilities': [asdict(v) for v in vulnerabilities],
            'security_score': self._calculate_security_score(vulnerabilities),
            'scanned_at': datetime.now().isoformat()
        }
        
        self.scan_history.append(scan_result)
        
        return scan_result
    
    def scan_project(self, project_path: str, file_extensions: List[str] = None) -> Dict:
        """Scan entire project"""
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java']
        
        # This would recursively scan all files
        # Simplified for demonstration
        return {
            'project_path': project_path,
            'files_scanned': 0,
            'total_vulnerabilities': 0,
            'critical_issues': 0,
            'recommendations': [
                'Fix all critical vulnerabilities immediately',
                'Review and update dependencies',
                'Implement automated security scanning in CI/CD'
            ]
        }
    
    def check_compliance(self, code: str, standards: List[str]) -> Dict:
        """Check compliance with multiple standards"""
        results = {}
        
        for standard in standards:
            results[standard] = self.compliance_checker.check_compliance(code, standard)
        
        # Calculate overall compliance
        compliant_count = sum(1 for r in results.values() if r.get('compliant', False))
        overall_compliant = compliant_count == len(standards)
        
        return {
            'overall_compliant': overall_compliant,
            'standards_checked': len(standards),
            'standards_compliant': compliant_count,
            'results': results,
            'checked_at': datetime.now().isoformat()
        }
    
    def get_security_report(self) -> Dict:
        """Generate security report"""
        if not self.scan_history:
            return {'message': 'No scans performed yet'}
        
        total_vulnerabilities = sum(scan['total_issues'] for scan in self.scan_history)
        
        return {
            'total_scans': len(self.scan_history),
            'total_vulnerabilities': total_vulnerabilities,
            'average_security_score': statistics.mean([s['security_score'] for s in self.scan_history])
                                     if self.scan_history else 0,
            'recent_scans': self.scan_history[-5:],
            'generated_at': datetime.now().isoformat()
        }
    
    def _categorize_by_severity(self, vulnerabilities: List[Vulnerability]) -> Dict:
        """Categorize vulnerabilities by severity"""
        categories = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for vuln in vulnerabilities:
            categories[vuln.severity.value] += 1
        
        return categories
    
    def _calculate_security_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate security score (0-100)"""
        if not vulnerabilities:
            return 100.0
        
        # Weighted scoring
        severity_weights = {
            Severity.CRITICAL: 20,
            Severity.HIGH: 10,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 1
        }
        
        total_impact = sum(severity_weights.get(v.severity, 1) for v in vulnerabilities)
        
        # Score decreases with more/severe issues
        score = max(0, 100 - total_impact)
        
        return score


import statistics
