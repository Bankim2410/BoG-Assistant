import { StrictMode } from 'react'; // Enables strict mode for highlighting potential problems in the app
import { createRoot } from 'react-dom/client'; // New way to create the root in React 18+
import './index.css'; // Importing global CSS styles
import App from './App.tsx'; // Importing the main App component
import { createTheme, ThemeProvider } from '@mui/material'; // MUI theming for styling
import { BrowserRouter } from 'react-router-dom'; // Enables client-side routing
import { AuthProvider } from './context/AuthContext.tsx'; // Provides authentication context
import { Toaster } from 'react-hot-toast'; // Provides toast notifications
import axios from 'axios'; // Axios for making HTTP requests

// Setting up Axios default configurations
axios.defaults.baseURL = 'http://localhost:5000/api/v1'; // Base URL for all API requests
axios.defaults.withCredentials = true; // Enables sending cookies with cross-origin requests

// Creating a custom theme using MUI
const theme = createTheme({
  typography: {
    fontFamily: "Roboto Slab, serif", // Setting the global font family
    allVariants: { color: "white" }, // Making all text white by default
  }
});

// Rendering the application into the root div
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider> {/* Wrapping the entire app with authentication context */}
      <BrowserRouter> {/* Enables routing in the application */}
        <ThemeProvider theme={theme}> {/* Provides custom theme to the app */}
          <Toaster position='top-right' /> {/* Displays toast notifications in the top-right */}
          <App /> {/* Main application component */}
        </ThemeProvider>
      </BrowserRouter>
    </AuthProvider>
  </StrictMode>,
);
