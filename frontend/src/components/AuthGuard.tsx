import React, { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

interface AuthGuardProps {
  children: React.ReactNode;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const { isAuthenticated, checkTokenExpiration, refreshTokenIfNeeded, logout } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) return;

    // Check token expiration every hour (since tokens now last 30 days)
    const checkInterval = setInterval(async () => {
      console.log('🔍 Checking token expiration...');
      
      const isExpiringSoon = checkTokenExpiration();
      
      if (isExpiringSoon) {
        console.log('⚠️ Token expiring within 24 hours, attempting refresh...');
        
        const refreshSuccessful = await refreshTokenIfNeeded();
        
        if (!refreshSuccessful) {
          console.log('❌ Token refresh failed, logging out...');
          logout();
        }
      }
    }, 60 * 60 * 1000); // Check every hour instead of every 5 minutes

    // Also check immediately on mount
    const checkImmediately = async () => {
      const isExpiringSoon = checkTokenExpiration();
      if (isExpiringSoon) {
        await refreshTokenIfNeeded();
      }
    };
    
    checkImmediately();

    return () => clearInterval(checkInterval);
  }, [isAuthenticated, checkTokenExpiration, refreshTokenIfNeeded, logout]);

  return <>{children}</>;
};
