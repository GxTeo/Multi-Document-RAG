import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';


function Logout() {
    const navigate = useNavigate();
    const { logout } = useAuth();

  
    const handleLogout = () => {
      const isConfirmed = window.confirm('Are you sure you want to logout?');
      if (isConfirmed) {
        logout(); // Clear the token from context
        navigate('/');
      }
    };
    return <button onClick={handleLogout}>Logout</button>;
  }
  
  export default Logout;