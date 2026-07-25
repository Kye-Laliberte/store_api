import axios from "axios";

// Allow overriding base URL via Vite env var VITE_API_URL, fallback to localhost
const baseURL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
    baseURL,
});

export default api;