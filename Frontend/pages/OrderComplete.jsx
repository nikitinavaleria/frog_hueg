import React from "react";
import { Link } from "react-router-dom";

export default function OrderComplete() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center bg-[--main-color] p-10 rounded-lg shadow-md min-w-[300px] min-h-[300px]">
        <h2 className="text-2xl font-bold mb-4">Заказ оформлен!</h2>
        <p className="mb-4">Жабка будет позже</p>
        {/* <img src="" alt="Жабка" className="mx-auto mb-4" /> */}
        <p>Ожидайте изменения статуса заказа на мониторе</p>
      </div>
    </div>
  );
}
