import axios from "axios";

const API_URL = process.env.API_URL;

//users
export function authenticate(userData) {
  return axios.post(`${API_URL}/login`, userData);
}

export function register(userData) {
  return axios.post(`${API_URL}/register`, userData);
}

export function getUsers() {
  return axios.get(`${API_URL}/users`);
}

export function delUser(id, jwt) {
  return axios.delete(`${API_URL}/users/${id}`, {
    headers: { Authorization: `Bearer: ${jwt}` }
  });
}

export function changeUserRole(id, role, jwt) {
  return axios.put(
    `${API_URL}/users/roles/${id}`,
    { role },
    {
      headers: { Authorization: `Bearer: ${jwt}` }
    }
  );
}

export function grantUser(id, jwt) {
  return axios.put(
    `${API_URL}/users/${id}`,
    {},
    {
      headers: { Authorization: `Bearer: ${jwt}` }
    }
  );
}

//rooms
export function getRooms() {
  return axios.get(`${API_URL}/rooms/`);
}

export function soundSwitch(id, sound, jwt) {
  return axios.post(
    `${API_URL}/sound`,
    { id, sound },
    { headers: { Authorization: `Bearer: ${jwt}` } }
  );
}

export function start(id, jwt) {
  return axios.post(
    `${API_URL}/startRec`,
    { id },
    { headers: { Authorization: `Bearer: ${jwt}` } }
  );
}

export function stop(id, jwt) {
  return axios.post(
    `${API_URL}/stopRec`,
    { id },
    { headers: { Authorization: `Bearer: ${jwt}` } }
  );
}

export function del(id, jwt) {
  return axios.delete(`${API_URL}/rooms/${id}`, {
    headers: { Authorization: `Bearer: ${jwt}` }
  });
}

export function add(name, jwt) {
  return axios.post(
    `${API_URL}/rooms`,
    { name },
    { headers: { Authorization: `Bearer: ${jwt}` } }
  );
}

export function edit(id, sources, jwt) {
  return axios.put(
    `${API_URL}/rooms/${id}`,
    { sources },
    { headers: { Authorization: `Bearer: ${jwt}` } }
  );
}
