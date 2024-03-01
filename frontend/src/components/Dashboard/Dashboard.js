import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import './Dashboard.css'; // Import the CSS file for styling
import { getBaseURL } from '../../config';

function Dashboard() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Fetch users data when the component mounts
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      // Fetch users data from the API
      const response = await axios.get(`${getBaseURL()}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleDisableChange = async (userId) => {
    try {
      // Toggle the disable value for the user
      const newValue = users.find(user => user.uid === userId).disable === 1 ? 0 : 1;

      // Send PUT request to update the user's disable status
      await axios.put(`${getBaseURL()}/userupdate/${userId}`, { disable: newValue });

      // Update local state to reflect the change
      const updatedUsers = users.map(user => {
        if (user.uid === userId) {
          return { ...user, disable: newValue };
        }
        return user;
      });
      setUsers(updatedUsers);
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const history = useHistory();

  const handleDetailsClick = (uid) => {
    // Navigate to the UserDetail component with the uid as a parameter
    history.push(`/UserDetail/${uid}`);
  };

  return (
    <div className="container">
      <h1>Users</h1>
      <table className="user-table">
        <thead>
          <tr>
            <th>UID</th>
            <th>User Type</th>
            <th>Timestamp</th>
            <th>Last Entry Timestamp</th>
            <th>Password</th>
            <th>Disabled</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Username</th>
            <th>Company</th>
            <th>Details</th> {/* Added a new column for details button */}
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.uid}>
              <td>{user.uid}</td>
              <td>{user.UserType}</td>
              <td>{user.tstamp}</td>
              <td>{user.ts_lastentry}</td>
              <td>{user.password}</td>
              <td>
                <button
                  className="toggle-button"
                  onClick={() => handleDisableChange(user.uid)}
                >
                  {user.disable === 1 ? 'Enable' : 'Disable'}
                </button>
              </td>
              <td>{user.first_name}</td>
              <td>{user.lastName}</td>
              <td>{user.username}</td>
              <td>{user.companies.join(', ')}</td> {/* Render associated companies */}
              <td>
                <button
                  className="detail-button"
                  onClick={() => handleDetailsClick(user.uid)} // Pass uid to the handler
                >
                  Details
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Dashboard;

