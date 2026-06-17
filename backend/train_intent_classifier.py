import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer

# Mapping of labels to indices
INTENTS = [
    'WEATHER_QUERY',
    'FERTILIZER_QUERY',
    'IRRIGATION_QUERY',
    'PEST_QUERY',
    'FARM_DATA_QUERY',
    'CROP_RECOMMENDATION_QUERY',
    'DISEASE_QUERY',
    'CROP_SOIL_REQUIREMENT_QUERY'
]
INTENT_TO_IDX = {intent: idx for idx, intent in enumerate(INTENTS)}

class IntentClassifier(nn.Module):
    def __init__(self, input_dim=384, num_classes=8):
        super().__init__()
        self.fc = nn.Linear(input_dim, num_classes)
        
    def forward(self, x):
        return self.fc(x)

def train_classifier():
    os.makedirs("models", exist_ok=True)
    
    # Load dataset
    dataset_path = "intent_train_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset {dataset_path} not found. Run generate_intent_dataset.py first.")
        return
        
    with open(dataset_path, "r") as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} examples.")
    
    # Initialize SentenceTransformer
    print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Prepare inputs and targets
    texts = [item["text"] for item in data]
    labels = [INTENT_TO_IDX[item["label"]] for item in data]
    
    print("Encoding sentences into embeddings (this might take a few seconds)...")
    embeddings = embedding_model.encode(texts, show_progress_bar=True, convert_to_tensor=True)
    targets = torch.tensor(labels, dtype=torch.long, device=embeddings.device)
    
    # Shuffle and split into train / val
    num_samples = len(data)
    indices = torch.randperm(num_samples)
    
    split = int(num_samples * 0.9)
    train_indices = indices[:split]
    val_indices = indices[split:]
    
    train_embeddings = embeddings[train_indices]
    train_targets = targets[train_indices]
    
    val_embeddings = embeddings[val_indices]
    val_targets = targets[val_indices]
    
    # Build model
    model = IntentClassifier(input_dim=384, num_classes=8).to(embeddings.device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    epochs = 30
    batch_size = 64
    
    print("Starting training loop...")
    for epoch in range(epochs):
        model.train()
        permutation = torch.randperm(train_embeddings.size(0))
        epoch_loss = 0.0
        
        for i in range(0, train_embeddings.size(0), batch_size):
            optimizer.zero_grad()
            indices_batch = permutation[i:i+batch_size]
            batch_x = train_embeddings[indices_batch]
            batch_y = train_targets[indices_batch]
            
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * batch_x.size(0)
            
        epoch_loss /= train_embeddings.size(0)
        
        # Validation accuracy
        model.eval()
        with torch.no_grad():
            val_outputs = model(val_embeddings)
            val_loss = criterion(val_outputs, val_targets).item()
            preds = val_outputs.argmax(dim=1)
            val_acc = (preds == val_targets).float().mean().item()
            
        print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss:.4f} - Val Loss: {val_loss:.4f} - Val Acc: {val_acc * 100:.2f}%")
        
    # Save the model
    save_path = "models/intent_classifier.pt"
    torch.save(model.state_dict(), save_path)
    
    # Save intent classes mapping
    with open("models/intent_classes.json", "w") as f:
        json.dump(INTENTS, f)
        
    print(f"\nTraining complete! Model weights saved to: {save_path}")
    print("Class mapping saved to: models/intent_classes.json")

if __name__ == "__main__":
    train_classifier()
