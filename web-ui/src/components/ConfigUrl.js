import React, { useState } from "react";

function ConfigUrl({ url, onSave }) {
  const [isEditing, setIsEditing] = useState(false);
  const [newUrl, setNewUrl] = useState(url);

  const handleEditClick = () => {
    setNewUrl(url);
    setIsEditing(true);
  };

  const handleSaveClick = () => {
    onSave(newUrl);
    setIsEditing(false);
  };

  const handleCancelSave = () => {
    setNewUrl(url);
    setIsEditing(false);
  };

  return (
    <div className="config-url">
      <div className="config-label">URL получения валют</div>
      {isEditing ? (
        <div className="config-form">
          <input
            type="text"
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value.trim())}
          />
          <div className="config-buttons">
            <button className="button" onClick={handleSaveClick}>
              Сохранить
            </button>
            <button className="button" onClick={handleCancelSave}>
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <div className="config-url-view">
          <span>{url}</span>
          <button className="button" onClick={handleEditClick}>
            Изменить
          </button>
        </div>
      )}
    </div>
  );
}

export default ConfigUrl;
