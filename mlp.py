import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import math
from PIL import Image
import json

import csv

import cv2



class GraspNet(nn.Module):
    def __init__(self):
        super().__init__()
        # CNN for image feature extraction
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=5, stride=2),  # 300->148
            nn.ReLU(),
            nn.MaxPool2d(2),  # 148->74
            nn.Conv2d(16, 32, kernel_size=5, stride=2), # 74->35
            nn.ReLU(),
            nn.MaxPool2d(2),  # 35->17
            nn.Flatten()
        )
        # Compute output size after CNN
        dummy = torch.zeros(1,3,300,300)
        
        n_cnn = self.cnn(dummy).shape[1]
        # MLP for pose+features -> score(not bin)
        
        self.mlp = nn.Sequential(
            nn.Linear(n_cnn, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    def forward(self, image):
        # pose: (B,4) [x,y,z,theta]
        # image: (B,3,300,300)
        features = self.cnn(image)
        x = torch.cat([features], dim=1)
        return self.mlp(x).squeeze(1)  # (B,)
        
def preprocess_sample(sample):
    # sample: dict with 'x','y','z','theta','image','grasp_score'
    pose = torch.tensor([sample['x'], sample['y'], sample['z'], sample['theta']], dtype=torch.float32)
    img = torch.tensor(sample['image'], dtype=torch.float32).permute(2,0,1) / 255.0  # (3,300,300)
    label = torch.tensor(sample['grasp_score'], dtype=torch.float32)
    return pose, img, label
    
    
    
#testing
def test(model, images, labels):
    total_loss = 0.0
        
    criterion = nn.BCELoss()
    
    res = []
    
    for i in range(len(images)):
        img = images[i]
        label = labels[i]
        out = model(img)
                    
        print("Model output:", out, "correct label:", label)
        
        loss = criterion(out, label.unsqueeze(0))
        res.append(out.item())
        print(loss.item())
                                
        total_loss += loss.item()
        print(total_loss)
        
    res = torch.tensor(res)
    print("res value", res)
    print("res value q", res > 0.5)
    print("labels value", labels)
    print("results:", torch.sum((res > 0.5).int() == labels) / len(images))
    print(total_loss)
    print(f"Test, Loss: {total_loss/len(images):.4f}")
    
#training
def train(model, images, labels, epochs=10, lr=1e-3):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()
    model.train()
    losses = []
    for epoch in range(epochs):
        total_loss = 0
        
        for i in range(len(images)):
            img = images[i]
            label = labels[i]
            
            out = model(img)
            loss = criterion(out, label.unsqueeze(0))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
                
        losses.append(total_loss/len(images))
        print(f"Epoch {epoch+1}, Loss: {total_loss/len(images):.4f}")
        
    plt.plot(losses)
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    
    plt.show()
# newviewpoint Sampling
def sample_viewpoints(n, bounds):
    # bounds: dict with 'x','y','z','theta' -> (min,max)
    samples = []
    for _ in range(n):
        s = {
            'x': np.random.uniform(*bounds['x']),
            'y': np.random.uniform(*bounds['y']),
            'z': np.random.uniform(*bounds['z']),
            'theta': np.random.uniform(*bounds['theta']),
        }
        samples.append(s)
    return samples
#Prediction Step (non bin)
def predict_best_grasp(model, image, bounds, n_samples=100):
    # image: numpy array (300,300,3)
    candidates = sample_viewpoints(n_samples, bounds)
    poses = []
    imgs = []
    for c in candidates:
        pose = torch.tensor([c['x'], c['y'], c['z'], c['theta']], dtype=torch.float32)
        img = torch.tensor(image, dtype=torch.float32).permute(2,0,1) / 255.0
        poses.append(pose)
        imgs.append(img)
    poses = torch.stack(poses)  # (N,4)
    imgs = torch.stack(imgs)    # (N,3,300,300)
    model.eval()
    with torch.no_grad():
        scores = model(imgs)
    best_idx = torch.argmax(scores)
    best_params = candidates[best_idx]
    best_score = scores[best_idx].item()
    return best_params, best_score
    
def load_data(data_count):
    images = []
    positions = []
    scores = []
    
    results_filename = "collected_data/project_results.csv"
    
    for i in range(data_count):
        current_image_filename = f"collected_data/out{i+1}_1.png"
        current_position_filename = f"collected_data/out_{i+1}.csv"
        
        image = cv2.imread(current_image_filename)
        image_tensor = (torch.tensor(image).float().permute(2,0,1) / 255.0).unsqueeze(0)
        images.append(image_tensor)
        
        with open(current_position_filename, 'r') as file:
            csvreader = csv.reader(file)
            for i, row in enumerate(csvreader):
                if i == 1:
                    positions.append([row[0], row[1], row[2]])
            
    with open(results_filename, 'r') as file:
        csvreader = csv.reader(file)
        for i, row in enumerate(csvreader):
            if i != 0:
                scores.append(int(row[1]))
        
    return images, torch.tensor(scores).float(), positions
    
    
if __name__ == "__main__":
    model = GraspNet()
    images, labels, positions = load_data(48)
            
    train(model, images[:36], labels[:36], epochs=50)
    #predict best grasp for new img
    bounds = {
        'x': (0, 1),
        'y': (0, 1),
        'z': (0, 1),
        'theta': (0, 2*np.pi)
    }
    
    test(model, images[36:], labels[36:])
    
    
    #test_image = np.random.randint(0, 256, size=(300, 300, 3), dtype=np.uint8)
    #best_grasp, score = predict_best_grasp(model, test_image, bounds)
    #print("\nBest grasp parameters:", best_grasp)
    #print("Predicted grasp score:", score)
