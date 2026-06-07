import Header from './components/header'; // Importing the Header component
import { Routes, Route } from 'react-router-dom'; // Routes acts as a container, Route defines individual paths
import Login from './pages/Login'; // Importing the Login page component
import Signup from './pages/Signup'; // Importing the Signup page component
import Chat from './pages/Chat'; // Importing the Chat page component
import Notfound from './pages/Notfound'; // Importing the NotFound page component (handles undefined routes)
import { useAuth } from './context/AuthContext'; // Importing authentication context for user authentication status

function App() {
  console.log(useAuth()?.isLoggedIn); // Logging authentication status (useful for debugging)

  return (
    <main>
      <Header /> {/* Displaying the Header component */}
      <Routes>
        <Route path="/" element={<Chat />} /> {/* Default route (redirects to Chat) */}
        <Route path="/login" element={<Login />} /> {/* Login page route */}
        <Route path="/signup" element={<Signup />} /> {/* Signup page route */}
        <Route path="/chat" element={<Chat />} /> {/* Chat page route */}
        <Route path="*" element={<Notfound />} /> {/* Catch-all route for undefined paths */}
      </Routes>
    </main>
  ); 
}

export default App; // Exporting App component as default
