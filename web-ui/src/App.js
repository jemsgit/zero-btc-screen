import React, { useState, useEffect } from "react";
import AlarmList from "./components/AlarmList";
import AlarmForm from "./components/AlarmForm";
import {
  fetchAlarms,
  fetchCurrencyList,
  addAlarm,
  deleteAlarm,
  updateAlarm,
  updateConfigUrl,
  fetchConfigUrl,
} from "./api";

import "./App.css";
import ConfigUrl from "./components/ConfigUrl";

function App() {
  const [alarms, setAlarms] = useState([]);
  const [isLoading, setIsLoading] = useState([]);
  const [currencyList, setCurrencyList] = useState([]);
  const [configUrl, setConfigUrl] = useState("");

  useEffect(() => {
    setIsLoading(true);
    fetchAlarms().then((data) => {
      setAlarms(data);
    });
    fetchConfigUrl().then((data) => setConfigUrl(data.url));
    fetchCurrencyList().then((data) => {
      setCurrencyList(data);
      setIsLoading(false);
    });
  }, []);

  const handleSaveConfigUrl = (newUrl) => {
    setIsLoading(true);
    updateConfigUrl(newUrl)
      .then((data) => setConfigUrl(data.url))
      .finally(() => setIsLoading(false));
  };

  const handleAddAlarm = (alarm) => {
    setIsLoading(true);
    addAlarm(alarm)
      .then(() => {
        return fetchAlarms();
      })
      .then((data) => setAlarms(data))
      .finally(() => setIsLoading(false));
  };

  const handleUpdateAlarm = (currency, alarm) => {
    setIsLoading(true);
    updateAlarm(currency, alarm)
      .then(() => {
        return fetchAlarms();
      })
      .then((data) => setAlarms(data))
      .finally(() => setIsLoading(false));
  };

  const handleDeleteAlarm = (currency) => {
    setIsLoading(true);
    deleteAlarm(currency)
      .then(() => {
        return fetchAlarms();
      })
      .then((data) => setAlarms(data))
      .finally(() => setIsLoading(false));
  };

  const existedAlarms = alarms.map(({ currency }) => currency.toUpperCase());
  const availableCurrencies = currencyList.filter(
    (item) => !existedAlarms.includes(item.toUpperCase())
  );
  return (
    <div className="App">
      <h1 className="title">Cryptocurrency Alarms ⏰</h1>

      <div className="content">
        {isLoading && (
          <div className="loader">
            Пагади, не суетись &nbsp;<span className="flip-content">☕️</span>
          </div>
        )}
        <ConfigUrl url={configUrl} onSave={handleSaveConfigUrl} />
        <AlarmForm
          onSubmit={handleAddAlarm}
          currencyList={availableCurrencies}
        />
        <AlarmList
          alarms={alarms}
          onUpdate={handleUpdateAlarm}
          onDelete={handleDeleteAlarm}
        />
      </div>
    </div>
  );
}

export default App;
