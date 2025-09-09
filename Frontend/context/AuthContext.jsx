import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  const login = ({ access_token, role_id }) => {
    setToken(access_token);
    setUser({ role_id });
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = () => !!token;

  const isAdmin = () => user?.role_id === 0;
  const isTV = () => user?.role_id === 2;

  return (
    <AuthContext.Provider
      value={{ user, token, login, logout, isAuthenticated, isAdmin, isTV }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
