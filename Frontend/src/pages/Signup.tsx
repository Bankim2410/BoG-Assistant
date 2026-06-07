import { Box, Typography, Button } from '@mui/material'; // MUI components for styling
import React from 'react';
import CustomizedInput from '../components/shared/CustomizedInput'; // Custom input field component
import { IoIosLogIn } from "react-icons/io"; // Login icon from react-icons
import { toast } from 'react-hot-toast'; // Toast notifications for user feedback
import { useAuth } from '../context/AuthContext'; // Authentication context
import { Link } from 'react-router-dom';


const Signup = () => {
    const auth = useAuth(); // Access authentication functions from context

    // Function to handle signup form submission
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault(); // Prevent page reload
        const formData = new FormData(e.currentTarget); // Extract form data

        const name = formData.get('name') as string; // Get name input
        const email = formData.get('email') as string; // Get email input
        const password = formData.get('password') as string; // Get password input

        try {
            toast.loading("Signing up", { id: "signup" }); // Show loading toast
            await auth?.signup(name, email, password); // Call signup function from AuthContext
            toast.success("Signed Up", { id: "signup" }); // Show success message
        } catch (error) {
            console.log(error);
            toast.error("Signup Failed", { id: "signup" }); // Show error message
        }

        console.log(email, password); // Debugging log
    };

    return (
        <Box width={"100%"} height={"100%"} display="flex" flex={1}>
            {/* Left Section - MNNIT Logo (Visible on medium and larger screens) */}
            <Box padding={8} mt={1} display={{ md: "flex", sm: "none", xs: "none" }}>
                <img 
                    src="MNNIT_Logo.png" 
                    alt="MNNIT" 
                    style={{ width: '400px' }} 
                />
            </Box>

            {/* Right Section - Signup Form */}
            <Box 
                display={'flex'} 
                flex={{ xs: 1, md: 0.5 }} 
                justifyContent={'center'} 
                alignItems={"center"} 
                padding={2} 
                ml={"auto"} 
                mt={8}
            >
                            <form 
                onSubmit={handleSubmit} 
                style={{
                    margin: 'auto',
                    padding: '40px',
                    borderRadius: '12px',
                    boxShadow: "10px 10px 20px #000",
                    width: '100%',
                    maxWidth: '450px'
                }}
                >
                <Box sx={{ 
                    display: 'flex', 
                    flexDirection: 'column',
                    gap: 1,
                    alignItems: 'center'
                }}>
                    {/* Signup Header */}
                    <Typography 
                    variant="h4"
                    sx={{
                        fontWeight: 700,
                        color: 'primary.main',
                        mb: 1,
                        background: 'linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent'
                    }}
                    >
                    Create Account
                    </Typography>

                    {/* Input Fields */}
                    <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <CustomizedInput 
                        type="text" 
                        name="name" 
                        label="Full Name"
                
                    />
                    <CustomizedInput 
                        type="email" 
                        name="email" 
                        label="Email Address"

                    />
                    <CustomizedInput 
                        type="password" 
                        name="password" 
                        label="Password" 

                    />
                    </Box>

                    {/* Signup Button */}
                    <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    size="large"
                    endIcon={<IoIosLogIn />}
                    sx={{
                        mt: 2,
                        py: 1.5,
                        borderRadius: '8px',
                        fontWeight: 600,
                        fontSize: '1rem',
                        background: 'linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%)',
                        '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 12px rgba(58, 123, 213, 0.3)'
                        },
                        transition: 'all 0.2s ease'
                    }}
                    >
                    Create Account
                    </Button>

                    {/* Login Link */}
                    <Typography
                    variant="body1"
                    sx={{
                        mt: 2,
                        color: 'text.secondary',
                        '& a': {
                        color: 'secondary.main',
                        fontWeight: 600,
                        textDecoration: 'none',
                        ml: 1,
                        '&:hover': {
                            textDecoration: 'underline',
                            textUnderlineOffset: '3px'
                        }
                        },
                        transition: 'all 0.2s ease'
                    }}
                    >
                    Already have an account?
                    <Link to="/login">Login</Link>
                    </Typography>
                </Box>
                </form>
            </Box>
        </Box>
    );
};

export default Signup;
