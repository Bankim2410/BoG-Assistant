import { Box, Avatar, Typography } from '@mui/material';
import React from 'react';
import { useAuth } from '../../context/AuthContext';

const Chatitem = ({ content, role }: { content: string; role: 'user' | 'assistant' }) => {
    const auth = useAuth();

    const prettifyText = (text: string): string => {
        let formatted = text.replace(/\n\s*\n/g, '</p><p>'); // Double newlines = new paragraph
        formatted = formatted.replace(/\n/g, '<br/>');        // Single newline = line break
        formatted = formatted.replace(/(?:^|\n)- (.*?)(?=\n|$)/g, '<li>$1</li>');
      
        if (formatted.includes('<li>')) {
          formatted = `<ul>${formatted}</ul>`;
        }
      
        return `<p>${formatted}</p>`;
      };
      

    return role === 'assistant' ? (
        // Assistant's message (icon on left)
        <Box className="bot-message"
        sx={{ display: 'flex', alignItems: 'center', gap: 2, my: 1 }}>
            <Avatar sx={{ width: 30, height: 30 }}>
                <img src="mnnit.png" width="30px" alt="AI" />
            </Avatar>
            <Box
                sx={{
                    maxWidth: '70%',
                    padding: '10px 15px',
                    borderRadius: '15px',
                    backgroundColor: '#f1f0f0', // Light gray background
                    borderTopLeftRadius: '0px',
                    boxShadow: '0px 1px 3px rgba(0,0,0,0.2)',
                }}
            >
               <Typography
                  fontSize="16px"
                    color="black"
                    dangerouslySetInnerHTML={{ __html: prettifyText(content) }}
/>

            </Box>
        </Box>
    ) : (
        // User's message (icon on right)
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 2, my: 1 }}>
            <Box
                sx={{
                    maxWidth: '70%',
                    padding: '10px 15px',
                    borderRadius: '15px',
                    backgroundColor: 'white', // White background for user
                    borderTopRightRadius: '0px',
                    boxShadow: '0px 1px 3px rgba(0,0,0,0.2)',
                }}
            >
                <Typography fontSize="16px" color="black">{content}</Typography> {/* Set text color to black */}
            </Box>
            <Avatar sx={{ width: 30, height: 30, bgcolor: 'black', color: 'white' }}>
            {auth?.User?.name[0] || 'U'}  {/* Safely extracts first letter or defaults to 'U' */}
            </Avatar>
        </Box>
    );
};

export default Chatitem;