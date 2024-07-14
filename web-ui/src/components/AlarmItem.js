
import React, { useState } from 'react';

function AlarmItem({ alarm, onUpdate, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedAlarm, setEditedAlarm] = useState({ ...alarm, type: alarm.isRising ? 'rising' : 'falling' });

  const handleUpdate = () => {
    onUpdate(alarm.currency, { ...editedAlarm, isRising: editedAlarm.type === 'rising' });
    setIsEditing(false);
  };

  return (
    <li className={`list-item ${!alarm.isActive ? 'not-active' : 'active'}`}>
      {isEditing ? (
        <div className='item-form'>
          <div className='item-form-controls'>
            <span>{editedAlarm.currency}</span>
            <select
              value={editedAlarm.type}
              onChange={e => setEditedAlarm({...editedAlarm, type: e.target.value})}
            >
              <option value="rising">Вверх</option>
              <option value="falling">Вниз</option>
            </select>
            <input
              type="number"
              value={editedAlarm.value}
              onChange={e => setEditedAlarm({...editedAlarm, value: parseFloat(e.target.value)})}
            />
            <label>Активен: <input type='checkbox' name='isActive' defaultChecked={editedAlarm.isActive} onChange={e => {
              setEditedAlarm({...editedAlarm, isActive: e.target.checked})
            }}/></label>
          </div>
          <div className='buttons-area'>
            <button onClick={handleUpdate} className='button'>Сохранить</button>
            <button onClick={() => setIsEditing(false)} className='button'>Отмена</button>
          </div>
        </div>
      ) : (
        <div className='list-item-value' onClick={() => setIsEditing(true)}>

          <div>{alarm.currency}  {alarm.isRising ? "Вверх" : "Вниз"}  {alarm.value}</div>
          <button onClick={(e) => { e.stopPropagation(); onDelete(alarm.currency) }} className="button">Удалить</button>
        </div>
      )}
    </li>
  );
}

export default AlarmItem;
