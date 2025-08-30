import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function OrderComplete() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center bg-[--main-color] p-10 rounded-lg shadow-md min-w-[300px] min-h-[300px]">
        <h2 className="text-2xl font-bold mb-4">Заказ оформлен!</h2>
        <p className="mb-4">Жабка будет позже</p>
        {/* <img src="" alt="Жабка" className="mx-auto mb-4" /> */}
        <p className="mb-10">Ожидайте изменения статуса заказа на мониторе</p>
        <button
          className=" text-2xl text-[#dff8b5] hover:text-[#b5e693] px-6 py-2 rounded-md bg-green-600 transition-colors"
          onClick={() => {
            navigate("/menu");
          }}>
          Еще хочу
        </button>
      </div>
    </div>
  );
}
