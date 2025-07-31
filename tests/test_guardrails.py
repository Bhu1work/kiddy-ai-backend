"""Unit tests for app.core.guardrails module."""

import pytest
from unittest.mock import patch, MagicMock

from app.core.guardrails import sanitize, within_daily_budget


class TestSanitize:
    """Test PII scrubbing functionality."""
    
    def test_sanitize_ssn(self):
        """Test SSN redaction."""
        text = "My SSN is 123-45-6789 and I live in NYC"
        result = sanitize(text)
        assert "123-45-6789" not in result
        assert "[redacted]" in result
        assert "NYC" in result  # Should not be redacted
    
    def test_sanitize_phone(self):
        """Test phone number redaction."""
        text = "Call me at 5551234567 or (555) 123-4567"
        result = sanitize(text)
        assert "5551234567" not in result
        assert "(555) 123-4567" not in result
        assert result.count("[redacted]") == 2
    
    def test_sanitize_email(self):
        """Test email redaction."""
        text = "Contact me at test@example.com"
        result = sanitize(text)
        assert "test@example.com" not in result
        assert "[redacted]" in result
    
    def test_sanitize_zip(self):
        """Test ZIP code redaction."""
        text = "I live in 12345 and work in 67890-1234"
        result = sanitize(text)
        assert "12345" not in result
        assert "67890-1234" not in result
        assert result.count("[redacted]") == 2
    
    def test_sanitize_clean_text(self):
        """Test text with no PII."""
        text = "Hello, how are you today?"
        result = sanitize(text)
        assert result == text
    
    def test_sanitize_multiple_pii(self):
        """Test multiple PII types in one text."""
        text = "Call 5551234567 or email test@example.com"
        result = sanitize(text)
        assert "5551234567" not in result
        assert "test@example.com" not in result
        assert result.count("[redacted]") == 2


class TestTokenBucket:
    """Test daily token budget functionality."""
    
    def test_within_daily_budget_new_session(self):
        """Test new session starts with zero tokens."""
        session_id = "test_session_1"
        text = "Hello world"
        result = within_daily_budget(session_id, text)
        assert result is True
    
    def test_within_daily_budget_existing_session(self):
        """Test existing session accumulates tokens."""
        session_id = "test_session_2"
        text = "Hello world"
        
        # First call should succeed
        result1 = within_daily_budget(session_id, text)
        assert result1 is True
        
        # Second call should also succeed (unless over limit)
        result2 = within_daily_budget(session_id, text)
        assert result2 is True
    
    @patch('app.core.guardrails._MAX_TOKENS', 10)  # Very low limit for testing
    def test_within_daily_budget_exceeds_limit(self):
        """Test when daily limit is exceeded."""
        session_id = "test_session_3"
        long_text = "This is a very long text that should exceed the token limit " * 10
        
        # Should fail due to length
        result = within_daily_budget(session_id, long_text)
        assert result is False
    
    def test_within_daily_budget_different_sessions(self):
        """Test that different sessions have separate budgets."""
        session1 = "session_1"
        session2 = "session_2"
        text = "Hello world"
        
        # Both should succeed independently
        result1 = within_daily_budget(session1, text)
        result2 = within_daily_budget(session2, text)
        
        assert result1 is True
        assert result2 is True
    
    @patch('app.core.guardrails.time.time')
    def test_within_daily_budget_reset_after_24h(self, mock_time):
        """Test that bucket resets after 24 hours."""
        session_id = "test_session_4"
        text = "Hello world"
        
        # Set initial time
        mock_time.return_value = 1000.0
        
        # First call
        result1 = within_daily_budget(session_id, text)
        assert result1 is True
        
        # Advance time by 25 hours (more than 24 hours)
        mock_time.return_value = 1000.0 + (25 * 3600)
        
        # Should reset and succeed again
        result2 = within_daily_budget(session_id, text)
        assert result2 is True


if __name__ == "__main__":
    pytest.main([__file__]) 