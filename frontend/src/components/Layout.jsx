import { Outlet } from "react-router-dom";

import CookieConsent from "./CookieConsent";
import Footer from "./Footer";
import Header from "./Header";

export default function Layout() {
  return (
    <>
      <Header />
      <main className="main">
        <Outlet />
      </main>
      <Footer />
      <CookieConsent />
    </>
  );
}
