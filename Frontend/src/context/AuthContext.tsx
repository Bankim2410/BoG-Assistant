import { createContext, ReactNode, useContext, useEffect, useState } from 'react';
import { loginUser, signupUser, checkAuthStatus } from '../helpers/api-communicator';
import axios from 'axios';

// Define User type
type User = {
    name: string;
    email: string;
};

// Define AuthContext type
type UserAuth = {
    isLoggedIn: boolean;
    User: User | null;
    login: (email: string, password: string) => Promise<void>;
    signup: (name: string, email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
};

// Create authentication context
const AuthContext = createContext<UserAuth | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    // State to store user details
    const [User, setUser] = useState<User | null>(null);
    // State to track login status
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // Check user authentication status on component mount
    // useEffect(() => {
    //     const fetchAuthStatus = async () => {
    //         try {
    //             const data = await checkAuthStatus();
    //             if (data?.user) {
    //                 // If user is authenticated, set the user state
    //                 setUser({ email: data.user.email, name: data.user.name });
    //                 setIsLoggedIn(true);
    //             }
    //         } catch (error) {
    //             console.log("Auth check failed:", error);
    //         }
    //     };
    //     fetchAuthStatus();
    // }, []);

    // Function to handle user login
    const login = async (email: string, password: string) => {
        try {
            // Call the login API
            const data = await loginUser(email, password);
            if (data) {
                // If login is successful, update user state
                setUser({ email: data.email, name: data.name });
                setIsLoggedIn(true);
            }
        } catch (error) {
            console.error("Login failed:", error);
            throw new Error("Invalid credentials");
        }
    };

    // Function to handle user signup
    const signup = async (name: string, email: string, password: string) => {
        try {
            // Call the signup API
            const data = await signupUser(name, email, password);
            if (data) {
                // If signup is successful, update user state
                setUser({ email: data.email, name: data.name });
                setIsLoggedIn(true);
            }
        } catch (error) {
            console.error("Signup failed:", error);
            throw new Error("Signup failed");
        }
    };

    // Function to handle user logout
    const logout = async () => {
        try {
            // Call the logout API to clear session
            await axios.post('/user/logout');
            // Reset user state
            setUser(null);
            setIsLoggedIn(false);
        } catch (error) {
            console.error("Logout failed:", error);
            throw new Error("Logout failed");
        }
    };

    // Provide authentication values to child components
    const value = {
        User,
        isLoggedIn,
        login,
        signup,
        logout,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to access authentication context
export const useAuth = () => useContext(AuthContext);
