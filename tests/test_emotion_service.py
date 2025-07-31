"""Unit tests for app.services.emotion_service module."""

import pytest
from unittest.mock import patch, MagicMock

from app.services.emotion_service import detect_emotion
from app.core.constants import SENTIMENT_TO_EMOTION


class TestDetectEmotion:
    """Test sentiment to emotion mapping."""
    
    @patch('app.services.emotion_service._nl_client')
    def test_detect_emotion_positive(self, mock_client):
        """Test positive sentiment maps to cheerful."""
        # Mock response with positive sentiment
        mock_response = MagicMock()
        mock_response.document_sentiment.score = 0.5  # Positive
        mock_client.analyze_sentiment.return_value = mock_response
        
        result = detect_emotion("I'm so happy today!")
        assert result == SENTIMENT_TO_EMOTION["positive"]
    
    @patch('app.services.emotion_service._nl_client')
    def test_detect_emotion_negative(self, mock_client):
        """Test negative sentiment maps to affectionate."""
        # Mock response with negative sentiment
        mock_response = MagicMock()
        mock_response.document_sentiment.score = -0.3  # Negative
        mock_client.analyze_sentiment.return_value = mock_response
        
        result = detect_emotion("I'm feeling sad today.")
        assert result == SENTIMENT_TO_EMOTION["negative"]
    
    @patch('app.services.emotion_service._nl_client')
    def test_detect_emotion_neutral(self, mock_client):
        """Test neutral sentiment maps to curious."""
        # Mock response with neutral sentiment
        mock_response = MagicMock()
        mock_response.document_sentiment.score = 0.1  # Neutral
        mock_client.analyze_sentiment.return_value = mock_response
        
        result = detect_emotion("What is the weather like?")
        assert result == SENTIMENT_TO_EMOTION["neutral"]
    
    @patch('app.services.emotion_service._nl_client')
    def test_detect_emotion_boundary_positive(self, mock_client):
        """Test boundary case for positive sentiment."""
        # Mock response with boundary positive sentiment
        mock_response = MagicMock()
        mock_response.document_sentiment.score = 0.25  # Exactly at threshold
        mock_client.analyze_sentiment.return_value = mock_response
        
        result = detect_emotion("This is great!")
        assert result == SENTIMENT_TO_EMOTION["positive"]
    
    @patch('app.services.emotion_service._nl_client')
    def test_detect_emotion_boundary_negative(self, mock_client):
        """Test boundary case for negative sentiment."""
        # Mock response with boundary negative sentiment
        mock_response = MagicMock()
        mock_response.document_sentiment.score = -0.25  # Exactly at threshold
        mock_client.analyze_sentiment.return_value = mock_response
        
        result = detect_emotion("I'm not feeling well.")
        assert result == SENTIMENT_TO_EMOTION["negative"]
    
    @patch('app.services.emotion_service._nl_client')
    def test_detect_emotion_zero(self, mock_client):
        """Test zero sentiment maps to neutral."""
        # Mock response with zero sentiment
        mock_response = MagicMock()
        mock_response.document_sentiment.score = 0.0  # Zero
        mock_client.analyze_sentiment.return_value = mock_response
        
        result = detect_emotion("Hello there.")
        assert result == SENTIMENT_TO_EMOTION["neutral"]
    
    @patch('app.services.emotion_service._nl_client')
    def test_detect_emotion_calls_google_api(self, mock_client):
        """Test that Google Cloud Natural Language API is called correctly."""
        mock_response = MagicMock()
        mock_response.document_sentiment.score = 0.0
        mock_client.analyze_sentiment.return_value = mock_response
        
        text = "Test message"
        detect_emotion(text)
        
        # Verify the API was called with correct parameters
        mock_client.analyze_sentiment.assert_called_once()
        call_args = mock_client.analyze_sentiment.call_args[1]
        assert call_args['document'].content == text
        assert call_args['document'].type_.name == 'PLAIN_TEXT'


if __name__ == "__main__":
    pytest.main([__file__]) 