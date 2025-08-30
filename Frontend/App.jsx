import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Menu from "./pages/Menu";
import OrderComplete from "./pages/OrderComplete";
import Admin from "./pages/Admin";
import Display from "./pages/Display";
import Login from "./pages/Login";
import { CartProvider } from "./context/CartContext";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import NotFound from "./pages/NotFound";
import Header from "./components/Header";

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <Header />
          <Routes>
            {/* Любой авторизованный пользователь может заходить */}
            <Route
              path="/menu"
              element={
                <ProtectedRoute requireRole={[0, 1, 2]}>
                  <Menu />
                </ProtectedRoute>
              }
            />

            <Route path="/order-complete" element={<OrderComplete />} />
            <Route path="/login" element={<Login />} />

            {/* Только админ */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requireRole={[0]}>
                  <Admin />
                </ProtectedRoute>
              }
            />

            {/* TV: роль 2 (TV) и админ */}
            <Route
              path="/display"
              element={
                <ProtectedRoute requireRole={[0, 2]}>
                  <Display />
                </ProtectedRoute>
              }
            />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}
