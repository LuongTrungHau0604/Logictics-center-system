import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator } from 'react-native';
import { LucideIcon } from 'lucide-react-native';

interface ActionButtonProps {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'success' | 'danger' | 'secondary';
  icon?: LucideIcon;
  loading?: boolean;
  disabled?: boolean;
}

const ActionButton: React.FC<ActionButtonProps> = ({
  label,
  onPress,
  variant = 'primary',
  icon: Icon,
  loading = false,
  disabled = false,
}) => {
  const getVariantBgColor = () => {
    switch (variant) {
      case 'primary':
        return '#2563EB';
      case 'success':
        return '#10B981';
      case 'danger':
        return '#EF4444';
      case 'secondary':
        return '#F3F4F6';
      default:
        return '#2563EB';
    }
  };

  const getTextColor = () => {
    return variant === 'secondary' ? '#111827' : '#FFFFFF';
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={{
        backgroundColor: getVariantBgColor(),
        borderRadius: 12,
        paddingVertical: 16,
        paddingHorizontal: 24,
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        opacity: (disabled || loading) ? 0.5 : 1,
      }}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'secondary' ? '#111827' : '#FFFFFF'} />
      ) : (
        <>
          {Icon && <Icon size={20} {...({ stroke: getTextColor() } as any)} />}
          <Text style={{ color: getTextColor(), fontWeight: '600', fontSize: 16, marginLeft: Icon ? 8 : 0 }}>
            {label}
          </Text>
        </>
      )}
    </TouchableOpacity>
  );
};

export default ActionButton;