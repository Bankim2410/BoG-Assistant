import { Typography, Box } from '@mui/material';
import { Link } from 'react-router-dom';

const Logo = () => {
  return (
    <Box 
      sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 'auto' }}
    >
      {/* Logo Image wrapped in Link */}
      <Link to="/" aria-label="MNNIT Home">
        <img 
          src="MNNIT_Logo.png" 
          alt="MNNIT Official Logo" 
          style={{ width: '40px', height: '40px' }} 
          className="image-inverted"
        />
      </Link> 

      {/* Logo Text with better spacing & alignment */}
      <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
        <Typography
          sx={{
            display: { md: 'block', sm: 'none', xs: 'none' },
            fontWeight: 800,
            fontSize: '1.5rem',
            color: 'primary.main',
            textShadow: 'linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%)'
          }}
        >
          MNNIT Chatbot
        </Typography>
      </Link>
    </Box>
  );
};

export default Logo;
