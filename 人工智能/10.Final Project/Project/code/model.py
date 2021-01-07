import torch
import torch.nn as nn


class QNet(nn.Module):
    def __init__(self, embedding_dim=512):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 64, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        self.conv3 = nn.Conv2d(128, 128, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.conv4 = nn.Conv2d(128, 128, 3, padding=1)
        self.bn4 = nn.BatchNorm2d(128)
        self.fc1 = nn.Linear(8 * 8 * 128, embedding_dim)
        self.fc2 = nn.Linear(embedding_dim, 65)

    def forward(self, x):
        x = x.view(-1, 1, 8, 8)
        x = torch.relu(self.bn1(self.conv1(x)))
        x = torch.relu(self.bn2(self.conv2(x)))
        x = torch.relu(self.bn3(self.conv3(x)))
        x = torch.relu(self.bn4(self.conv4(x)))
        x = torch.sigmoid(self.fc1(x.view(-1, 8 * 8 * 128)))
        # embedding = x
        x = torch.sigmoid(self.fc2(x))
        return x  # , embedding
