import { useState, useContext, createContext } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

function safeParseJSON(key) {
  try {
    const val = localStorage.getItem(key);
    return val ? JSON.parse(val) : null;
  } catch {
    localStorage.removeItem(key);
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => safeParseJSON('user'));
  const [token, setToken] = useState(() => localStorage.getItem('token') || null);

  const login = async (correo, password) => {
    const response = await api.post('/auth/login', { correo, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Ignorar errores al cerrar sesion
    }
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
