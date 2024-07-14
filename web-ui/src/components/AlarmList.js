import React from 'react';
import AlarmItem from './AlarmItem';

function AlarmList({ alarms, onUpdate, onDelete }) {
  return (
    <ul className='alarms-list'>
      {alarms.map(alarm => (
        <AlarmItem key={alarm.currency} alarm={alarm} onUpdate={onUpdate} onDelete={onDelete} />
      ))}
    </ul>
  );
}

export default AlarmList;
