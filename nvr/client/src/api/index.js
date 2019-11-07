import axios from "axios";

const API_URL = `${process.env.NVR_URL}/api`;

//users
export function authenticate(userData) {
  return axios.post(`${API_URL}/login`, userData);
}

export function register(userData) {
  return axios.post(`${API_URL}/register`, userData);
}

export function getUsers(token) {
  return axios.get(`${API_URL}/users`, {
    headers: { Authorization: `Bearer: ${token}` }
  });
}

export function createAPIKey(email, token) {
  return axios.post(
    `${API_URL}/api-key/${email}`,
    {},
    {
      headers: { Authorization: `Bearer: ${token}` }
    }
  );
}

export function updateAPIKey(email, token) {
  return axios.put(
    `${API_URL}/api-key/${email}`,
    {},
    {
      headers: { Authorization: `Bearer: ${token}` }
    }
  );
}

export function deleteAPIKey(email, token) {
  return axios.delete(`${API_URL}/api-key/${email}`, {
    headers: { Authorization: `Bearer: ${token}` }
  });
}

//rooms
export function getRooms() {
  return axios.get(`${API_URL}/rooms/`);
}
