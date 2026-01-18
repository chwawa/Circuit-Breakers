import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Modal,
  StyleSheet,
  Image,
  Alert,
  Platform
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { apiService } from '../services/api';

interface CreateFriendModalProps {
  visible: boolean;
  onClose: () => void;
  onCreateFriend: (friend: any) => void;
}

export const CreateFriendModal: React.FC<CreateFriendModalProps> = ({
  visible,
  onClose,
  onCreateFriend,
}) => {
  const [name, setName] = useState('');
  const [personality, setPersonality] = useState('');
  const [imageUri, setImageUri] = useState<string | null>(null);

  const [cameraPermission, requestCameraPermission] =
  ImagePicker.useCameraPermissions();

  const [libraryPermission, requestLibraryPermission] =
  ImagePicker.useMediaLibraryPermissions();

  const pickImage = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (!permissionResult.granted) {
      Alert.alert('Permission needed', 'Please allow access to photos');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Camera permission denied');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });

    console.log('Camera result:', result);

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  };

  const handleCreate = async () => {
    if (!name || !imageUri) {
      Alert.alert('Missing info', 'Please add a name and photo');
      return;
    }

    const result = await apiService.createFriend(imageUri, name, personality);

    // Reset form
    handleClose();

    const newFriend = {
      id: result.friendId,
      name,
      personality,
      imageUrl: imageUri,
      isProcessing: true,
      createdAt: Date.now(),
      modelUrl: result.modelUrl,
    };

    onCreateFriend(newFriend);

    // Add to friends list


    console.log('Created friend:', newFriend);
    
  };

  const handleClose = () => {
    setName('');
    setPersonality('');
    setImageUri(null);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>Create New Friend</Text>

          <View style={styles.imageSection}>
            <Text style={styles.label}>Photo</Text>
            <TouchableOpacity
              onPress={() => {
                if (Platform.OS === 'web') {
                  pickImage(); // web should go straight to file picker
                } else {
                  Alert.alert('Choose Photo', 'Select photo source', [
                    { text: 'Camera', onPress: takePhoto },
                    { text: 'Gallery', onPress: pickImage },
                    { text: 'Cancel', style: 'cancel' },
                  ]);
                }
              }}
              style={styles.imagePicker}
            >
              {imageUri ? (
                <Image source={{ uri: imageUri }} style={styles.selectedImage} />
              ) : (
                <View style={styles.imagePickerContent}>
                  <Text style={styles.imagePickerText}>📷</Text>
                  <Text style={styles.imagePickerLabel}>Take or Upload Photo</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>

          <View style={styles.inputSection}>
            <Text style={styles.label}>Name</Text>
            <TextInput
              value={name}
              onChangeText={setName}
              placeholder="Enter friend's name"
              placeholderTextColor="rgba(255, 255, 255, 0.5)"
              style={styles.input}
            />
          </View>

          <View style={styles.inputSection}>
            <Text style={styles.label}>Personality (Optional)</Text>
            <TextInput
              value={personality}
              onChangeText={setPersonality}
              placeholder="Describe their personality..."
              placeholderTextColor="rgba(255, 255, 255, 0.5)"
              style={[styles.input, styles.textArea]}
              multiline
              numberOfLines={3}
            />
          </View>

          <View style={styles.buttons}>
            <TouchableOpacity onPress={handleClose} style={styles.cancelButton}>
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={handleCreate}
              disabled={!name || !imageUri}
              style={[styles.createButton, (!name || !imageUri) && styles.buttonDisabled]}
            >
              <Text style={styles.createButtonText}>Create</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    padding: 24,
  },
  modalContent: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(168, 85, 247, 0.3)',
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 24,
  },
  imageSection: {
    marginBottom: 24,
  },
  label: {
    color: '#d8b4fe',
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
  },
  imagePicker: {
    aspectRatio: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: 'rgba(168, 85, 247, 0.5)',
    overflow: 'hidden',
  },
  imagePickerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
  },
  imagePickerText: {
    fontSize: 48,
  },
  imagePickerLabel: {
    color: '#d8b4fe',
    fontSize: 16,
  },
  selectedImage: {
    width: '100%',
    height: '100%',
  },
  inputSection: {
    marginBottom: 16,
  },
  input: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 8,
    padding: 12,
    color: 'white',
    fontSize: 16,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  buttons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
  createButton: {
    flex: 1,
    backgroundColor: '#9333ea',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  createButtonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
});