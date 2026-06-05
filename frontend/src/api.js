const API_BASE = '';

async function handleResponse(response) {
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.message || 'Request failed';
    const errors = body?.errors || null;
    throw { message, errors };
  }
  return body?.data;
}

export async function getStandups(limit = 50, offset = 0) {
  const response = await fetch(`${API_BASE}/api/standups?limit=${limit}&offset=${offset}`);
  return handleResponse(response);
}

export async function getStats() {
  const response = await fetch(`${API_BASE}/api/standups/stats`);
  return handleResponse(response);
}

export async function createStandup(formData) {
  const response = await fetch(`${API_BASE}/api/standups`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
}
