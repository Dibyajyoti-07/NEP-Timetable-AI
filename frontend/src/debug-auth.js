// Debug authentication state
console.log('=== AUTH DEBUG START ===');

// Check localStorage for auth data
const authStorage = localStorage.getItem('auth-storage');
console.log('📦 Auth storage:', authStorage);

if (authStorage) {
  try {
    const parsed = JSON.parse(authStorage);
    console.log('📦 Parsed auth storage:', parsed);
    
    if (parsed.state && parsed.state.token) {
      const token = parsed.state.token;
      console.log('🔑 Token found:', token.substring(0, 50) + '...');
      
      // Decode JWT to check expiration
      try {
        const tokenParts = token.split('.');
        const payload = JSON.parse(atob(tokenParts[1]));
        const currentTime = Date.now() / 1000;
        const timeUntilExpiry = payload.exp - currentTime;
        
        console.log('⏰ Token payload:', payload);
        console.log('⏰ Current time:', currentTime);
        console.log('⏰ Token expires at:', payload.exp);
        console.log('⏰ Time until expiry (seconds):', timeUntilExpiry);
        console.log('⏰ Token is expired:', timeUntilExpiry <= 0);
      } catch (e) {
        console.error('❌ Error decoding token:', e);
      }
    } else {
      console.log('❌ No token in storage');
    }
  } catch (e) {
    console.error('❌ Error parsing auth storage:', e);
  }
} else {
  console.log('❌ No auth storage found');
}

// Test API call
fetch('http://localhost:8000/api/v1/timetable', {
  headers: {
    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('auth-storage') || '{}').state?.token || ''}`,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('🌐 API Response status:', response.status);
  return response.text();
})
.then(data => {
  console.log('🌐 API Response data:', data);
})
.catch(error => {
  console.error('🌐 API Error:', error);
});

console.log('=== AUTH DEBUG END ===');