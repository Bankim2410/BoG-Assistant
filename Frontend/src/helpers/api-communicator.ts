import axios from 'axios';

// Function to login user
export const loginUser = async (email: string, password: string) => {
    try {
        const { data } = await axios.post('/user/login', { email, password });
        return data;
    } catch (error) {
        throw new Error("Unable to login");
    }
};

// Function to signup user
export const signupUser = async (name: string, email: string, password: string) => {
    try {
        const { data } = await axios.post('/user/signup', { name, email, password });
        return data;
    } catch (error) {
        throw new Error("Unable to Signup");
    }
};

// Function to check authentication status
// export const checkAuthStatus = async () => {
//     try {
//         const { data } = await axios.get('/user/auth-status');
//         return data;
//     } catch (error) {
//         throw new Error("Unable to authenticate");
//     }
// };

// Function to send a chat message
export const sendChatRequest = async (message: string) => {
    try {
        // Call the FastAPI backend directly
        const { data } = await axios.post('http://localhost:8000/query', {
            query: message,
            top_k: 200
        });
        // Return in the format expected by the frontend
        return { chats: [{ role: "assistant", content: data.response }] };
    } catch (error) {
        console.error("Chat request error:", error);
        throw new Error("Unable to send chat");
    }
};

// export const sendChatRequest = async (message: string) => {
//     // Predefined responses
//     const predefinedResponses: { [key: string]: string } = {
//         "hello": "Hi there! How can I help you?",
//         "how are you": "I'm just a chatbot, but I'm here to assist you!",
//         "what is your name": "I'm MNNIT's chatbot, here to answer your queries.",
//         "bye": "Goodbye! Have a great day! 😊",
//     };

//     // Check if user message has a predefined response
//     const lowerCaseMessage = message.toLowerCase();
//     if (predefinedResponses[lowerCaseMessage]) {
//         return { role: "assistant", content: predefinedResponses[lowerCaseMessage] };
//     }

//     // Default response if no predefined response is found
//     return { role: "assistant", content: "I'm not sure how to respond to that. Can you rephrase?" };
// };




// Function to fetch user chats
export const getUserChats = async () => {
    try {
        const { data } = await axios.get('/chat/all-chats');
        return data;
    } catch (error) {
        throw new Error("Unable to fetch chats");
    }
};

// Function to delete user chats
export const deleteUserChats = async () => {
    try {
        const { data } = await axios.delete('/chat/delete');
        return data;
    } catch (error) {
        throw new Error("Unable to delete chats");
    }
};
