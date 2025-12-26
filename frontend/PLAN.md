# Frontend Detailed Implementation Plan

## 1. Project Overview & Structure
This is the user interface for the platform. It handles user interactions, displays analysis results visually, and manages the session state.

### Directory Structure
```
frontend/
├── src/
│   ├── assets/              # Static images/icons
│   ├── components/          # Reusable UI components
│   │   ├── Navbar.jsx       # Top navigation
│   │   ├── Footer.jsx
│   │   ├── FileDropzone.jsx # Drag & Drop area
│   │   ├── ResultCard.jsx   # Display analysis result
│   │   └── ProtectedRoute.jsx
│   ├── context/             # Global State
│   │   └── AuthContext.jsx  # User login state
│   ├── pages/               # Full Page Views
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx    # User Hub
│   │   ├── Analyze.jsx      # Main Analysis Page
│   │   └── History.jsx      # Past Uploads
│   ├── services/
│   │   └── api.js           # Axios configuration
│   ├── App.jsx              # Routing Logic
│   └── main.jsx             # Entry Point
├── package.json
└── .env                     # API URL (VITE_API_URL)
```

---

## 2. Key Features & Visual Flow

### A. Authentication Flow
1.  **Login Page:** Simple form (Email/Password).
2.  **Logic:** On submit, call `POST /auth/token`.
3.  **Success:** Save JWT to `localStorage` and update `AuthContext`. Redirect to Dashboard.

### B. Analysis Flow (The Core Feature)
1.  **Analyze Page:**
    *   **Center:** A large dotted box (FileDropzone). Text: "Drag 'n' drop some files here, or click to select files".
    *   **Bottom:** Checkbox "I consent to saving this image for research."
2.  **Upload Action:**
    *   User drops an image.
    *   Frontend shows a "Loading..." spinner or progress bar.
    *   Request sent to `POST /documents/analyze` with `FormData`.
3.  **Result Display:**
    *   Hide dropzone, show **ResultCard**.
    *   **Left:** The image user uploaded.
    *   **Right:**
        *   **Prediction:** "FAKE" (Red) or "REAL" (Green).
        *   **Confidence:** A gauge chart showing 98%.
        *   **Details:** "Model detected inconsistencies in texture."

---

## 3. Component Implementation Examples

### API Service (`src/services/api.js`)
Centralized place for all backend calls. Automatically attaches the token.

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to attach the Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
```

### Analysis Page Logic (`src/pages/Analyze.jsx`)

```jsx
import React, { useState } from 'react';
import api from '../services/api';
import { FileDropzone } from '../components/FileDropzone';

export const Analyze = () => {
  const [file, setFile] = useState(null);
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!file) return;
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('consent', consent); // 'true' or 'false'

    try {
      const response = await api.post('/documents/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (error) {
      console.error("Analysis failed", error);
      alert("Failed to analyze document");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1>Document Analysis</h1>
      
      {!result ? (
        <div className="upload-section">
          <FileDropzone onFileSelect={setFile} />
          
          <div className="mt-4">
            <label>
              <input 
                type="checkbox" 
                checked={consent} 
                onChange={(e) => setConsent(e.target.checked)} 
              />
              I agree to store this image for research purposes.
            </label>
          </div>
          
          <button 
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="bg-blue-500 text-white px-4 py-2 rounded mt-2"
          >
            {loading ? "Analyzing..." : "Analyze Document"}
          </button>
        </div>
      ) : (
        <div className="result-section">
          <h2>Result: {result.prediction}</h2>
          <p>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
          <button onClick={() => setResult(null)}>Analyze Another</button>
        </div>
      )}
    </div>
  );
};
```

---

## 4. Development Roadmap

### Phase 1: Setup & Routing (Day 1)
1.  **Install:** `npm install` (axios, react-router-dom, mui, etc.).
2.  **Clean Up:** Remove default Vite boilerplate.
3.  **Router:** Setup `App.jsx` with `<Routes>` for Login, Home, Analyze.
4.  **UI Framework:** Configure Material UI or Tailwind.

### Phase 2: Auth Integration (Day 2)
1.  **Auth Context:** Create the context to hold `user` state.
2.  **Login Page:** Build the form and connect to `api.post('/auth/token')`.
3.  **Protected Routes:** Create a wrapper that redirects to `/login` if no user is found.

### Phase 3: Analysis Feature (Day 3-4)
1.  **Dropzone:** Implement drag-and-drop file selection.
2.  **API Connection:** Connect the `Analyze` page to the backend.
3.  **Visualization:** Design a nice card to show the results (Green/Red colors based on "Real"/"Fake").

### Phase 4: History & Polish (Day 5)
1.  **History Page:** Fetch list of documents from `/documents/history`.
2.  **Display:** Show a grid of past uploads with small thumbnails (from Cloudinary).

