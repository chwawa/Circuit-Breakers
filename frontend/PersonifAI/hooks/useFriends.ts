import { useState, useEffect } from 'react';
import { Alert } from 'react-native';
import { Friend } from '../types';
import { apiService } from '../services/api';

export const useFriends = () => {
  const [friends, setFriends] = useState<Friend[]>([]);

  // Poll for processing friends
  useEffect(() => {
    const processingFriends = friends.filter(f => f.isProcessing);
    
    if (processingFriends.length === 0) return;

    const interval = setInterval(async () => {
      for (const friend of processingFriends) {
        const status = await apiService.getFriendStatus(friend.id);
        if (!status.isProcessing) {
          setFriends(prev => prev.map(f => 
            f.id === friend.id ? { ...f, isProcessing: false } : f
          ));
          // Show notification
          Alert.alert('Friend Ready!', `${friend.name} is ready to chat!`);
        }
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [friends]);

  const addFriend = (friend: Friend) => {
    setFriends(prev => [...prev, friend]);
  };

  const updateFriend = (id: string, updates: Partial<Friend>) => {
    setFriends(prev => prev.map(f => 
      f.id === id ? { ...f, ...updates } : f
    ));
  };

  return { friends, addFriend, updateFriend };
};
