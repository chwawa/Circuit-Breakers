import { create } from 'zustand';
import { Alert } from 'react-native';
import { Friend } from '../types';
import { apiService } from '../services/api';

type FriendsState = {
  friends: Friend[];
  addFriend: (friend: Friend) => void;
  updateFriend: (id: string, updates: Partial<Friend>) => void;
  pollProcessingFriends: () => void;
};

export const useFriends = create<FriendsState>((set, get) => ({
  friends: [],

  addFriend: (friend) =>
    set(state => ({ friends: [...state.friends, friend] })),

  updateFriend: (id, updates) =>
    set(state => ({
      friends: state.friends.map(f =>
        f.id === id ? { ...f, ...updates } : f
      ),
    })),

  pollProcessingFriends: () => {
    setInterval(async () => {
      for (const friend of get().friends.filter(f => f.isProcessing)) {
        const status = await apiService.getFriendStatus(friend.id);
        if (!status.isProcessing) {
          get().updateFriend(friend.id, { isProcessing: false });
          Alert.alert('Friend Ready!', `${friend.name} is ready to chat!`);
        }
      }
    }, 3000);
  },
}));
