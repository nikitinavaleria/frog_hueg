import React from "react";

export default function Modal({ isOpen, onClose, children }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg w-3/4 max-w-2xl">
        <button onClick={onClose} className="float-right text-xl font-bold">
          &times;
        </button>
        {children}
      </div>
    </div>
  );
}
