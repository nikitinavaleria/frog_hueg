import React, { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = (userData) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  const isAuthenticated = () => {
    return !!user;
  };

  const isAdmin = () => {
    return user?.role_id === 0;
  };

  const isTV = () => {
    return user?.role_id === 2;
  };

  return (
    <AuthContext.Provider
      value={{ user, login, logout, isAuthenticated, isAdmin, isTV }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
