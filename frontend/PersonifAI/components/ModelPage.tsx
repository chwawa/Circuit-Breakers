import React, { useEffect, useRef } from 'react';
import { View, Modal, StyleSheet, Dimensions, Text } from 'react-native';
import { createScene } from './ThreeScenePage';

interface ThreeSceneModalProps {
  visible: boolean;
  onClose: () => void;
}

const ModelPage: React.FC<ThreeSceneModalProps> = ({ visible, onClose }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  let sceneData: any;

  useEffect(() => {
    if (visible && containerRef.current) {
      sceneData = createScene();
      const renderer = sceneData.getRenderer();
      containerRef.current.appendChild(renderer.domElement);

      // Example: Load a model when the modal is visible
      sceneData.loadModel('/models/preview_model.glb');

      return () => {
        if (containerRef.current) {
          containerRef.current.removeChild(renderer.domElement);
        }
        sceneData.cleanup(); // Cleanup event listeners and renderer
      };
    }
  }, [visible]);

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalContent}>
          <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
        </View>
        <View style={styles.closeButton} onTouchEnd={onClose}>
          <Text style={styles.closeButtonText}>Close</Text>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
  },
  modalContent: {
    width: Dimensions.get('window').width * 0.9,
    height: Dimensions.get('window').height * 0.8,
    backgroundColor: '#000',
  },
  closeButton: {
    marginTop: 20,
    padding: 10,
    backgroundColor: '#9333ea',
    borderRadius: 5,
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
  },
});

export default ModelPage;
