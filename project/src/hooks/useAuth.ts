import { useState, useEffect } from 'react';
import { User, AuthState } from '../types';

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    currentUser: null,
  });

  useEffect(() => {
    const storedAuth = localStorage.getItem('authState');
    if (storedAuth) {
      setAuthState(JSON.parse(storedAuth));
    }
  }, []);

  const login = (username: string, password: string): boolean => {
    const users = JSON.parse(localStorage.getItem('users') || '[]') as User[];
    const user = users.find(u => u.username === username && u.password === password);
    
    if (user) {
      const newAuthState = { isAuthenticated: true, currentUser: username };
      setAuthState(newAuthState);
      localStorage.setItem('authState', JSON.stringify(newAuthState));
      return true;
    }
    return false;
  };

  const register = (username: string, password: string): boolean => {
    const users = JSON.parse(localStorage.getItem('users') || '[]') as User[];
    
    if (users.some(u => u.username === username)) {
      return false;
    }

    users.push({ username, password });
    localStorage.setItem('users', JSON.stringify(users));
    return true;
  };

  const logout = () => {
    setAuthState({ isAuthenticated: false, currentUser: null });
    localStorage.setItem('authState', JSON.stringify({ isAuthenticated: false, currentUser: null }));
  };

  const changePassword = (username: string, oldPassword: string, newPassword: string): boolean => {
    const users = JSON.parse(localStorage.getItem('users') || '[]') as User[];
    const userIndex = users.findIndex(u => u.username === username && u.password === oldPassword);
    
    if (userIndex === -1) {
      return false;
    }

    users[userIndex].password = newPassword;
    localStorage.setItem('users', JSON.stringify(users));
    return true;
  };

  return { ...authState, login, register, logout, changePassword };
}