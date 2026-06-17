import os
import json
import pickle
import random
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# Predefined variables for generating diverse non-farming examples
ACTORS = ["NTR", "Prabhas", "Mahesh Babu", "Allu Arjun", "Ram Charan", "Shah Rukh Khan", "Salman Khan", "Aamir Khan", "Amitabh Bachchan", "Rajinikanth", "Deepika Padukone", "Pawan Kalyan", "Nani", "Jr NTR"]
MOVIES = ["Devara", "Pushpa 2", "Salaar", "Kalki 2898 AD", "RRR", "Baahubali", "Inception", "Titanic", "Oppenheimer", "Interstellar", "Avatar", "Jawan", "Pathaan", "Dangal", "Bahubali 2", "Game Changer"]
STATES = ["Maharashtra", "Punjab", "Gujarat", "Karnataka", "Uttar Pradesh", "Haryana", "Madhya Pradesh", "Tamil Nadu", "Andhra Pradesh", "Rajasthan"]
YEARS = ["2023", "2024", "2025", "2026", "2027"]

non_farming_categories = {
    "movies": [
        "suggest me a movie", "best movies in {year}", "recommend a movie", "who is the actor in {movie}",
        "tell me about {movie} movie", "upcoming movies of {actor}", "who directed {movie}", "showtimes for {movie}",
        "web series to watch on Netflix", "popular TV shows", "Oscar awards best picture winner",
        "who won best actor for {movie}", "box office collection of {movie}", "thriller movie suggestions",
        "best comedy film", "top romantic movies", "science fiction movies list", "is there a new {actor} film",
        "cast of {movie}", "synopsis of {movie}", "NTR upcoming movie", "best NTR movies", "who acted in {movie}",
        "show me list of movies directed by Christopher Nolan", "actors in Game Changer movie"
    ],
    "politics": [
        "who is the prime minister of India", "who won the elections", "BJP congress coalition news",
        "who is the president of USA", "political debates on TV", "what is government policy on taxes",
        "assembly election results date", "parliament session bill updates", "who is the governor of {state}",
        "local politics discussion", "corruption news today", "Supreme court judgement updates",
        "what is democracy", "how is voting done in India", "who is the chief minister of Maharashtra",
        "news about political parties", "upcoming political rally in Delhi", "who is the Prime Minister of UK",
        "political updates", "foreign policy of India", "trade agreement details", "Narendra Modi speech today",
        "Rahul Gandhi rally updates"
    ],
    "sports": [
        "who won the IPL match today", "cricket live score card", "IPL points table", "T20 world cup schedule",
        "Lionel Messi total goals", "Cristiano Ronaldo statistics", "Real Madrid match tomorrow",
        "who won the tennis final", "Wimbledon matches schedule", "Olympic gold medal winners list",
        "Formula 1 race calendar", "who won the badminton trophy", "soccer transfer news", "IPL scores",
        "NBA finals schedule", "who is the best batsman in the world", "Virat Kohli runs", "Dhoni retirement news",
        "sports updates", "who is playing in the final today", "live updates on the match", "T20 world cup match score"
    ],
    "technology": [
        "best laptop under 50000", "Nvidia RTX 5080 release date", "graphics card prices", "how to build a PC",
        "iPhone 16 pro max reviews", "macbook pro m4 vs m3 specs", "how to write a Python script",
        "JavaScript coding tutorial", "React frontend development guides", "what is cloud computing",
        "machine learning algorithms overview", "best programming language for data science", "how to install Windows 11",
        "PC building tutorial", "Android vs iOS comparison", "best smartwatches in 2026", "what is a server",
        "how to debug a code error", "artificial intelligence updates", "ChatGPT vs Claude comparison",
        "learn Java programming", "AMD Ryzen processor prices", "best budget phone under 15000"
    ],
    "general_knowledge": [
        "what time is it", "who won the match", "capital of Australia", "capital of France", "how far is the moon",
        "tell me a joke", "what is 2 + 2", "define photosynthesis", "history of French revolution",
        "why is the sky blue", "largest country by population", "longest river in the world", "how does internet work",
        "who wrote Romeo and Juliet", "are you a human", "what is your name", "how to make a cup of tea",
        "explain quantum physics simply", "what is the speed of light", "inventor of telephone", "how to tie a tie",
        "facts about dinosaurs", "how many states in India", "what is the currency of Japan", "who is the PM of India"
    ]
}

def generate_non_farming(count=1300):
    samples = []
    keys = list(non_farming_categories.keys())
    # Generate count samples (duplicates are fine as templates are limited to ~288 unique combinations)
    for _ in range(count):
        cat = random.choice(keys)
        tpl = random.choice(non_farming_categories[cat])
        text = tpl.format(
            actor=random.choice(ACTORS),
            movie=random.choice(MOVIES),
            state=random.choice(STATES),
            year=random.choice(YEARS)
        )
        samples.append(text)
    return samples

def train_classifier():
    print("--------------------------------------------------")
    print("Training Farming Domain Classifier Model")
    print("--------------------------------------------------")
    
    # 1. Load Farming Dataset
    dataset_path = "intent_train_dataset.json"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Farming intent dataset not found. Please run generate_intent_dataset.py first.")
        
    with open(dataset_path, "r") as f:
        farming_data = json.load(f)
        
    farming_texts = [item["text"] for item in farming_data]
    print(f"Loaded {len(farming_texts)} farming examples.")
    
    # 2. Generate Non-Farming Dataset
    non_farming_texts = generate_non_farming(len(farming_texts) + 100)
    print(f"Generated {len(non_farming_texts)} non-farming examples.")
    
    # Prepare labels (FARMING = 1, NON_FARMING = 0)
    X_texts = farming_texts + non_farming_texts
    y = np.array([1] * len(farming_texts) + [0] * len(non_farming_texts))
    
    # 3. Load Embedding Model
    print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Compute embeddings
    print("Encoding texts to embeddings...")
    X_emb = model.encode(X_texts, show_progress_bar=True)
    
    # 4. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_emb, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # 5. Train Classifier (LogisticRegression)
    print("Training LogisticRegression classifier...")
    clf = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate
    preds = clf.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    print(f"Evaluation Accuracy: {accuracy * 100:.2f}%")
    print("Classification Report:")
    print(classification_report(y_test, preds, target_names=["NON_FARMING", "FARMING"]))
    
    # 6. Save the trained model
    os.makedirs("models", exist_ok=True)
    model_save_path = "models/farming_domain_classifier.pkl"
    with open(model_save_path, "wb") as f:
        pickle.dump(clf, f)
        
    print(f"Domain classifier model saved to: {model_save_path}")

if __name__ == "__main__":
    train_classifier()
