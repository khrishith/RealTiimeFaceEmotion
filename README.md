# Real-Time Facial Emotion Recognition with Visual Filters and Gamification Using CNN and Flask

This project showcases a real-time Facial Emotion Recognition (FER) system built using a CNN model, Flask backend, and OpenCV video processing pipeline. It features dynamic visual filters, real-time emotion analytics, and an interactive gamification engine that challenges users to match specific emotions within a 30-second window.

> **Note:** Due to GitHub file-size limitations, the dataset, virtual environment (`emotion_env`), and model file (`emotion_cnn_model.h5`) are not uploaded.

---

## 🎯 Key Features

### 🔹 Real-Time Emotion Prediction
- Live webcam-based processing  
- Haar Cascade face detection  
- CNN model trained on 48×48 grayscale dataset  
- Predicts: **angry, disgust, fear, happy, neutral, sad, surprise**

### 🔹 Advanced Visual Filters
Live filters include:
- Sketch  
- Emboss  
- Sepia  
- Gray  
- Pencil  
- Cartoon / Cartoon-2  
- Blur  
- Vintage  
- Lomo  
- Hot / Cold / Winter / Spring  
- Solarize, Posterize  
…and more creative effects.

### 🔹 Real-Time Emotion Analytics
- Tracks last 100 predicted emotions  
- Visualized through Chart.js bar chart  
- Auto-refreshing every second  

### 🔹 Gamification System
- Random emotion target assignment  
- 30-second timer  
- Score increments when dominant emotion matches the target  
- Simple yet engaging game flow  

---



