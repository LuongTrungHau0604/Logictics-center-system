import React from 'react';
import { View, Text, Modal, TouchableOpacity, Pressable } from 'react-native';
import { Package, X, CheckCircle2 } from 'lucide-react-native';

interface ScanConfirmModalProps {
  visible: boolean;
  orderCode: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ScanConfirmModal: React.FC<ScanConfirmModalProps> = ({
  visible,
  orderCode,
  onConfirm,
  onCancel,
}) => {
  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onCancel}
    >
      <Pressable 
        style={{ flex: 1, backgroundColor: 'rgba(0, 0, 0, 0.5)', justifyContent: 'center', alignItems: 'center', paddingHorizontal: 24 }}
        onPress={onCancel}
      >
        <Pressable 
          style={{ backgroundColor: '#fff', borderRadius: 16, padding: 24, width: '100%', maxWidth: 320 }}
          onPress={() => {}}
        >
          {/* Close Button */}
          <TouchableOpacity
            onPress={onCancel}
            style={{ position: 'absolute', top: 16, right: 16, zIndex: 10 }}
          >
            <X size={24} {...({ stroke: '#6B7280' } as any)} />
          </TouchableOpacity>

          {/* Icon */}
          <View style={{ alignItems: 'center', marginBottom: 16 }}>
            <View style={{ backgroundColor: '#DBEAFE', borderRadius: 50, padding: 16, marginBottom: 12 }}>
              <Package size={40} {...({ stroke: '#2563EB' } as any)} />
            </View>
            <Text style={{ fontSize: 20, fontWeight: '700', color: '#111827', marginBottom: 8 }}>
              Package Scanned
            </Text>
          </View>

          {/* Order Code */}
          <View style={{ backgroundColor: '#F9FAFB', borderRadius: 8, padding: 16, marginBottom: 24 }}>
            <Text style={{ fontSize: 14, color: '#4B5563', marginBottom: 4 }}>Order Code</Text>
            <Text style={{ fontSize: 28, fontWeight: '700', color: '#2563EB' }}>
              {orderCode}
            </Text>
          </View>

          {/* Message */}
          <Text style={{ textAlign: 'center', color: '#374151', marginBottom: 24 }}>
            Confirm that you have picked up this package?
          </Text>

          {/* Actions */}
          <View style={{ gap: 12 }}>
            <TouchableOpacity
              onPress={onConfirm}
              style={{ backgroundColor: '#2563EB', borderRadius: 12, paddingVertical: 16, flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}
              activeOpacity={0.8}
            >
              <CheckCircle2 size={20} {...({ stroke: '#FFFFFF' } as any)} />
              <Text style={{ color: '#fff', fontWeight: '600', fontSize: 16, marginLeft: 8 }}>
                Confirm Pickup
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={onCancel}
              style={{ backgroundColor: '#F3F4F6', borderRadius: 12, paddingVertical: 16 }}
              activeOpacity={0.8}
            >
              <Text style={{ color: '#374151', fontWeight: '600', fontSize: 16, textAlign: 'center' }}>
                Cancel
              </Text>
            </TouchableOpacity>
          </View>
        </Pressable>
      </Pressable>
    </Modal>
  );
};

export default ScanConfirmModal;