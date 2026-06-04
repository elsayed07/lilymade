import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import "./i18n";
import "./index.css";

import Layout from "./components/Layout";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import { StoreProvider } from "./context/StoreContext";
import About from "./pages/About";
import Account from "./pages/Account";
import Cart from "./pages/Cart";
import CollectionPage from "./pages/CollectionPage";
import Contact from "./pages/Contact";
import Home from "./pages/Home";
import OrderCancel from "./pages/OrderCancel";
import OrderSuccess from "./pages/OrderSuccess";
import Policies from "./pages/Policies";
import Product from "./pages/Product";
import Shop from "./pages/Shop";

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/shop", element: <Shop /> },
      { path: "/collections/:handle", element: <CollectionPage /> },
      { path: "/products/:handle", element: <Product /> },
      { path: "/cart", element: <Cart /> },
      { path: "/account", element: <Account /> },
      { path: "/order/success", element: <OrderSuccess /> },
      { path: "/order/cancel", element: <OrderCancel /> },
      { path: "/about", element: <About /> },
      { path: "/contact", element: <Contact /> },
      { path: "/policies", element: <Policies /> },
    ],
  },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <StoreProvider>
      <AuthProvider>
        <CartProvider>
          <RouterProvider router={router} />
        </CartProvider>
      </AuthProvider>
    </StoreProvider>
  </StrictMode>
);
