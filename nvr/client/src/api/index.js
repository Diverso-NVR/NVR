import axios from "axios";

const API_URL = process.env.API_URL;

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

export function delUser(id, token) {
  return axios.delete(`${API_URL}/users/${id}`, {
    headers: { Authorization: `Bearer: ${token}` }
  });
}

export function changeUserRole({ id, role, token }) {
  return axios.put(
    `${API_URL}/users/roles/${id}`,
    { role },
    {
      headers: { Authorization: `Bearer: ${token}` }
    }
  );
}

export function grantUser(id, token) {
  return axios.put(
    `${API_URL}/users/${id}`,
    {},
    {
      headers: { Authorization: `Bearer: ${token}` }
    }
  );
}

//rooms
export function getRooms() {
  return axios.get(`${API_URL}/rooms/`);
}

export function soundSwitch({ id, sound, token }) {
  return axios.post(
    `${API_URL}/sound`,
    { id, sound },
    { headers: { Authorization: `Bearer: ${token}` } }
  );
}

export function start(id, token) {
  return axios.post(
    `${API_URL}/startRec`,
    { id },
    { headers: { Authorization: `Bearer: ${token}` } }
  );
}

export function stop(id, token) {
  return axios.post(
    `${API_URL}/stopRec`,
    { id },
    { headers: { Authorization: `Bearer: ${token}` } }
  );
}

export function del(id, token) {
  return axios.delete(`${API_URL}/rooms/${id}`, {
    headers: { Authorization: `Bearer: ${token}` }
  });
}

export function add(name, token) {
  return axios.post(
    `${API_URL}/rooms`,
    { name },
    { headers: { Authorization: `Bearer: ${token}` } }
  );
}

export function edit({ id, sources, token }) {
  return axios.put(
    `${API_URL}/rooms/${id}`,
    { sources },
    { headers: { Authorization: `Bearer: ${token}` } }
  );
}
