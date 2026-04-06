import React, { useState, useEffect } from "react";
import { Disclosure } from "@headlessui/react";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";
import { Link, useLocation } from "react-router-dom";

const navigation = [
  { name: "About", href: "/" },
  { name: "Start Practice", href: "/get-started" },
  { name: "Dashboard", href: "/dashboard" },
  { name: "Leaderboard", href: "/leaderboard" },
];

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

const Navbar = () => {
  const location = useLocation();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    if (token) {
      setIsLoggedIn(true);
      if (storedUser) setUser(JSON.parse(storedUser));
    } else {
      setIsLoggedIn(false);
      setUser(null);
    }
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/";
  };

  return (
    <Disclosure
      as="nav"
      className="bg-gray-900 bg-opacity-95 fixed w-full z-[9999] shadow-xl border-b border-gray-800 backdrop-blur-md"
    >
      {({ open, close }) => (
        <>
          <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
            <div className="relative flex h-20 items-center justify-between">
              {/* Mobile Menu Button */}
              <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
                <Disclosure.Button className="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none">
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Disclosure.Button>
              </div>

              {/* Logo Section */}
              <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
                <Link to="/" className="flex flex-shrink-0 items-center">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400 font-black text-3xl tracking-tight">
                    Alcruiter
                  </span>
                </Link>

                {/* Desktop Navigation */}
                <div className="hidden sm:ml-10 sm:block">
                  <div className="flex space-x-2">
                    {navigation.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? "bg-gray-800 text-white"
                            : "text-gray-400 hover:bg-gray-800 hover:text-white",
                          "px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300"
                        )}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="hidden sm:flex sm:items-center sm:gap-4">
                {isLoggedIn ? (
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-400 font-medium">Hello, <span className="text-indigo-400">{user?.name}</span></span>
                    <button
                      onClick={handleLogout}
                      className="text-sm font-bold text-white bg-gray-800 hover:bg-red-900/40 hover:text-red-400 border border-gray-700 px-5 py-2.5 rounded-xl transition-all"
                    >
                      Log Out
                    </button>
                    <Link
                      to="/get-started"
                      className="text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-500 px-5 py-2.5 rounded-xl shadow-lg shadow-indigo-600/20 transition-all"
                    >
                      New Session
                    </Link>
                  </div>
                ) : (
                  <div className="flex items-center gap-4">
                    <Link
                      to="/login"
                      className="text-sm font-bold text-gray-400 hover:text-white transition-all"
                    >
                      Sign In
                    </Link>
                    <Link
                      to="/login"
                      className="text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-500 px-5 py-2.5 rounded-xl shadow-lg shadow-indigo-600/20 transition-all"
                    >
                      Get Started Free
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Mobile Navigation Panel */}
          <Disclosure.Panel className="sm:hidden bg-gray-900 border-b border-gray-800">
            <div className="space-y-1 px-4 pt-2 pb-6">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={classNames(
                    location.pathname === item.href
                      ? "bg-gray-800 text-white text-lg"
                      : "text-gray-400 hover:text-white text-lg",
                    "block rounded-xl px-4 py-3 font-semibold transition-all"
                  )}
                  onClick={close}
                >
                  {item.name}
                </Link>
              ))}
              <div className="pt-4 mt-4 border-t border-gray-800">
                {isLoggedIn ? (
                  <button
                    onClick={() => { handleLogout(); close(); }}
                    className="w-full text-left rounded-xl px-4 py-3 text-lg font-bold text-red-400 hover:bg-red-900/20 transition-all"
                  >
                    Log Out
                  </button>
                ) : (
                  <Link
                    to="/login"
                    className="block rounded-xl px-4 py-3 text-lg font-bold text-indigo-400 hover:bg-indigo-900/20 transition-all"
                    onClick={close}
                  >
                    Log In / Sign Up
                  </Link>
                )}
              </div>
            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
};

export default Navbar;
