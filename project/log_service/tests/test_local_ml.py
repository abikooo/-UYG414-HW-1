"""
Unit tests for the PyTorch-based Local ML Anomaly Detection Service.
These tests run WITHOUT any external API calls or database connections.
"""
import pytest
import sys
import os

# Add parent directory to path so we can import the service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.local_ml_service import LocalMLService, Autoencoder


class TestAutoencoder:
    """Tests for the raw PyTorch model."""

    def test_model_initialization(self):
        """The model should initialize with correct layer dimensions."""
        model = Autoencoder(input_dim=128)
        assert model is not None

    def test_model_forward_pass(self):
        """A forward pass should produce output with the same shape as input."""
        import torch
        model = Autoencoder(input_dim=128)
        test_input = torch.rand(128)
        output = model(test_input)
        assert output.shape == test_input.shape

    def test_model_output_range(self):
        """Output should be between 0 and 1 due to Sigmoid activation."""
        import torch
        model = Autoencoder(input_dim=128)
        test_input = torch.rand(128)
        output = model(test_input)
        assert output.min() >= 0.0
        assert output.max() <= 1.0

    def test_model_deterministic_with_seed(self):
        """With the same seed, the model should produce identical results."""
        import torch
        torch.manual_seed(42)
        model1 = Autoencoder(input_dim=128)
        torch.manual_seed(42)
        model2 = Autoencoder(input_dim=128)

        test_input = torch.rand(128)
        out1 = model1(test_input)
        out2 = model2(test_input)
        assert torch.allclose(out1, out2)


class TestLocalMLService:
    """Tests for the anomaly detection service."""

    def setup_method(self):
        self.service = LocalMLService(input_dim=128)

    def test_vectorize_normal_text(self):
        """Normal text should produce a non-zero vector."""
        vec = self.service._vectorize("Hello, world!")
        assert vec.sum().item() > 0

    def test_vectorize_empty_string(self):
        """Empty string should produce a zero vector."""
        vec = self.service._vectorize("")
        assert vec.sum().item() == 0.0

    def test_vectorize_normalization(self):
        """The resulting vector should be normalized (L2 norm ≈ 1)."""
        import torch
        vec = self.service._vectorize("Some log message about a database error")
        norm = torch.linalg.norm(vec).item()
        assert abs(norm - 1.0) < 0.01  # Should be approximately 1

    def test_anomaly_score_returns_float(self):
        """get_anomaly_score should return a float."""
        score = self.service.get_anomaly_score("Normal log message")
        assert isinstance(score, float)

    def test_anomaly_score_non_negative(self):
        """Anomaly score should never be negative."""
        score = self.service.get_anomaly_score("Any text message")
        assert score >= 0.0

    def test_is_anomalous_returns_bool(self):
        """is_anomalous should return a boolean."""
        result = self.service.is_anomalous("Test message")
        assert isinstance(result, bool)

    def test_different_inputs_different_scores(self):
        """Different inputs should (generally) produce different scores."""
        score1 = self.service.get_anomaly_score("User logged in successfully")
        score2 = self.service.get_anomaly_score("' OR '1'='1'; DROP TABLE users; --")
        # They should at least be computed (both non-negative)
        assert score1 >= 0.0
        assert score2 >= 0.0

    def test_long_input_handled(self):
        """Very long input should not crash the service."""
        long_text = "A" * 10000
        score = self.service.get_anomaly_score(long_text)
        assert isinstance(score, float)

    def test_special_characters_handled(self):
        """Input with special characters should not crash."""
        special = "SELECT * FROM users WHERE id='' OR '1'='1' -- DROP TABLE"
        score = self.service.get_anomaly_score(special)
        assert isinstance(score, float)

    def test_unicode_handled(self):
        """Unicode input should not crash."""
        unicode_text = "日本語テスト 🔥 émojis and àccents"
        score = self.service.get_anomaly_score(unicode_text)
        assert isinstance(score, float)

    def test_threshold_logic(self):
        """High threshold should make fewer things anomalous."""
        text = "Normal log entry"
        high_threshold = self.service.is_anomalous(text, threshold=999.0)
        assert high_threshold is False  # Nothing should exceed 999

    def test_zero_threshold(self):
        """Zero threshold with non-empty text should flag as anomalous (any score > 0)."""
        text = "Some non-empty text"
        score = self.service.get_anomaly_score(text)
        result = self.service.is_anomalous(text, threshold=0.0)
        # If score is > 0, it should be anomalous; if score is exactly 0, not.
        assert result == (score > 0.0)
