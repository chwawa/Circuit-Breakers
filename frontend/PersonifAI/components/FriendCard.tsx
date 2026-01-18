import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { Friend } from '../types';

interface FriendCardProps {
    friend: Friend;
    onPress: () => void;
}

export const FriendCard: React.FC<FriendCardProps> = ({ friend, onPress }) => {
    return (
        <TouchableOpacity
            onPress={onPress}
            disabled={friend.isProcessing}
            style={[styles.card, friend.isProcessing && styles.cardDisabled]}
            activeOpacity={0.7}
        >
            <Image source={{ uri: friend.imageUrl }} style={styles.image} />
              <View style={styles.info}>
                <Text style={styles.name} numberOfLines={1}>
                  {String(friend.name)}
                </Text>

                {typeof friend.personality === 'string' && friend.personality.length > 0 ? (
                  <Text style={styles.personality} numberOfLines={1}>
                    {friend.personality}
                  </Text>
                ) : null}
              </View>
            {friend.isProcessing && (
                <View style={styles.processingOverlay}>
                    <ActivityIndicator size="large" color="#a855f7" />
                </View>
            )}
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 16,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.1)',
        overflow: 'hidden',
        aspectRatio: 1,
    },
    cardDisabled: {
        opacity: 0.5,
    },
    image: {
        width: '100%',
        height: '66.67%',
        backgroundColor: '#1e1b4b',
    },
    info: {
        padding: 16,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        height: '33.33%',
        justifyContent: 'center',
    },
    name: {
        color: 'white',
        fontSize: 18,
        fontWeight: '600',
    },
    personality: {
        color: '#d8b4fe',
        fontSize: 14,
        marginTop: 4,
    },
    processingOverlay: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        justifyContent: 'center',
        alignItems: 'center',
    },
});