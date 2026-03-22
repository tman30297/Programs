# AI/ML Trends 2026 - Research Notes
## 2026-03-14

---

## 1. Large Language Models (LLMs)

### Leading Models
| Model | Provider | Key Features |
|-------|----------|--------------|
| GPT-4 | OpenAI | Multi-modal, reasoning |
| Claude | Anthropic | Helpful, harmless |
| Gemini | Google | Multi-modal, context |
| Llama | Meta | Open source |
| Mistral | Mistral AI | Efficient, open |

### Trends
- Smaller, efficient models
- Open-source alternatives
- Multi-modal capabilities
- Long context windows
- Function calling

---

## 2. Deep Learning Frameworks

### TensorFlow
```python
import tensorflow as tf

# Create model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=10)
```

### PyTorch
```python
import torch
import torch.nn as nn

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)
```

---

## 3. Hugging Face Ecosystem

### Transformers
```python
from transformers import pipeline

# Sentiment analysis
classifier = pipeline("sentiment-analysis")
result = classifier("I love learning!")

# Text generation
generator = pipeline("text-generation")
result = generator("Once upon a time")

# Translation
translator = pipeline("translation_en_to_fr")
result = translator("Hello world")
```

### Key Libraries
- **transformers** - Pre-trained models
- **diffusers** - Image generation
- **accelerate** - Distributed training
- **optimum** - Optimization

---

## 4. Computer Vision

### Key Libraries
| Library | Use Case |
|---------|----------|
| OpenCV | Image processing |
| Pillow | Image manipulation |
| torchvision | Vision models |
| albumentations | Augmentation |

### Object Detection
```python
import cv2

# Load cascade
face_cascade = cv2.CascadeClassifier('haarcascade.xml')

# Detect faces
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.1, 4)
```

---

## 5. MLOps

### Tools
- **MLflow** - ML lifecycle management
- **Kubeflow** - ML on Kubernetes
- **Weights & Biases** - Experiment tracking
- **Neptune** - Metadata store

### Key Practices
- Version control for models
- Experiment tracking
- Model registry
- Continuous training

---

## 6. Edge AI

### Frameworks
- **TensorFlow Lite** - Mobile/Edge
- **PyTorch Mobile** - iOS/Android
- **ONNX Runtime** - Cross-platform
- **MediaPipe** - Google's solution

### Optimization
- Quantization
- Pruning
- Knowledge distillation

---

## 7. Responsible AI

### Key Areas
- Bias detection/mitigation
- Explainability (XAI)
- Privacy-preserving ML
- Fairness frameworks

### Tools
- **Fairlearn** - Fairness toolkit
- **SHAP** - Feature importance
- **LIME** - Local explanations
- **AI Fairness 360** - IBM's toolkit

---

## 8. Federated Learning

### Concept
- Train on distributed data
- Keep data local
- Aggregate model updates

### Libraries
- **PySyft** - Federated learning
- **Flower** - FL framework
- **NVIDIA FLARE** - NVIDIA's solution

---

## 9. AutoML

### Tools
- **AutoML** - Google's solution
- **Auto-sklearn** - AutoML for sklearn
- **TPOT** - Genetic programming
- **H2O AutoML** - Enterprise AutoML

---

## 10. Reinforcement Learning

### Libraries
| Library | Description |
|---------|-------------|
| Stable Baselines3 | Stable RL implementations |
| RLlib | Scalable RL |
| OpenAI Gym | Environment interface |
| Unity ML-Agents | Game RL |

### Example
```python
from stable_baselines3 import PPO
from gymnasium import make

env = make("CartPole-v1")
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
model.save("ppo_cartpole")
```

---

## 11. NLP Trends

### Architectures
- Transformers (BERT, GPT)
- Attention mechanisms
- Tokenizers (BPE, WordPiece)

### Tasks
- Text classification
- Named entity recognition
- Question answering
- Text summarization
- Machine translation

---

## 12. Data Science Stack

### Key Libraries
```python
import numpy as np      # Numerical computing
import pandas as pd     # Data manipulation
import matplotlib.pyplot as plt  # Visualization
import seaborn as sns   # Statistical graphics
from sklearn import *   # ML algorithms
```

### Pandas Operations
```python
# Read data
df = pd.read_csv('data.csv')

# Filter
df[df['age'] > 30]

# Group
df.groupby('category').mean()

# Transform
df['log_value'] = np.log(df['value'])
```

---

## 13. Resources

### Documentation
- tensorflow.org
- pytorch.org
- scikit-learn.org
- huggingface.co/docs

### Datasets
- Kaggle
- Hugging Face Datasets
- UCI Machine Learning Repository

---

*Last Updated: 2026-03-14*
