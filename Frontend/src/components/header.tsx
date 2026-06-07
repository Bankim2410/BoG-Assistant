
import { AppBar, Toolbar, Box } from '@mui/material';
import Logo from './shared/Logo';
import { useAuth } from '../context/AuthContext';
import NavigationLink from './shared/NavigationLink';

const Header = () => {
    const auth = useAuth(); // Access authentication context

    return ( 
        <AppBar 
            sx={{ bgcolor: "transparent", position: "static", boxShadow: "none" }}>
            <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}> 
                {/* Logo Component */}
                <Logo />  

                {/* Navigation Links */}
                <Box sx={{ display: "flex", gap: 2 }}> 
                    {auth?.isLoggedIn ? (
                        <>
                            <NavigationLink to={'/chat'} bg={'#00fffc'} text={'Go to Chat'} textcolor={'black'} />
                            <NavigationLink to={'/'} bg={'#51538f'} text={'Logout'} textcolor={'white'} onClick={() => auth.logout()} />
                        </>
                    ) : (
                        <>
                            <NavigationLink to={'/chat'} bg={'#51538f'} text={'Go to Chat'} textcolor={'white'} />
                            <NavigationLink to={'/login'} bg={'#51538f'} text={'Login'} textcolor={'white'} />
                        </>
                    )}
                </Box>     
            </Toolbar>
        </AppBar>
    );
}

export default Header;
