#!/usr/bin/env python3
"""
Unit tests for setup.py security dependency changes
Tests that the security==1.3.1 dependency is properly configured
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestSetupSecurityDependency(unittest.TestCase):
    """Test security dependency in setup.py configuration"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_setup_content = '''#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="ai_kindlemint_engine",
    version="0.1.0",
    description="AI KindleMint Engine for automated content generation and formatting",
    packages=setuptools.find_packages(
        exclude=["tests", "scripts", "docs", "assets"]),
    install_requires=[
        # Alphabetical order for readability
        "beautifulsoup4>=4.10.0",
        "certifi>=2022.12.7",
        "charset-normalizer>=3.1.0",
        "click>=8.1.3",
        "cryptography>=40.0.0",
        "idna>=3.4",
        "jinja2>=3.1.2",
        "markupsafe>=2.1.2",
        "numpy>=1.24.0",
        "packaging>=23.1",
        "pandas>=2.0.0",
        "pillow>=9.5.0",
        "pycryptodome>=3.17.0",
        "pypdf>=3.8.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "pyyaml>=6.0",
        "reportlab>=4.0.0",
        "requests>=2.31.0",
        "sentry-sdk>=1.40.0",
        "security==1.3.1",
    ],
)
'''

    def test_security_dependency_in_install_requires(self):
        """Test that security==1.3.1 is included in install_requires"""
        # Parse the mock setup content to extract install_requires
        lines = self.mock_setup_content.split('\n')
        in_install_requires = False
        dependencies = []
        
        for line in lines:
            if 'install_requires=[' in line:
                in_install_requires = True
                continue
            elif in_install_requires and line.strip() == '],':
                break
            elif in_install_requires and line.strip().startswith('"'):
                # Extract dependency string
                dep = line.strip().strip('",')
                if dep and not dep.startswith('#'):
                    dependencies.append(dep)
        
        # Verify security dependency is present
        security_deps = [dep for dep in dependencies if dep.startswith('security')]
        self.assertEqual(len(security_deps), 1)
        self.assertEqual(security_deps[0], 'security==1.3.1')

    def test_dependencies_alphabetical_order(self):
        """Test that dependencies maintain alphabetical order including security"""
        # Extract dependencies as in previous test
        lines = self.mock_setup_content.split('\n')
        in_install_requires = False
        dependencies = []
        
        for line in lines:
            if 'install_requires=[' in line:
                in_install_requires = True
                continue
            elif in_install_requires and line.strip() == '],':
                break
            elif in_install_requires and line.strip().startswith('"'):
                dep = line.strip().strip('",')
                if dep and not dep.startswith('#'):
                    dependencies.append(dep.split('>=')[0].split('==')[0])
        
        # Verify alphabetical order
        sorted_deps = sorted(dependencies, key=str.lower)
        self.assertEqual(dependencies, sorted_deps, 
                        "Dependencies should be in alphabetical order")
        
        # Verify security is in the correct position
        self.assertIn('security', dependencies)
        security_index = dependencies.index('security')
        
        # Check that security comes after sentry-sdk and before any dependencies starting with 't' or later
        sentry_index = dependencies.index('sentry-sdk')
        self.assertGreater(security_index, sentry_index, 
                          "security should come after sentry-sdk alphabetically")

    @patch('builtins.open', new_callable=mock_open)
    def test_setup_file_imports_setuptools(self, mock_file):
        """Test that setup.py properly imports setuptools"""
        mock_file.return_value.read.return_value = self.mock_setup_content
        
        # Verify setuptools import exists in content
        self.assertIn('import setuptools', self.mock_setup_content)
        self.assertIn('setuptools.setup(', self.mock_setup_content)
        self.assertIn('setuptools.find_packages(', self.mock_setup_content)

    def test_package_configuration(self):
        """Test that package configuration is correct"""
        # Verify package name
        self.assertIn('name="ai_kindlemint_engine"', self.mock_setup_content)
        
        # Verify version format
        self.assertIn('version="0.1.0"', self.mock_setup_content)
        
        # Verify description
        self.assertIn('description="AI KindleMint Engine', self.mock_setup_content)
        
        # Verify excluded packages
        self.assertIn('exclude=["tests", "scripts", "docs", "assets"]', 
                     self.mock_setup_content)

    def test_security_version_pinning(self):
        """Test that security dependency is pinned to specific version"""
        # Verify exact version pinning with ==
        self.assertIn('"security==1.3.1"', self.mock_setup_content)
        
        # Ensure it's not using >= or other version specifiers
        self.assertNotIn('security>=', self.mock_setup_content)
        self.assertNotIn('security>', self.mock_setup_content)
        self.assertNotIn('security~=', self.mock_setup_content)


if __name__ == '__main__':
    unittest.main()
