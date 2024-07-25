const baseUrl = "http://localhost:5001";

const username = "0";
const password = "passForCrypto";
const authToken = btoa(`${username}:${password}`);

export const fetchAlarms = async () => {
  try {
    const response = await fetch(`/api/alarms`, {
      headers: {
        Authorization: `Basic ${authToken}`,
      },
    });
    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      console.error("Failed to fetch alarms");
    }
  } catch (e) {
    console.log(e);
  }
  return [];
};

export const fetchCurrencyList = async () => {
  const response = await fetch(`/api/currency-list`, {
    headers: {
      Authorization: `Basic ${authToken}`,
    },
  });
  if (response.ok) {
    const data = await response.json();
    return data.list;
  } else {
    console.error("Failed to fetch currency list");
  }
  return [];
};

export const addAlarm = async (newAlarm) => {
  const response = await fetch(`/api/alarms`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${authToken}`,
    },
    body: JSON.stringify(newAlarm),
  });
  if (response.ok) {
    const data = await response.json();
    return data;
  } else {
    console.error("Failed to add alarm");
  }
};

export const updateAlarm = async (currency, updatedAlarm) => {
  const response = await fetch(`/api/alarms/${currency}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${authToken}`,
    },
    body: JSON.stringify(updatedAlarm),
  });
  if (response.ok) {
    return true;
  } else {
    console.error("Failed to update alarm");
  }
};

export const deleteAlarm = async (currency) => {
  const response = await fetch(`/api/alarms/${currency}`, {
    method: "DELETE",
    headers: {
      Authorization: `Basic ${authToken}`,
    },
  });
  if (response.ok) {
    return 1;
  } else {
    console.error("Failed to delete alarm");
  }
};

export async function fetchConfigUrl() {
  const response = await fetch(`/api/currency-list-url`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${authToken}`,
    },
  });
  const data = await response.json();
  return data;
}

export async function updateConfigUrl(newUrl) {
  const response = await fetch(`/api/currency-list-url`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${authToken}`,
    },
    body: JSON.stringify({ url: newUrl }),
  });
  const data = await response.json();
  return data;
}
