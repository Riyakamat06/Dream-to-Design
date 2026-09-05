import { createContext, useContext, useState, useEffect } from "react";
import { login as apiLogin, getCurrentUser } from "../api/api";

// This file holds the logged-in user's state globally, so any
// component in the app can access "who's logged in" without
// passing it down manually through every component in between.

// What this provides:
// - user -> the current user's data (or null if not logged in)
// - token -> the JWT access token (or null)
// - login(email, password) -> logs in, stores user + token
// - logout() -> clears user + token
// - loading -> true while we're checking if a token exists on load

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  // On first load (or whenever the token changes), check if the
  // saved token is still valid by fetching the real user profile.
  useEffect(() => {
    if (token) {
      getCurrentUser(token)
        .then((userData) => setUser(userData))
        .catch(() => {
          setToken(null);
          localStorage.removeItem("token");
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  async function login(email, password) {
    const data = await apiLogin(email, password);
    setToken(data.access_token);
    localStorage.setItem("token", data.access_token);
    const userData = await getCurrentUser(data.access_token);
    setUser(userData);
  }

  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Convenience hook — lets any component call useAuth() instead of
// writing useContext(AuthContext) themselves every time.
export function useAuth() {
  return useContext(AuthContext);
}

// context/AuthContext.jsx's role in the project:
// Holds the logged-in user's state globally using React Context,
// so any component can know who's logged in without prop-drilling.
//
// Core idea:
// AuthProvider wraps the whole app and provides user, token, login,
// logout, and loading to every nested component via useAuth(). The
// token is persisted in localStorage so a page refresh doesn't log
// the user out, and useEffect verifies the saved token is still
// valid on load by calling the real /users/me endpoint.