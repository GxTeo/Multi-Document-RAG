import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Logout() {
    const navigate = useNavigate();
  
    const handleLogout = () => {
      // Clear user session or token
      localStorage.removeItem('token');
      // Redirect to home page
      navigate('/');
    };
  
    return <button onClick={handleLogout}>Logout</button>;
  }
  
  export default Logout;