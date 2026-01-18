import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Platform
} from 'react-native';
import { useRouter } from 'expo-router';
import { useEffect } from 'react';
import { useFriends } from '../../hooks/useFriends';
import { FriendCard } from '../../components/FriendCard';
import { CreateFriendModal } from '../../components/CreateFriendModal';
import ModelPage from '@/components/ModelPage';
import { Ionicons } from '@expo/vector-icons';

const STAR_COUNT = 60;
const isWeb = Platform.OS === 'web';

function BackgroundStars() {
  const stars = Array.from({ length: STAR_COUNT });

  return (
    <View style={styles.starsContainer} pointerEvents="none">
      {stars.map((_, i) => {
        const size = Math.random() * 2 + 1;
        const opacity = Math.random() * 0.6 + 0.2;

        return (
          <View
            key={i}
            style={[
              styles.star,
              {
                width: size,
                height: size,
                borderRadius: size / 2,
                opacity,
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
              },
            ]}
          />
        );
      })}
    </View>
  );
}

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
      {Platform.OS === 'web' && (
        <style>{`
          .glow-title {
            font-size: 300%;
            font-weight: 700;
            color: white;
            display: flex;
            flex-wrap: wrap;
          }

          .glow-letter {
            display: inline-block;
            animation: starGlow 2.5s ease-in-out infinite;
          }

          @keyframes starGlow {
            0% {
              text-shadow: 0 0 4px rgba(216,180,254,0.4);
            }
            50% {
              text-shadow: 0 0 16px rgba(168,85,247,0.8);
            }
            100% {
              text-shadow: 0 0 4px rgba(216,180,254,0.4);
            }
          }
        `}</style>
    )}
      <BackgroundStars />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          {isWeb ? (
            <h1 className="glow-title">
              {"Your 3D Friends".split("").map((char, i) => (
                <span
                  key={i}
                  className="glow-letter"
                  style={{ animationDelay: `${i * 0.15}s` }}
                >
                  {char === " " ? "\u00A0" : char}
                </span>
              ))}
            </h1>
        ) : (
          <Text style={styles.title}>Your 3D Friends</Text>
        )}
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
    alignItems: 'center',
  },
  title: {
    fontSize: 64,
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
  starsContainer: {
    ...StyleSheet.absoluteFillObject,
    zIndex: -1,
  },
  star: {
    position: 'absolute',
    backgroundColor: 'white',

    // Glow ✨
    shadowColor: '#ffffff',
    shadowOpacity: 0.9,
    shadowRadius: 4,

    // Android glow
    elevation: 3,
  },
});