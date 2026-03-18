# Frontend — Identity Document Fraud Detection

React 18 single-page application for uploading and analyzing identity documents using deep learning models.

## Tech Stack

| Tool | Purpose |
|------|---------|
| React 18 + Vite | UI framework and build tool |
| React Router DOM v6 | Client-side routing |
| Material-UI (MUI) v5 | Component library and theming |
| Recharts | Charts in admin dashboard |
| Emotion | CSS-in-JS styling |

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── context/
│   │   ├── AuthContext.jsx       # JWT auth state + localStorage persistence
│   │   ├── ThemeContext.jsx      # Dark/light mode toggle
│   │   ├── ChatContext.jsx       # Real-time chat via WebSocket
│   │   └── ToastContext.jsx      # Global toast notifications
│   ├── lib/
│   │   └── api.js                # All API calls (fetch wrapper, no axios)
│   ├── components/
│   │   ├── Navbar.jsx            # Top navigation bar
│   │   ├── ChatWidget.jsx        # Floating live-support chat window
│   │   └── ScanDemo.jsx          # Interactive ML pipeline demo component
│   ├── pages/
│   │   ├── LandingPage.jsx       # Public home page with features + demo
│   │   ├── Login.jsx             # Email/password + Google OAuth login
│   │   ├── Register.jsx          # Registration with password strength meter
│   │   ├── AuthCallback.jsx      # OAuth redirect handler
│   │   ├── VerifyEmail.jsx       # Email verification via token
│   │   ├── CheckEmail.jsx        # Post-registration confirmation screen
│   │   ├── ForgotPassword.jsx    # Request password reset
│   │   ├── ResetPassword.jsx     # Set new password via reset token
│   │   ├── ScanPage.jsx          # Main scan interface (upload + results + PDF)
│   │   ├── UserProfile.jsx       # Account management
│   │   └── AdminDashboard.jsx    # Admin panel (users, scans, stats)
│   ├── App.jsx                   # Routes with PrivateRoute + AdminRoute guards
│   ├── main.jsx                  # Entry point — wraps app in all context providers
│   └── config.js                 # API base URL from env
├── index.html
├── vite.config.js
├── package.json
├── .env.example
└── Dockerfile
```

## Features

- **Document Scanning** — drag-and-drop image upload, choose between ViT-Tiny and ResNet-18 models, visualize the 5-step ML pipeline, view confidence scores per document class, download a PDF report
- **Authentication** — JWT login/register, Google OAuth, email verification, password reset
- **Real-time Chat** — WebSocket-based live support for users; admin polling for session management
- **Admin Dashboard** — user list, scan history, activity charts, role management
- **Theming** — dark/light mode persisted in localStorage
- **Responsive** — mobile-friendly navigation

## Getting Started

### Prerequisites

- Node.js 18+
- Running backend (see `../backend/README.md`)

### Install and Run

```bash
cd frontend
npm install
cp .env.example .env     # then fill in VITE_API_URL
npm run dev              # starts dev server on http://localhost:5173
```

### Available Scripts

```bash
npm run dev      # development server with hot reload
npm run build    # production build → dist/
npm run lint     # ESLint check
npm run preview  # preview the production build locally
```

### Environment Variables

Copy `.env.example` to `.env` and set:

```env
VITE_API_URL=http://localhost:8000
```

## Docker

```bash
docker build -t fraud-detection-frontend .
docker run -p 5173:5173 fraud-detection-frontend
```

## Routes

| Path | Access | Description |
|------|--------|-------------|
| `/` | Public | Landing page |
| `/login` | Public | Sign in |
| `/register` | Public | Create account |
| `/verify-email` | Public | Email confirmation |
| `/forgot-password` | Public | Password reset request |
| `/reset-password` | Public | Set new password |
| `/scan` | Auth required | Upload and analyze documents |
| `/profile` | Auth required | Account settings |
| `/admin` | Admin only | Admin dashboard |

## API Integration

All backend calls go through `src/lib/api.js`. The base URL is read from `VITE_API_URL`.
JWT tokens are stored in `localStorage` and automatically attached to every request via the `Authorization: Bearer` header.

## WebSocket (Chat)

- User connection: `ws://<backend>/ws/user/<jwt_token>`
- Admin connection: `ws://<backend>/ws/admin/<jwt_token>`

The `ChatContext` manages the WebSocket lifecycle; `ChatWidget` renders the floating UI.
