import { createContext, useContext, useEffect, useState } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => {
    const raw = localStorage.getItem("cart");
    return raw ? JSON.parse(raw) : [];
  });

  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(items));
  }, [items]);

  const add = (line) => {
    setItems((prev) => {
      const idx = prev.findIndex((x) => x.variant_id === line.variant_id);
      if (idx >= 0) {
        const copy = [...prev];
        copy[idx] = { ...copy[idx], quantity: copy[idx].quantity + line.quantity };
        return copy;
      }
      return [...prev, line];
    });
  };

  const setQuantity = (variant_id, quantity) => {
    setItems((prev) =>
      prev
        .map((x) => (x.variant_id === variant_id ? { ...x, quantity } : x))
        .filter((x) => x.quantity > 0)
    );
  };

  const remove = (variant_id) =>
    setItems((prev) => prev.filter((x) => x.variant_id !== variant_id));

  const clear = () => setItems([]);

  const count = items.reduce((n, x) => n + x.quantity, 0);

  return (
    <CartContext.Provider value={{ items, add, setQuantity, remove, clear, count }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
