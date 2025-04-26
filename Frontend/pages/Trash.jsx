// import React from "react";
// import { useCart } from "../context/CartContext";
// import { Link } from "react-router-dom";
// import axios from "axios";

// const mockDrinks = [
//   { id: 1, name: "Latte", price: 150 },
//   { id: 2, name: "Espresso", price: 100 },
//   { id: 3, name: "Tea", price: 80 },
// ];

// export default function Menu() {
//   const { addToCart } = useCart();

//   return (
//     <div className="p-4">
//       <div className="flex justify-between items-center mb-6">
//         <h1 className="text-xl font-bold">Меню напитков</h1>
//         <Link
//           to="/login"
//           className="bg-[--dark-color] text-white px-4 py-2 rounded-md hover:opacity-90 transition-opacity">
//           Админ панель
//         </Link>
//       </div>
//       <ul>
//         {mockDrinks.map((drink) => (
//           <li key={drink.id} className="mb-2 flex justify-between">
//             <span>
//               {drink.name} — {drink.price}₽
//             </span>
//             <button
//               className="bg-blue-500 text-white px-2 py-1 rounded"
//               onClick={() => addToCart(drink)}>
//               Добавить
//             </button>
//           </li>
//         ))}
//       </ul>
//       <button
//         onClick={() => {
//           axios.get("http://127.0.0.1:8000/auth/me").then((res) => {
//             alert("Джинсы");
//           });
//         }}
//         className="block mt-4 text-blue-600 underline">
//         Даете ежжи
//       </button>
//     </div>
//   );
// }
