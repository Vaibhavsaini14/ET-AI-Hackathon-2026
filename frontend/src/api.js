import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await axios.post(`${API_BASE}/documents/upload`, formData);
  return res.data;
};

export const sendQuery = async (query, userRole, docIds = []) => {
  const res = await axios.post(`${API_BASE}/chat/query`, {
    query,
    user_role: userRole,
    doc_ids: docIds,
  });
  return res.data;
};

export const getAnalytics = async () => {
  const res = await axios.get(`${API_BASE}/analytics/dashboard`);
  return res.data;
};

export const getGraphEntities = async () => {
  const res = await axios.get(`${API_BASE}/graph/entities`);
  return res.data;
};