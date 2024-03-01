import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UserDetail.css'; // Import the CSS file
import { getBaseURL } from '../../config';

function UserDetail({ match }) {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [disableStatus, setDisableStatus] = useState(false);

  useEffect(() => {
    const { uid } = match.params;
    const fetchUser = async () => {
      try {
        const response = await axios.get(`${getBaseURL()}/user/${uid}`);
        const formattedUserData = formatUserData(response.data);
        setUserData(formattedUserData);
        setDisableStatus(formattedUserData.disable === 1);
      } catch (error) {
        setError('Error fetching user');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [match.params]);

  const formatUserData = (data) => {
    const formattedData = { ...data };
    if (formattedData.ts_lastentry) {
      formattedData.ts_lastentry = new Date(formattedData.ts_lastentry).toLocaleString();
    }
    return formattedData;
  };

  const handleDisableChange = async () => {
    try {
      const newValue = disableStatus ? 0 : 1;
      await axios.put(`${getBaseURL()}/userupdate/${userData.uid}`, { disable: newValue });
      setDisableStatus(newValue === 1);
      setUserData(prevData => ({ ...prevData, disable: newValue }));
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (!userData) return <div>User not found</div>;

  return (
    <div className="user-detail-container">
      <h2>User Detail</h2>
      <ul className="user-detail-list">
        {Object.entries(userData).map(([key, value]) => (
          <li key={key} className="user-detail-item">
            <span className="user-detail-key">{key}:</span>
            <span className="user-detail-value">
              {key === 'disable' ? '' : Array.isArray(value) ? value.join(', ') : value}
            </span>
            {key === 'disable' && (
              <button className="toggle-button" onClick={handleDisableChange}>
                {disableStatus ? 'Enable' : 'Disable'}
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default UserDetail;







