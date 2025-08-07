# Authentication UI Documentation

## Overview

The Elenchus AI frontend now includes a complete authentication UI that integrates with the backend authentication system. **Authentication is only required when accessing protected routes** (`/app`, `/research`, `/dashboard`, `/settings`, `/workflows`), while the landing page remains publicly accessible.

## Features

### 🎨 **Authentication Modal**
- Modern, responsive modal design matching the provided design mockup
- Tab-based interface for Sign Up / Sign In
- Dark theme with glassmorphic effects
- Smooth transitions and animations
- Form validation with error messages
- Password visibility toggle

### 🔐 **Authentication Flow**

1. **Auto-Display**: Modal appears automatically for unauthenticated users
2. **Sign Up**: 
   - First name (optional)
   - Last name (optional)  
   - Email (required)
   - Password (min 8 characters)
3. **Sign In**:
   - Email
   - Password
4. **Persistent Session**: Uses JWT tokens stored in localStorage
5. **User Profile**: Displays user initials in avatar after login

### 🎯 **Integration Points**

#### Components
- **AuthModal** (`/components/AuthModal.tsx`): Main authentication modal component
- **AuthProtection** (`/components/AuthProtection.tsx`): Wrapper component for protected routes
- **Zustand Store** (`/store/useStore.ts`): Global auth state management
- **Protected Routes**: All routes under `/app` structure use AuthProtection wrapper

#### State Management
```typescript
// Auth state in Zustand store
{
  user: User | null,
  accessToken: string | null,
  isAuthenticated: boolean,
  setAuth: (user, token) => void,
  logout: () => void,
  checkAuth: () => void
}
```

#### API Endpoints Used
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### 📱 **Responsive Design**

The authentication modal is fully responsive:
- **Desktop**: Centered modal with optimal width (max-w-md)
- **Tablet**: Adjusted padding and spacing
- **Mobile**: Full-width modal with proper touch targets

### 🎨 **Design Features**

- **Dark Theme**: Matches the app's dark aesthetic
- **Glassmorphism**: Backdrop blur and transparency effects
- **Form States**: Loading, error, and success states
- **Smooth Animations**: Fade-in effects and transitions
- **Accessibility**: Proper focus management and keyboard navigation

### 🔒 **Security Features**

- Password field with visibility toggle
- Minimum password length validation (8 characters)
- Email format validation
- JWT token management
- Automatic token removal on logout
- Protected routes that require authentication

### 🚀 **User Experience**

1. **Landing Page**: Publicly accessible without authentication
2. **Protected Routes**: Auth modal appears when accessing `/app`, `/research`, etc.
3. **Registration**: Quick sign-up with optional name fields  
4. **Login**: Simple email/password login
5. **Session Persistence**: Stay logged in across page refreshes and route navigation
6. **Profile Menu**: Access user settings and logout
7. **Logout**: Clear session and return to auth modal when accessing protected routes

## Usage

### Testing the Authentication

1. **Visit the app**: http://localhost:3001/app
2. **Sign Up**: Create a new account with email/password
3. **Sign In**: Login with existing credentials
4. **Profile**: Click avatar to see user menu
5. **Logout**: Sign out from the dropdown menu

### Development

To modify the authentication UI:

```typescript
// Update modal appearance
// File: /components/AuthModal.tsx

// Modify auth state management
// File: /store/useStore.ts

// Change integration behavior
// File: /app/app/page.tsx
```

## Screenshots

The authentication modal follows this design pattern:
- Clean, modern interface
- Dark theme with subtle gradients
- Clear CTAs (Call-to-Action buttons)
- Minimal form fields
- Social login buttons (prepared for future implementation)

## Future Enhancements

- [ ] Email verification flow
- [ ] "Remember me" checkbox
- [ ] Social authentication (Google, Apple)
- [ ] Two-factor authentication
- [ ] Password strength indicator
- [ ] Terms of Service links
- [ ] Forgot password flow in UI

## Testing

Run the automated test script:
```bash
./test-auth-flow.sh
```

This tests:
- User registration
- User login
- Protected endpoint access
- Password reset
- Frontend accessibility
- Full authentication flow