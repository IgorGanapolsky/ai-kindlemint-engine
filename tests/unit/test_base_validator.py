#!/usr/bin/env python3
"""Tests for base_validator module - improve coverage from 55% to 85%+"""

import tempfile
from pathlib import Path

import pytest

from kindlemint.validators.base_validator import (
    BaseValidator,
    ValidationError,
    ValidationLevel,
    ValidationResult,
)


class TestValidationResult:
    """Test ValidationResult dataclass"""

        """Test Validation Result Creation"""
def test_validation_result_creation(self):
        """Test creating validation results"""
        result = ValidationResult(
            is_valid=True, errors=[], warnings=["Minor issue"], info={"pages": 100}
        )
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert result.info["pages"] == 100

        """Test Validation Result Invalid"""
def test_validation_result_invalid(self):
        """Test invalid validation result"""
        result = ValidationResult(
            is_valid=False,
            errors=["Critical error", "Another error"],
            warnings=[],
            info={},
        )
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert "Critical error" in result.errors


class TestValidationLevel:
    """Test ValidationLevel enum"""

        """Test Validation Levels"""
def test_validation_levels(self):
        """Test validation level values"""
        assert ValidationLevel.ERROR.value == "error"
        assert ValidationLevel.WARNING.value == "warning"
        assert ValidationLevel.INFO.value == "info"

        """Test Level Comparison"""
def test_level_comparison(self):
        """Test we can compare levels"""
        levels = list(ValidationLevel)
        assert len(levels) == 3


class TestBaseValidator:
    """Test BaseValidator abstract class"""

        """Test Base Validator Abstract"""
def test_base_validator_abstract(self):
        """Test that BaseValidator is abstract"""
        with pytest.raises(TypeError):
            BaseValidator()

        """Test Validator Implementation"""
def test_validator_implementation(self):
        """Test implementing a validator"""

        class TestValidator(BaseValidator):
                """Validate"""
def validate(self, data):
                if data == "valid":
                    return ValidationResult(True, [], [], {})
                else:
                    return ValidationResult(False, ["Invalid data"], [], {})

                """Validate File"""
def validate_file(self, file_path):
                if file_path.exists():
                    return ValidationResult(True, [], [], {"file": str(file_path)})
                else:
                    return ValidationResult(False, ["File not found"], [], {})

        validator = TestValidator()

        # Test validate method
        result = validator.validate("valid")
        assert result.is_valid is True

        result = validator.validate("invalid")
        assert result.is_valid is False
        assert "Invalid data" in result.errors

        # Test validate_file method
        with tempfile.NamedTemporaryFile() as f:
            result = validator.validate_file(Path(f.name))
            assert result.is_valid is True

        result = validator.validate_file(Path("/nonexistent/file.txt"))
        assert result.is_valid is False

        """Test Validation Error"""
def test_validation_error(self):
        """Test ValidationError exception"""
        error = ValidationError("Test error", level=ValidationLevel.ERROR)
        assert str(error) == "Test error"
        assert error.level == ValidationLevel.ERROR

        warning = ValidationError("Test warning", level=ValidationLevel.WARNING)
        assert warning.level == ValidationLevel.WARNING

        """Test Validator With Config"""
def test_validator_with_config(self):
        """Test validator with configuration"""

        class ConfigurableValidator(BaseValidator):
                """  Init  """
def __init__(self, strict=False):
                self.strict = strict

                """Validate"""
def validate(self, data):
                if self.strict and not data:
                    return ValidationResult(False, ["Empty data not allowed"], [], {})
                return ValidationResult(True, [], [], {})

                """Validate File"""
def validate_file(self, file_path):
                return ValidationResult(True, [], [], {})

        validator = ConfigurableValidator(strict=True)
        result = validator.validate("")
        assert result.is_valid is False

        validator = ConfigurableValidator(strict=False)
        result = validator.validate("")
        assert result.is_valid is True
