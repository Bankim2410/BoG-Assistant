import React from 'react';
import { TextField } from '@mui/material';

type Props = {
    name: string;
    type: string;
    label: string;
    value?: string;
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

const CustomizedInput: React.FC<Props> = ({ name, type, label, value, onChange }) => {
    return (
        <TextField 
            margin="normal"
            name={name}
            label={label}
            type={type}
            fullWidth // Makes input responsive
            value={value}
            onChange={onChange}
            InputLabelProps={{ style: { color: 'black' } }}
            InputProps={{ 
                sx: { 
                    borderRadius: 2, 
                    fontSize: 18, 
                    color: 'black', 
                    backgroundColor: 'rgba(255, 255, 255, 0.1)', 
                    paddingX: 1 
                } 
            }} 
        />
    );
};

export default CustomizedInput;
