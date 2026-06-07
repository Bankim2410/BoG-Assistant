import { Avatar, Box, Typography, Button, IconButton } from '@mui/material';
import { useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { red } from '@mui/material/colors';
import Chatitem from '../components/chat/Chatitem';
import { IoMdSend } from 'react-icons/io';
import toast from 'react-hot-toast';
import { CircularProgress } from '@mui/material';

type Message = {
    role: "user" | "assistant";
    content: string;
};

const Chat = () => {
    const inputRef = useRef<HTMLInputElement | null>(null);
    const auth = useAuth();
    const [chatMessages, setChatMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async () => {
        const content = inputRef.current?.value as string;

        if (!content.trim()) {
            toast.error("Message cannot be empty");
            return;
        }

        if (inputRef.current) {
            inputRef.current.value = "";
        }

        const newMessage: Message = { role: "user", content };
        setChatMessages((prev) => [...prev, newMessage]);
        setIsLoading(true);

        try {
            const response = await fetch("http://localhost:8000/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"  // Add this header
                },
                body: JSON.stringify({
                    query: content,
                    top_k: 200
                }),
                mode: "cors"  // Explicitly enable CORS
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const data = await response.json();
            console.log(data)
            setChatMessages(prev => [...prev, { role: "assistant", content: data.response }]);
        } catch (error) {
            console.error("Error:", error);
            toast.error("Failed to get response");
            setChatMessages(prev => [...prev, {
                role: "assistant",
                content: "Sorry, I encountered an error. Please try again."
            }]);
        } finally {
            setIsLoading(false);
        }
    };






    const handleDeleteChats = () => {
        setChatMessages([]);
        toast.success("Chat history cleared");
    };

    return (
        <Box sx={{ display: 'flex', flex: 1, width: '100%', height: '120%', mt: 3, gap: 3 }}>
            {/* Sidebar */}
            <Box sx={{ display: { md: 'flex', xs: 'none', sm: 'none' }, flex: 0.2, flexDirection: 'column' }}>
                <Box sx={{
                    display: 'flex',
                    width: '100%',
                    height: '60vh',
                    bgcolor: "rgb(244, 247, 249)",
                    borderRadius: 5,
                    flexDirection: 'column',
                    mx: 3
                }}>
                    <Avatar
                        sx={{
                            mx: 'auto',
                            my: 2,
                            width: 60,
                            height: 60,
                            bgcolor: 'primary.light',
                            color: 'common.white',
                            fontWeight: 700,
                            border: '2px solid',
                            borderColor: 'primary.main',
                            '& img': {
                                width: '80%',
                                height: '80%',
                                objectFit: 'contain'
                            }
                        }}
                    >
                        <img
                            src="mnnit.png"
                            alt="MNNIT Logo"
                            style={{
                                width: '100%',
                                height: '100%',
                                objectFit: 'contain'
                            }}
                        />
                    </Avatar>
                    <Typography variant="h6" sx={{ mx: 'auto', fontFamily: 'work sans', color: "black" }}>
                        I am MNNIT Chatbot
                    </Typography>

                    <Typography sx={{ mx: 'auto', fontFamily: 'work sans', color: "black", my: 4, px: 3 }}>
                        This official chatbot provides authenticated information about MNNIT's past Board of Governors meetings, including agendas, resolutions, and attendance records. For optimal results, please phrase questions clearly regarding specific meetings or topics.
                    </Typography>
                    <Button
                        onClick={handleDeleteChats}
                        sx={{
                            width: '200px',
                            my: 'auto',
                            color: 'white',
                            fontWeight: '700',
                            borderRadius: 3,
                            mx: 'auto',
                            bgcolor: red[300],
                            ":hover": { bgcolor: red[400] }
                        }}>
                        Clear Conversation
                    </Button>
                </Box>
            </Box>

            {/* Main Chat Window */}
            <Box sx={{ display: 'flex', flex: { md: 0.8, xs: 1, sm: 1 }, flexDirection: 'column', px: 3 }}>
                <Typography sx={{
                    textAlign: 'center',
                    fontSize: '40px',
                    color: 'rgb(65, 134, 161)',
                    mb: 2,
                    mx: 'auto',
                    fontWeight: 600
                }}>
                    MNNIT - Prayagraj
                </Typography>

                {/* Chat messages */}
                <Box sx={{
                    width: "100%",
                    height: "60vh",
                    borderRadius: 3,
                    mx: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                    overflowY: 'auto',
                    overflowX: 'hidden'
                }}>
                    {chatMessages.map((chat, index) => (
                        <Chatitem content={chat.content} role={chat.role} key={index} />
                    ))}

                    {/* Add this loader */}
                    {isLoading && (
                        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                            <CircularProgress color="primary" />
                        </Box>
                    )}
                </Box>


                {/* Input area */}
                <Box sx={{
                    width: "100%",
                    borderRadius: 8,
                    backgroundColor: "rgb(251, 252, 252)",
                    display: 'flex',
                    marginBottom: '0',
                    border: '1px solid #ccc'
                }}>
                    <input
                        ref={inputRef}
                        type="text"
                        onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                        style={{
                            width: "100%",
                            backgroundColor: "transparent",
                            padding: '30px',
                            borderRadius: 8,
                            border: "none",
                            outline: "none",
                            color: "black",
                            fontSize: '20px'
                        }}
                    />
                    <IconButton
                        onClick={handleSubmit}
                        disabled={isLoading}
                        sx={{ ml: "auto", color: "rgb(65, 134, 161)", mx: 1 }}
                    >
                        <IoMdSend />
                    </IconButton>
                </Box>
            </Box>
        </Box>
    );
};

export default Chat;