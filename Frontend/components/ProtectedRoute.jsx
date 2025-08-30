// components/ProtectedRoute.js
import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ProtectedRoute = ({ children, requireRole }) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated()) return <Navigate to="/login" replace />;

  if (requireRole !== undefined) {
    if (Array.isArray(requireRole)) {
      if (!requireRole.includes(user?.role_id))
        return <Navigate to="/login" replace />;
    } else {
      if (user?.role_id !== requireRole)
        return <Navigate to="/login" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
