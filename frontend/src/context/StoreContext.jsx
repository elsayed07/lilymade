import { createContext, useContext, useState } from "react";

export const CURRENCIES = [
  { code: "EUR", symbol: "€" },
  { code: "USD", symbol: "$" },
  { code: "GBP", symbol: "£" },
  { code: "CAD", symbol: "CA$" },
];

const StoreContext = createContext(null);

export function StoreProvider({ children }) {
  const [currency, setCurrencyState] = useState(
    () => localStorage.getItem("currency") || "EUR"
  );

  const setCurrency = (code) => {
    setCurrencyState(code);
    localStorage.setItem("currency", code);
  };

  const symbol = CURRENCIES.find((c) => c.code === currency)?.symbol || "";

  return (
    <StoreContext.Provider value={{ currency, setCurrency, symbol }}>
      {children}
    </StoreContext.Provider>
  );
}

export const useStore = () => useContext(StoreContext);
