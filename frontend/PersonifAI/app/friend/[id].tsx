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
    sceneData.loadModel(`/models/${id}.glb`)
    console.log("id: ", id)

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

    try {
      console.log("📤 Sending message to backend...");
      const response = await apiService.sendTextMessage(friend.id, text);
      console.log("✅ Backend response:", response);

      if (response && response.results) {
        // Combine all response chunks into one message
        const fullText = response.results
          .map((r: any) => r.clean_text)
          .join(" ")
          .trim();

        console.log("💬 Full AI response text:", fullText);

        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: fullText || `Response from ${friend.name}`,
          isUser: false,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error("❌ Error getting response:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I had an error processing that. Please try again.",
        isUser: false,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleSendVoice = async (audioUri: string) => {
    console.log("🎤 Processing voice message:", audioUri);

    try {
      // Send voice to backend
      const response = await apiService.sendVoiceMessage(friend.id, audioUri);

      if (response && response.transcribed_text) {
        // Add user's transcribed message
        const userMessage: Message = {
          id: Date.now().toString(),
          text: response.transcribed_text,
          isUser: true,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, userMessage]);
        console.log("✅ Added transcribed message:", response.transcribed_text);

        // Add AI response(s)
        if (response.results && Array.isArray(response.results)) {
          const fullText = response.results
            .map((r: any) => r.clean_text)
            .join(" ")
            .trim();

          console.log("💬 Full AI response text:", fullText);

          const aiMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: fullText || `Response from ${friend.name}`,
            isUser: false,
            timestamp: Date.now(),
          };
          setMessages((prev) => [...prev, aiMessage]);
        }
      }
    } catch (error) {
      console.error("❌ Error processing voice message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I had an error processing your voice message. Please try again.",
        isUser: false,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
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
            ref={containerRef}
            style={styles.modelWrapper}
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
});