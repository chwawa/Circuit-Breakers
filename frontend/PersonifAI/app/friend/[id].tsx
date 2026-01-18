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
  Dimensions,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Audio } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import { useFriends } from '../../hooks/useFriends';
import { MessageBubble } from '../../components/MessageBubble';
import { ChatInput } from '../../components/ChatInput';
import { apiService } from '../../services/api';
import { Message } from '../../types';
import { createScene } from '../../components/ThreeScenePage';

export default function ChatScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const { friends } = useFriends();
  const [messages, setMessages] = useState<Message[]>([]);
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  const containerRef = useRef<any>(null);
  let sceneData: any;

  const friend = friends.find((f) => f.id === id);

  useEffect(() => {
    return sound
      ? () => {
          sound.unloadAsync();
        }
      : undefined;
  }, [sound]);

  useEffect(() => {
    if (!containerRef.current) return

    sceneData = createScene()
    const renderer = sceneData.getRenderer()

    containerRef.current.appendChild(renderer.domElement)

    // Load model
    sceneData.loadModel('/models/preview_model.glb')

    return () => {
      containerRef.current?.removeChild(renderer.domElement)
      sceneData.cleanup()
    }
  }, [])


  if (!friend) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.errorText}>Friend not found</Text>
      </SafeAreaView>
    );
  }

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
          <View
            style={styles.modelWrapper}
            onLayout={(e) => {
              const { width, height } = e.nativeEvent.layout
              // if (sceneData) {
              //   sceneData.resize(width, height)
              // }
            }}
          >
            <div ref={containerRef} style={styles.webCanvas} />
          </View>
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

const MODEL_HEIGHT = Math.round(Dimensions.get('window').width * 0.50);

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
  modelContainer: {
    backgroundColor: '#020617',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.08)',
  },

  modelWrapper: {
    width: '55%',
    height: MODEL_HEIGHT,
    alignSelf: 'center',
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: '#020617',
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
  },

  webCanvas: {
    width: '100%',
    height: '100%',
    display: 'flex',
    justifyContent: 'center',
  },
});