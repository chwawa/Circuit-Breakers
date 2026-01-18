import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Image,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Audio } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import { useFriends } from '../../hooks/useFriends';
import { MessageBubble } from '../../components/MessageBubble';
import { ChatInput } from '../../components/ChatInput';
import { apiService } from '../../services/api';
import { Message } from '../../types';

import { GLView } from 'expo-gl';
import { createScene } from '../../components/threeScene';

export default function ChatScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const { friends } = useFriends();
  const [messages, setMessages] = useState<Message[]>([]);
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  const threeSceneRef = useRef<any>(null);

  const friend = friends.find((f) => f.id === id);

  useEffect(() => {
    return sound
      ? () => {
          sound.unloadAsync();
        }
      : undefined;
  }, [sound]);

  if (!friend) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.errorText}>Friend not found</Text>
      </SafeAreaView>
    );
  }

  const onContextCreate = (gl: any) => {
    const { drawingBufferWidth, drawingBufferHeight } = gl;

    const scene = createScene(
      gl,
      drawingBufferWidth,
      drawingBufferHeight
    );

    // Use friend-specific model if you want later
    scene.loadModel(friend.modelUrl);

    threeSceneRef.current = scene;
  };


  const playAudioResponse = async (audioUri: string) => {
    try {
      const { sound } = await Audio.Sound.createAsync({ uri: audioUri });
      setSound(sound);
      await sound.playAsync();
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const handleSendText = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);

    const audioUri = await apiService.sendTextMessage(friend.id, text);

    if (audioUri) {
      playAudioResponse(audioUri);
    }

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `Response from ${friend.name}`,
        isUser: false,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 1000);
  };

  const handleSendVoice = async (audioUri: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text: '[Voice message]',
      isUser: true,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);

    const responseUri = await apiService.sendVoiceMessage(friend.id, audioUri);

    if (responseUri) {
      playAudioResponse(responseUri);
    }

    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: '[Voice response]',
        isUser: false,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 1000);
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="white" />
          </TouchableOpacity>
          <Image source={{ uri: friend.imageUrl }} style={styles.avatar} />
          <View style={styles.headerInfo}>
            <Text style={styles.friendName}>{friend.name}</Text>
            {friend.personality && (
              <Text style={styles.friendPersonality}>{friend.personality}</Text>
            )}
          </View>
        </View>

        {/* 3D Model */}
        <View style={styles.modelContainer}>
          <GLView
            style={styles.modelPlaceholder}
            onContextCreate={onContextCreate}
            onTouchStart={() => threeSceneRef.current?.shakeModel()}
          />
        </View>

        {/* Messages */}
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
          onContentSizeChange={() => scrollViewRef.current?.scrollToEnd({ animated: true })}
        >
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </ScrollView>

        {/* Input */}
        <ChatInput onSendText={handleSendText} onSendVoice={handleSendVoice} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
    gap: 12,
  },
  backButton: {
    padding: 8,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 2,
    borderColor: '#a855f7',
  },
  headerInfo: {
    flex: 1,
  },
  friendName: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  friendPersonality: {
    color: '#d8b4fe',
    fontSize: 14,
  },
  modelContainer: {
    padding: 32,
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
    alignItems: 'center',
  },
  modelPlaceholder: {
    width: 256,
    height: 256,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: 'rgba(168, 85, 247, 0.3)',
    backgroundColor: 'rgba(168, 85, 247, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modelText: {
    color: '#d8b4fe',
    fontSize: 16,
    textAlign: 'center',
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    gap: 12,
  },
  errorText: {
    color: 'white',
    fontSize: 18,
    textAlign: 'center',
    marginTop: 50,
  },
});