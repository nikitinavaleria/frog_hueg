import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { getDisplayData } from "../api";

export default function Display() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await getDisplayData();
        // Проверяем, что response.data существует и является массивом
        const ordersData = Array.isArray(response.data) ? response.data : [];
        setOrders(ordersData);
      } catch (err) {
        console.error("Error fetching orders:", err);
        setError("Ошибка при загрузке заказов");
      }
    };

    // Initial fetch
    fetchOrders();

    // Set up polling every 10 seconds
    const interval = setInterval(fetchOrders, 10000);

    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  // Разделяем заказы по статусам
  const cookingOrders = orders.filter((order) => order.status === "Готовится");
  const readyOrders = orders.filter((order) => order.status === "Готов");

  if (error) {
    return (
      <div className="p-4 text-center">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  const OrderCard = ({ order }) => (
    <div className="bg-[--accent-color] p-6 rounded-lg shadow-lg">
      <div className="text-xl font-semibold mb-4">Заказ #{order.id}</div>
      <div className="space-y-2">
        {order.items && order.items.length > 0 ? (
          order.items.map((item) => (
            <div
              key={item.id || item.dish_name}
              className="flex justify-between">
              <span>{item.dish_name}</span>
              <span className="font-medium">{item.quantity}x</span>
            </div>
          ))
        ) : (
          <div className="text-gray-500">Нет блюд в заказе</div>
        )}
      </div>
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-lg font-semibold text-[--dark-color]">
          Статус: {order.status}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[--main-color] p-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Левая колонка - заказы в процессе приготовления */}
          <div>
            <h2 className="text-2xl font-bold mb-4 text-center">Хуевертится</h2>
            {cookingOrders.length === 0 ? (
              <div className="text-center text-xl text-gray-600">
                Повара в полном откисе
              </div>
            ) : (
              <div className="space-y-4">
                {cookingOrders.map((order) => (
                  <OrderCard key={order.id} order={order} />
                ))}
              </div>
            )}
          </div>

          {/* Правая колонка - готовые заказы */}
          <div>
            <h2 className="text-2xl font-bold mb-4 text-center">Жрити</h2>
            {readyOrders.length === 0 ? (
              <div className="text-center text-xl text-gray-600">
                Нема готового
              </div>
            ) : (
              <div className="space-y-4">
                {readyOrders.map((order) => (
                  <OrderCard key={order.id} order={order} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
