
import torch.nn as nn
import torch.nn.functional as F

class EpilepsyCNN(nn.Module):
    def __init__(self):
        super(EpilepsyCNN, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv3d(1, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool3d(2),

            nn.Conv3d(8, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool3d(2),

            nn.Conv3d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool3d(2),
        )
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(32 * 8 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 2)

    def forward(self, x):
        x = self.conv(x)
        x = self.flatten(x)
        x = F.relu(self.fc1(x))
        return self.fc2(x)
