import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useEffect } from 'react';
import { useFriends } from '../../hooks/useFriends';
import { FriendCard } from '../../components/FriendCard';
import { CreateFriendModal } from '../../components/CreateFriendModal';
import ModelPage from '@/components/ModelPage';
import { Ionicons } from '@expo/vector-icons';

export default function FriendsScreen() {
  const router = useRouter();
  const { friends, addFriend, pollProcessingFriends } = useFriends();

  useEffect(() => {
    pollProcessingFriends();
  }, []);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showModelPage, setShowModelPage] = useState(false);

  const handleSelectFriend = (friendId: string) => {
    router.push(`/friend/${friendId}`);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>Your 3D Friends</Text>
          <Text style={styles.subtitle}>Create and chat with your AI companions</Text>
        </View>

        <View style={styles.grid}>
          {/* Create Friend Card */}
          <TouchableOpacity
            onPress={() => setShowCreateModal(true)}
            style={styles.createCard}
            activeOpacity={0.7}
          >
            <View style={styles.createIconContainer}>
              <Ionicons name="add" size={32} color="white" />
            </View>
            <Text style={styles.createText}>Create Friend</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => setShowModelPage(true)}
            style={styles.createCard}
            activeOpacity={0.7}
          >
            <View style={styles.createIconContainer}>
              <Ionicons name="add" size={32} color="white" />
            </View>
            <Text style={styles.createText}>See Model</Text>
          </TouchableOpacity>

          {/* Friend Cards */}
          {friends.map((friend) => (
            <FriendCard
              key={friend.id}
              friend={friend}
              onPress={() => handleSelectFriend(friend.id)}
            />
          ))}
        </View>

        {friends.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No friends yet. Create your first one!</Text>
          </View>
        )}
      </ScrollView>

      <CreateFriendModal
        visible={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreateFriend={addFriend}
      />
      <ModelPage
        visible={showModelPage}
        onClose={() => setShowModelPage(false)}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  scrollContent: {
    padding: 24,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#d8b4fe',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 24,
  },
  createCard: {
    width: '45%',
    aspectRatio: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 16,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: 'rgba(168, 85, 247, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  createIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#9333ea',
    justifyContent: 'center',
    alignItems: 'center',
  },
  createText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  emptyState: {
    paddingVertical: 48,
    alignItems: 'center',
  },
  emptyText: {
    color: '#d8b4fe',
    fontSize: 18,
  },
});