// pages/Login.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { login as apiLogin } from "../api";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await apiLogin({ username, password });

      // Сохраняем токен и роль в контекст
      login({
        access_token: response.data.access_token,
        role_id: response.data.role_id,
      });

      // Берём роль из ответа
      const userRole = response.data.role_id;

      // Навигация в зависимости от роли
      switch (userRole) {
        case 0:
          navigate("/admin");
          break;
        case 2:
          navigate("/display");
          break;
        default:
          navigate("/menu");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError(err.response?.data?.detail || "Ошибка при входе");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[--main-color]">
      <div className="bg-[--accent-color] p-8 rounded-3xl shadow-lg w-96">
        <h2 className="text-2xl font-bold mb-6 text-center">
          Необходима авторизация
        </h2>
        {error && (
          <div className="mb-4 p-2 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-lg mb-2">
              Логин:
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-2 rounded-md border border-[--dark-color] focus:outline-none focus:border-2"
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-lg mb-2">
              Пароль:
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 rounded-md border border-[--dark-color] focus:outline-none focus:border-2"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-[#4ade80] text-white py-2 px-4 rounded-md hover:bg-[#22c55e] transition-colors">
            Войти
          </button>
        </form>
      </div>
    </div>
  );
}
