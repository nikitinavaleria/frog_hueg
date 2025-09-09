import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NotFound = () => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  switch (user.role_id) {
    case 0:
      return <Navigate to="/admin" replace />;
    case 1:
      return <Navigate to="/menu" replace />;
    case 2:
      return <Navigate to="/display" replace />;
    default:
      return <Navigate to="/login" replace />;
  }
};

export default NotFound;
