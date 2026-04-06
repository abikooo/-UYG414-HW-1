import torch
import torch.nn as nn
import numpy as np
from core.logger import log

class Autoencoder(nn.Module):
    def __init__(self, input_dim=128):
        super(Autoencoder, self).__init__()
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 8),
            nn.ReLU()
        )
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(8, 32),
            nn.ReLU(),
            nn.Linear(32, input_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

class LocalMLService:
    def __init__(self, input_dim=128):
        self.input_dim = input_dim
        self.model = Autoencoder(input_dim)
        self.criterion = nn.MSELoss()
        # In a real app, you would load weights from a trained file
        # For demonstration, we'll use randomized (but deterministic) weights
        torch.manual_seed(42)
        
    def _vectorize(self, text: str) -> torch.Tensor:
        # Simple character-level ASCII frequency vectorization
        vec = np.zeros(self.input_dim)
        for char in text[:512]: # Limit to first 512 chars for speed
            code = ord(char)
            if code < self.input_dim:
                vec[code] += 1
        
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
            
        return torch.tensor(vec, dtype=torch.float32)

    def get_anomaly_score(self, text: str) -> float:
        """
        Calculates the reconstruction error of the log message.
        Higher score = More anomalous.
        """
        try:
            self.model.eval()
            with torch.no_grad():
                input_vec = self._vectorize(text)
                output_vec = self.model(input_vec)
                loss = self.criterion(output_vec, input_vec)
                return float(loss.item() * 100) # Scaling for readability
        except Exception as e:
            log.error("local_ml_error", error=str(e))
            return 0.0

    def is_anomalous(self, text: str, threshold: float = 0.5) -> bool:
        score = self.get_anomaly_score(text)
        return score > threshold
