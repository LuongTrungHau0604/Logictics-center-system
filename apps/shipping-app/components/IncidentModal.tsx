import React, { useState, useRef, useEffect } from 'react';
import { 
  View, 
  Text, 
  Modal, 
  TextInput, 
  TouchableOpacity, 
  ActivityIndicator, 
  StyleSheet, 
  KeyboardAvoidingView, 
  Platform,
  ScrollView,
  Keyboard,
  TouchableWithoutFeedback
} from 'react-native';
import * as Location from 'expo-location';
import { X, Send } from 'lucide-react-native';
import { reportIncidentAPI } from '@/lib/api'; // Đảm bảo import đúng hàm API

type Message = {
  id: string;
  text: string;
  sender: 'system' | 'user';
};

export default function IncidentModal({ visible, onClose, shipperId }: any) {
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false); // Thay thế loading toàn màn hình
  
  const [messages, setMessages] = useState<Message[]>([]);
  const scrollViewRef = useRef<ScrollView>(null);

  // Reset tin nhắn khi mở lại Modal
  useEffect(() => {
    if (visible && messages.length === 0) {
      setMessages([
        { id: '1', text: 'Chào bạn, bạn đang gặp sự cố gì? (Hỏng xe, tai nạn, tắc đường...)', sender: 'system' }
      ]);
    }
  }, [visible]);

  // Tự động cuộn xuống
  useEffect(() => {
    if (visible) {
      setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
    }
  }, [messages, isTyping, visible]);

  const handleSendReport = async () => {
    if (!inputText.trim()) return;

    const userMsg = inputText;
    setInputText(''); // Xóa ô nhập ngay lập tức
    
    // 1. Hiện tin nhắn user ngay lập tức
    setMessages(prev => [...prev, { id: Date.now().toString(), text: userMsg, sender: 'user' }]);
    
    // 2. Bật trạng thái "AI đang nhập..."
    setIsTyping(true);

    // Không gọi Keyboard.dismiss() để tránh giật màn hình

    try {
      // Lấy vị trí
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setMessages(prev => [...prev, { id: Date.now().toString(), text: '⚠️ Cần quyền vị trí để tìm người cứu hộ.', sender: 'system' }]);
        setIsTyping(false);
        return;
      }
      let location = await Location.getCurrentPositionAsync({});

      // Gọi API
      const data = await reportIncidentAPI(
        shipperId,
        userMsg,
        location.coords.latitude,
        location.coords.longitude
      );

      // 3. Nhận phản hồi từ AI
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        text: data.summary || 'Đã nhận thông tin. Đang điều phối...', 
        sender: 'system' 
      }]);
      
    } catch (error: any) {
      let errText = '❌ Lỗi kết nối.';
      if (error.message) errText = error.message;
      setMessages(prev => [...prev, { id: Date.now().toString(), text: errText, sender: 'system' }]);
    } finally {
      setIsTyping(false); // Tắt bong bóng loading
    }
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.overlay}>
        {/* Vùng bấm ra ngoài để đóng modal (Tùy chọn) */}
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
           <View style={{flex: 1}} /> 
        </TouchableWithoutFeedback>

        <KeyboardAvoidingView 
          behavior={Platform.OS === "ios" ? "padding" : "height"}
          style={styles.keyboardContainer}
          keyboardVerticalOffset={0} 
        >
          <View style={styles.chatBox}>
            
            {/* HEADER */}
            <View style={styles.header}>
              <View style={styles.headerTitleContainer}>
                <View style={styles.onlineDot} />
                <Text style={styles.headerTitle}>Trung tâm Cứu hộ AI</Text>
              </View>
              <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
                <X size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            {/* MESSAGE LIST */}
            <ScrollView 
              ref={scrollViewRef}
              style={styles.messagesList}
              contentContainerStyle={{ paddingBottom: 20, paddingTop: 10 }}
              keyboardShouldPersistTaps="handled"
            >
              {messages.map((msg) => (
                <View 
                  key={msg.id} 
                  style={[
                    styles.messageRow, 
                    msg.sender === 'user' ? styles.userRow : styles.systemRow
                  ]}
                >
                  {msg.sender === 'system' && <Text style={styles.avatar}>🤖</Text>}
                  <View style={[
                    styles.messageBubble, 
                    msg.sender === 'user' ? styles.userBubble : styles.systemBubble
                  ]}>
                    <Text style={[
                      styles.messageText,
                      msg.sender === 'user' ? styles.userText : styles.systemText
                    ]}>
                      {msg.text}
                    </Text>
                  </View>
                </View>
              ))}

              {/* Bong bóng Loading khi AI đang nghĩ */}
              {isTyping && (
                <View style={[styles.messageRow, styles.systemRow]}>
                  <Text style={styles.avatar}>🤖</Text>
                  <View style={[styles.messageBubble, styles.systemBubble, { paddingVertical: 12 }]}>
                    <ActivityIndicator size="small" color="#DC2626" />
                  </View>
                </View>
              )}
            </ScrollView>

            {/* INPUT AREA */}
            <View style={styles.footer}>
              <TextInput
                style={styles.input}
                placeholder="Nhập vấn đề (vd: Hỏng xe)..."
                placeholderTextColor="#9CA3AF"
                value={inputText}
                onChangeText={setInputText}
                onSubmitEditing={handleSendReport} // Bấm Enter trên phím ảo để gửi
              />
              <TouchableOpacity 
                style={[styles.sendBtn, !inputText.trim() && styles.disabledBtn]} 
                onPress={handleSendReport}
                disabled={!inputText.trim() || isTyping}
              >
                <Send size={20} color="white" />
              </TouchableOpacity>
            </View>

          </View>
        </KeyboardAvoidingView>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  keyboardContainer: {
    width: '100%',
    height: '75%', // Tăng chiều cao lên để nhìn thoải mái hơn
  },
  chatBox: {
    flex: 1,
    backgroundColor: '#F3F4F6', // Màu nền xám nhẹ dịu mắt
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 10,
    overflow: 'hidden'
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#10B981', // Chấm xanh online
    marginRight: 8,
  },
  headerTitle: {
    fontWeight: '700',
    fontSize: 16,
    color: '#111827',
  },
  closeBtn: {
    padding: 4,
    backgroundColor: '#F3F4F6',
    borderRadius: 20,
  },
  messagesList: {
    flex: 1,
    paddingHorizontal: 16,
  },
  messageRow: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-end',
  },
  userRow: {
    justifyContent: 'flex-end',
  },
  systemRow: {
    justifyContent: 'flex-start',
  },
  avatar: {
    fontSize: 24,
    marginRight: 8,
    marginBottom: 4,
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 14,
    borderRadius: 20,
  },
  systemBubble: {
    backgroundColor: 'white',
    borderBottomLeftRadius: 4,
  },
  userBubble: {
    backgroundColor: '#DC2626', // Màu đỏ chủ đạo của app
    borderBottomRightRadius: 4,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
  },
  systemText: {
    color: '#1F2937',
  },
  userText: {
    color: 'white',
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: 'white',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  input: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    marginRight: 12,
    color: '#1F2937',
  },
  sendBtn: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#DC2626',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: "#DC2626",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
    elevation: 3,
  },
  disabledBtn: {
    backgroundColor: '#D1D5DB',
    shadowOpacity: 0,
    elevation: 0,
  }
});