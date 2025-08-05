"""Unit tests for app.core.guardrails module."""

import pytest
import re

from app.core.guardrails import sanitize


class TestSanitize:
    """Test PII sanitization functionality."""
    
    def test_sanitize_no_pii(self):
        """Test text with no PII remains unchanged."""
        text = "Hello, how are you today?"
        result = sanitize(text)
        assert result == text
    
    def test_sanitize_ssn(self):
        """Test SSN pattern is redacted."""
        text = "My SSN is 123-45-6789"
        result = sanitize(text)
        assert "[redacted]" in result
        assert "123-45-6789" not in result
    
    def test_sanitize_ssn_multiple(self):
        """Test multiple SSNs are redacted."""
        text = "SSN1: 123-45-6789 and SSN2: 987-65-4321"
        result = sanitize(text)
        assert result.count("[redacted]") == 2
        assert "123-45-6789" not in result
        assert "987-65-4321" not in result
    
    def test_sanitize_phone_number_10_digits(self):
        """Test 10-digit phone number is redacted."""
        text = "Call me at 1234567890"
        result = sanitize(text)
        assert "[redacted]" in result
        assert "1234567890" not in result
    
    def test_sanitize_phone_number_with_parentheses(self):
        """Test phone number with parentheses is redacted."""
        text = "Call me at (123) 456-7890"
        result = sanitize(text)
        assert "[redacted]" in result
        assert "(123) 456-7890" not in result
    
    def test_sanitize_phone_number_with_spaces(self):
        """Test phone number with spaces is redacted."""
        text = "Call me at (123) 456-7890"
        result = sanitize(text)
        assert "[redacted]" in result
        assert "(123) 456-7890" not in result
    
    def test_sanitize_zip_code_5_digits(self):
        """Test 5-digit ZIP code is redacted."""
        text = "My address is 123 Main St, 12345"
        result = sanitize(text)
        assert "[redacted]" in result
        assert "12345" not in result
    
    def test_sanitize_zip_code_9_digits(self):
        """Test 9-digit ZIP code is redacted."""
        text = "My address is 123 Main St, 12345-6789"
        result = sanitize(text)
        assert "[redacted]" in result
        assert "12345-6789" not in result
    
    def test_sanitize_email_address(self):
        """Test email address is redacted."""
        text = "Contact me at john.doe@example.com"
        result = sanitize(text)
        assert "[redacted]" in result
        assert "john.doe@example.com" not in result
    
    def test_sanitize_email_with_subdomain(self):
        """Test email with subdomain is redacted."""
        text = "Contact me at user@sub.example.com"
        result = sanitize(text)
        assert "[redacted]" in result
        assert "user@sub.example.com" not in result
    
    def test_sanitize_multiple_pii_types(self):
        """Test multiple types of PII in same text."""
        text = "Contact: john@example.com, SSN: 123-45-6789, Phone: (555) 123-4567"
        result = sanitize(text)
        assert result.count("[redacted]") == 3
        assert "john@example.com" not in result
        assert "123-45-6789" not in result
        assert "(555) 123-4567" not in result
    
    def test_sanitize_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with empty string
        assert sanitize("") == ""
        
        # Test with only PII
        text = "123-45-6789"
        result = sanitize(text)
        assert result == "[redacted]"
        
        # Test with PII at boundaries
        text = "123-45-6789 and some text"
        result = sanitize(text)
        assert result == "[redacted] and some text"
    
    def test_sanitize_partial_matches_not_redacted(self):
        """Test that partial matches are not redacted."""
        # 9 digits (not SSN format)
        text = "Number: 123456789"
        result = sanitize(text)
        assert result == text
        
        # 11 digits (not phone format)
        text = "Number: 12345678901"
        result = sanitize(text)
        assert result == text
        
        # Invalid email format
        text = "Invalid: user@"
        result = sanitize(text)
        assert result == text
    
    def test_sanitize_case_insensitive_email(self):
        """Test email redaction is case insensitive."""
        text = "Emails: USER@EXAMPLE.COM and user@Example.com"
        result = sanitize(text)
        assert result.count("[redacted]") == 2
        assert "USER@EXAMPLE.COM" not in result
        assert "user@Example.com" not in result
    
    def test_sanitize_mixed_content(self):
        """Test mixed content with PII and normal text."""
        text = "Hello! My name is John. You can reach me at john@example.com or call (555) 123-4567. My SSN is 123-45-6789 and I live in ZIP 12345."
        result = sanitize(text)
        
        # Should have 4 redactions
        assert result.count("[redacted]") == 4
        
        # Original PII should not be present
        assert "john@example.com" not in result
        assert "(555) 123-4567" not in result
        assert "123-45-6789" not in result
        assert "12345" not in result
        
        # Normal text should remain
        assert "Hello!" in result
        assert "My name is John" in result
        assert "You can reach me at" in result
        assert "or call" in result
        assert "and I live in ZIP" in result


if __name__ == "__main__":
    pytest.main([__file__]) 