/**
 * Custom hook for fetching news data from the API
 */
import { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

export const useNewsData = (refreshTrigger = 0) => {
  const [newsData, setNewsData] = useState({ articles: [], topics: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchNewsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/news-data`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setNewsData(result.data);
      } else {
        throw new Error(result.error || 'Failed to fetch news data');
      }
    } catch (err) {
      console.error('Error fetching news data:', err);
      setError(err.message);
      
      // Fallback to static data if API fails
      try {
        const { newsData: fallbackData } = await import('../data.js');
        setNewsData(fallbackData);
        console.log('Fallback to static data successful');
      } catch (fallbackError) {
        console.error('Fallback to static data failed:', fallbackError);
        setNewsData({ articles: [], topics: [] });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNewsData();
  }, [refreshTrigger]);

  const refetch = () => {
    fetchNewsData();
  };

  return {
    newsData,
    loading,
    error,
    refetch
  };
}; 