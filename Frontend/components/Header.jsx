import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Определяем, какие ссылки показывать в зависимости от роли пользователя
  const getNavLinks = () => {
    if (!user) return [];

    const links = [];

    // Общие ссылки для всех авторизованных пользователей
    if (user.role_id !== 1 && user.role_id !== 2) {
      links.push({ to: "/menu", text: "Меню" });
    }

    // Ссылки для админа (role_id = 0)
    if (user.role_id === 0) {
      links.push({ to: "/admin", text: "Админ панель" });
      links.push({ to: "/display", text: "Дисплей" });
    }

    return links;
  };

  if (!user) return null;

  // Определяем цвет хедера в зависимости от роли пользователя
  const getHeaderStyles = () => {
    if (!user) return "bg-[--main-color] text-[--dark-color]";

    switch (user.role_id) {
      case 0: // Админ
        return "bg-[--dark-color] text-white";
      case 1: // Обычный пользователь
        return "bg-[--main-color] text-[--dark-color]";
      case 2: // TV
        return "bg-[--main-color] text-[--secondary-color]";
      default:
        return "bg-[--main-color] text-[--dark-color]";
    }
  };

  return (
    <>
      {user.role_id !== 2 && ( // Прячем хедер для обычных пользователей
        <header className={`${getHeaderStyles()} py-4`}>
          <div className="container mx-auto flex justify-between items-center">
            <div className="flex items-center">
              <Link
                to={user.role_id === 0 ? "/admin" : "/menu"}
                className={`text-2xl font-semibold hover:opacity-80 ${
                  user.role_id === 0
                    ? "text-white"
                    : user.role_id === 2
                    ? "text-[--secondary-color]"
                    : "text-[--dark-color]"
                }`}>
                Жаб Кафе
              </Link>
            </div>

            <nav className="flex items-center font-semibold space-x-6">
              {getNavLinks().map((link, index) => (
                <Link
                  key={index}
                  to={link.to}
                  className={`p-2 hover:opacity-80 transition-colors ${
                    user.role_id === 0
                      ? "text-white"
                      : user.role_id === 2
                      ? "text-[--secondary-color]"
                      : "text-[--dark-color]"
                  }`}>
                  {link.text}
                </Link>
              ))}

              <button
                onClick={handleLogout}
                className={`${
                  user.role_id === 0
                    ? "bg-[--accent-color] hover:bg-[--secondary-color] text-[--dark-color]"
                    : user.role_id === 2
                    ? "bg-[--dark-color] hover:bg-[--secondary-color] text-white"
                    : "bg-[--secondary-color] hover:bg-[--accent-color] text-[--dark-color]"
                } font-bold py-2 px-4 rounded transition-colors`}>
                Выйти
              </button>
            </nav>
          </div>
        </header>
      )}
    </>
  );
};

export default Header;
