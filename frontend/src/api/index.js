import axios from "axios";

const API_URL = `${process.env.NVR_URL}/api`;

//users
export function authenticate(userData) {
  return axios.post(`${API_URL}/login`, userData);
}

export function googleLog({ token }) {
  return axios.post(`${API_URL}/google-login`, { token });
}

export function register(userData) {
  return axios.post(`${API_URL}/register`, userData);
}

export function sendResetEmail(email) {
  return axios.post(`${API_URL}/reset-pass/${email}`, {});
}

export function resetPass({ new_pass, token }) {
  return axios.put(`${API_URL}/reset-pass/${token}`, { new_pass });
}

export function getUsers(token) {
  return axios.get(`${API_URL}/users`, {
    headers: { Token: token }
  });
}

export function inviteUsers(emails, role, token) {
  return axios.post(
    `${API_URL}/users`,
    { emails, role },
    {
      headers: { Token: token }
    }
  );
}

export function createAPIKey(email, token) {
  return axios.post(
    `${API_URL}/api-key/${email}`,
    {},
    {
      headers: { Token: token }
    }
  );
}

export function updateAPIKey(email, token) {
  return axios.put(
    `${API_URL}/api-key/${email}`,
    {},
    {
      headers: { Token: token }
    }
  );
}

export function deleteAPIKey(email, token) {
  return axios.delete(`${API_URL}/api-key/${email}`, {
    headers: { Token: token }
  });
}

export function getAPIKey(email, token) {
  return axios.get(`${API_URL}/api-key/${email}`, {
    headers: { Token: token }
  });
}

export function getRecords(email, token) {
  return axios.get(`${API_URL}/records/${email}`, {
    headers: { Token: token }
  });
}

export function getEruditeRecords(pageNumber) {
  return axios.get(`${API_URL}/erudite/records`, {
    params: {
      page_number: pageNumber,
      with_keywords_only: true,
      ignore_autorec: true
    }
  });
}

//rooms
export function getRooms(token) {
  return axios.get(`${API_URL}/rooms`, {
    headers: { Token: token }
  });
}

export function createMontageEvent(
  { room_name, event_name, date, start_time, end_time },
  token
) {
  return axios.post(
    `${API_URL}/montage-event/${room_name}`,
    { event_name, date, start_time, end_time },
    {
      headers: { Token: token }
    }
  );
}

export function getAutorecParams(token) {
  return axios.get(`${API_URL}/autorec-config`, {
    headers: { Token: token }
  });
}

export function getMonitoringLink(token) {
  return axios.get(`${API_URL}/autorec-monitoring`, {
    headers: { Token: token }
  });
}

export function autorecDeploy({ days, record_start, record_end, duration, upload_without_sound }, token) {
  return axios.put(
      `${API_URL}/autorec-deploy`,
    { days, record_start, record_end, duration, upload_without_sound },
    {
      headers: { Token: token }
    }
  );
}

export function autorecDelete(token) {
  return axios.delete(`${API_URL}/autorec-delete`, {
    headers: { Token: token }
  });
}
