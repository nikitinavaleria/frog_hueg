import React from "react";
import { Link, useNavigate } from "react-router-dom";
import cl from "./AddDish.module.scss";

export default function AddDish() {
  return (
    <div className={cl.addDish}>
      <h2 className={cl.title}>Добавить блюдо</h2>
      <form className={cl.form}>
        <input placeholder="Название блюда"></input>
        <input placeholder="Количество"></input>
        <textarea placeholder="Описание"></textarea>
        <select placeholder="Категория">
          <option value="Напитки">Напитки</option>
          <option value="Закуски">Закуски</option>
          <option value="Салаты">Салаты</option>
          <option value="Горячее">Горячее</option>
          <option value="Десерты">Десерты</option>
        </select>
        <input type="file" placeholder="Картинка"></input>
      </form>
    </div>
  );
}
