import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  getOrders,
  updateOrderStatus,
  deleteOrder,
  clearOrders,
  removeFromCart,
  getCart,
  getMenu,
  updateMenuItem,
} from "../api";
import { useAuth } from "../context/AuthContext";
import AddDish from "../components/AddDish/AddDish";

const Admin = () => {
  const [orders, setOrders] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const statuses = [
    { id: 1, name: "Создан" },
    { id: 2, name: "Готовится" },
    { id: 3, name: "Готов" },
    { id: 4, name: "Выдан" },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (!isAuthenticated()) {
          navigate("/login");
          return;
        }
        const [ordersResponse, menuResponse] = await Promise.all([
          getOrders(),
          getMenu(),
        ]);
        const ordersData = Array.isArray(ordersResponse?.data)
          ? ordersResponse.data
          : [];
        const menuData = Array.isArray(menuResponse?.data)
          ? menuResponse.data
          : [];

        // Дедупликация меню по dish_name
        const uniqueMenuData = menuData.reduce((acc, item) => {
          if (
            !acc.some(
              (existingItem) => existingItem.dish_name === item.dish_name
            )
          ) {
            acc.push(item);
          }
          return acc;
        }, []);

        setOrders(ordersData);
        setMenuItems(uniqueMenuData);
        setError(null);
      } catch (err) {
        console.error("Error fetching data:", err);
        if (err.response?.status === 401) {
          navigate("/login");
        } else {
          setError("Ошибка при загрузке данных");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate, isAuthenticated]);

  const handleStatusChange = async (orderId, newStatusId) => {
    try {
      const newStatus = statuses.find((s) => s.id === newStatusId);

      if (newStatus.name === "Выдан") {
        await updateOrderStatus(orderId, newStatusId);
        await deleteOrder(orderId);
        setOrders(orders.filter((order) => order.id !== orderId));
      } else {
        const response = await updateOrderStatus(orderId, newStatusId);
        if (response?.data) {
          setOrders(
            orders.map((order) =>
              order.id === orderId ? response.data : order
            )
          );
        }
      }
      setError(null);
    } catch (err) {
      console.error("Error updating order status:", err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Ошибка при обновлении статуса заказа");
      }
    }
  };

  const handleQuantityChange = async (itemId, newQuantity) => {
    try {
      const item = menuItems.find((item) => item.id === itemId);
      if (!item) return;

      // Если поле пустое, устанавливаем 0
      const newQuantityInt = newQuantity === "" ? 0 : parseInt(newQuantity);
      const isAvailable = newQuantityInt > 0;

      const response = await updateMenuItem(itemId, {
        dish_name: item.dish_name,
        image: item.image || null,
        is_available: isAvailable,
        description: item.description || null,
        category: item.category || null,
        quantity_left: newQuantityInt,
      });

      if (response?.data) {
        setMenuItems(
          menuItems.map((item) => (item.id === itemId ? response.data : item))
        );
      }
      setError(null);
    } catch (err) {
      console.error("Error updating item quantity:", err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Ошибка при обновлении количества блюда");
      }
    }
  };

  const handleClearOrders = async () => {
    try {
      await clearOrders(); // DELETE /api/orders/
      setOrders([]); // обновляем состояние
      setError(null);
    } catch (err) {
      console.error("Error clearing orders:", err);
      setError(err.response?.data?.detail || "Ошибка при очистке заказов");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-red-500 text-xl">{error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Панель управления</h1>
        <button
          onClick={handleClearOrders}
          className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded">
          Очистить все заказы
        </button>
      </div>

      {/* Секция управления меню */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Управление меню</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {menuItems.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-semibold text-lg mb-2">{item.dish_name}</h3>
              <div className="flex items-center gap-4">
                <label className="text-sm text-gray-600">
                  Количество:
                  <input
                    type="number"
                    min="0"
                    value={item.quantity_left}
                    onChange={(e) => {
                      const value = e.target.value;
                      // Если значение пустое, разрешаем ввод
                      if (value === "") {
                        handleQuantityChange(item.id, value);
                      } else {
                        // Иначе проверяем, что это число и оно неотрицательное
                        const numValue = parseInt(value);
                        if (!isNaN(numValue) && numValue >= 0) {
                          handleQuantityChange(item.id, numValue);
                        }
                      }
                    }}
                    className="ml-2 border rounded px-2 py-1 w-20"
                  />
                </label>
                <span
                  className={`text-sm ${
                    item.is_available ? "text-green-500" : "text-red-500"
                  }`}>
                  {item.is_available ? "Доступно" : "Недоступно"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <AddDish />
      {/* Секция заказов */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Управление заказами</h2>
        {!Array.isArray(orders) || orders.length === 0 ? (
          <div className="text-center text-gray-500 text-xl">
            Нет активных заказов
          </div>
        ) : (
          <div className="grid gap-6">
            {orders.map((order) => (
              <div key={order.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-xl font-semibold">Заказ #{order.id}</h2>
                    <p className="text-gray-500">
                      Создан: {new Date(order.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <select
                      value={order.status_id}
                      onChange={(e) =>
                        handleStatusChange(order.id, parseInt(e.target.value))
                      }
                      className="border rounded px-3 py-2">
                      {statuses.map((status) => (
                        <option key={status.id} value={status.id}>
                          {status.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Состав заказа:</h3>
                  <ul className="space-y-2">
                    {Array.isArray(order.items) &&
                      order.items.map((item) => (
                        <li key={item.id} className="flex justify-between">
                          <span>
                            {item.dish_name} x {item.quantity}
                          </span>
                          <span className="text-gray-500">
                            {item.is_available ? "Доступно" : "Недоступно"}
                          </span>
                        </li>
                      ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
