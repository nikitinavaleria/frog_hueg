import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import Modal from "../components/Modal";
import { getMenu, createOrder, addToCart as addToCartApi } from "../api";

export default function Menu() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { addItem, removeItem, cart, clearCart } = useCart();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isOrderConfirmed, setIsOrderConfirmed] = useState(false);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [orderError, setOrderError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    const fetchMenuItems = async () => {
      try {
        const response = await getMenu();
        setMenuItems(response.data);
        setLoading(false);
      } catch (err) {
        setError("Ошибка при загрузке меню. Пожалуйста, попробуйте позже.");
        setLoading(false);
      }
    };

    fetchMenuItems();
  }, [isAuthenticated, navigate]);

  const isInCart = (item) => cart.some((cartItem) => cartItem.id === item.id);

  const handleOrder = async () => {
    try {
      // Validate cart is not empty
      if (cart.length === 0) {
        setOrderError("Корзина пуста. Добавьте товары для оформления заказа.");
        return;
      }

      // Check if all items are available
      const unavailableItems = cart.filter((item) => !item.is_available);
      if (unavailableItems.length > 0) {
        setOrderError(
          `Следующие товары недоступны: ${unavailableItems}
            .map((item) => item.dish_name)
            .join(", ")}`
        );
        return;
      }

      // Create an order
      const orderResponse = await createOrder({});

      if (!orderResponse || !orderResponse.data || !orderResponse.data.id) {
        throw new Error("Не удалось создать заказ");
      }

      const orderId = orderResponse.data.id;

      // Add items to cart
      const cartResponse = await addToCartApi(
        orderId,
        cart.map((item) => item.id)
      );

      if (!cartResponse || !cartResponse.data) {
        throw new Error("Не удалось добавить товары в заказ");
      }

      // Show success message
      setIsOrderConfirmed(true);
      setIsModalOpen(true);
      setOrderError(null);

      // Clear cart and redirect
      clearCart();
      navigate("/order-complete");
    } catch (err) {
      console.error("Order error:", err);

      // Handle specific error cases
      if (err.response) {
        const { status, data } = err.response;
        if (status === 403) {
          setOrderError(
            "У вас нет прав для создания заказа. Пожалуйста, войдите в систему."
          );
        } else if (status === 400) {
          setOrderError(
            data.detail ||
              "Ошибка при создании заказа. Проверьте доступность товаров."
          );
        } else if (status === 500) {
          setOrderError("Ошибка сервера. Пожалуйста, попробуйте позже.");
        } else {
          setOrderError(
            "Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже."
          );
        }
      } else {
        setOrderError(
          "Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже."
        );
      }
    }
  };

  // Group menu items by category
  const uniqueMenuItems = menuItems.reduce((acc, item) => {
    if (
      !acc.some((existingItem) => existingItem.dish_name === item.dish_name)
    ) {
      acc.push(item);
    }
    return acc;
  }, []);

  const categories = {
    Напитки: uniqueMenuItems.filter((item) => item.category === "Напитки"),
    Закуски: uniqueMenuItems.filter((item) => item.category === "Закуски"),
    Салаты: uniqueMenuItems.filter((item) => item.category === "Салаты"),
    Горячее: uniqueMenuItems.filter((item) => item.category === "Горячее"),
    Десерты: uniqueMenuItems.filter((item) => item.category === "Десерты"),
  };

  const isItemTypeInCart = (category) =>
    cart.some((item) => item.category === category);

  if (loading) {
    return (
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Grenoilli de Frace</h1>
        <p>Загрузка меню...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Grenoilli de Frace</h1>
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Grenoilli de Frace</h1>
        {cart.length > 0 && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors">
            Подтвердить заказ
          </button>
        )}
      </div>

      {Object.entries(categories).map(([category, items]) => (
        <div key={category} className="mb-8">
          <h2 className="text-xl font-bold mb-4">{category}:</h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((item) => (
              <li
                key={item.id}
                className="bg-gray-100 p-4 rounded-lg shadow-md">
                <h3 className="font-bold text-lg mb-2">{item.dish_name}</h3>
                <p className="text-gray-700 mb-3">{item.description}</p>
                {item.image && (
                  <img
                    src={item.image}
                    alt={item.dish_name}
                    className="w-full h-48 object-cover rounded-md mb-3"
                  />
                )}
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">
                    Осталось: {item.quantity_left}
                  </span>
                  <button
                    className={`px-4 py-2 rounded-md transition-colors ${
                      isInCart(item)
                        ? "bg-gray-400 hover:bg-gray-500"
                        : "bg-red-500 hover:bg-red-600 text-white"
                    }`}
                    onClick={() => {
                      if (isItemTypeInCart(item.category) && !isInCart(item)) {
                        return;
                      }
                      isInCart(item) ? removeItem(item.id) : addItem(item);
                    }}
                    disabled={!item.is_available}>
                    {!item.is_available
                      ? "Нет в наличии"
                      : isInCart(item)
                      ? "Отменить выбор"
                      : isItemTypeInCart(item.category)
                      ? "Уже выбрано"
                      : "Добавить"}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ))}

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        {isOrderConfirmed ? (
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Заказ оформлен!</h2>
            <p className="mb-4">Вам досталась такая жабка:</p>
            <img src="/images/frog.png" alt="Жабка" className="mx-auto mb-4" />
            <p>Ожидайте изменения статуса заказа на мониторе</p>
            <button
              onClick={() => {
                setIsModalOpen(false);
                clearCart();
              }}>
              Еще хочу
            </button>
          </div>
        ) : (
          <>
            <h2 className="text-xl font-bold mb-4">Подтверждение заказа</h2>
            {orderError && <p className="text-red-500 mb-4">{orderError}</p>}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cart.map((item) => (
                <div key={item.id} className="bg-gray-100 p-4 rounded-lg">
                  <h3 className="font-bold">{item.dish_name}</h3>
                  <p>{item.description}</p>
                  {item.image && (
                    <img
                      src={item.image}
                      alt={item.dish_name}
                      className="w-full h-32 object-cover rounded-md mb-2"
                    />
                  )}
                </div>
              ))}
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleOrder}
                className="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600 transition-colors">
                Оформить заказ
              </button>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
}
