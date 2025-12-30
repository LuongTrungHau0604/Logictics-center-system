import React from 'react';
import { View, Text } from 'react-native';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  rightComponent?: React.ReactNode;
}

const SectionHeader: React.FC<SectionHeaderProps> = ({ 
  title, 
  subtitle, 
  rightComponent 
}) => {
  return (
    <View style={{ marginBottom: 16 }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <View style={{ flex: 1 }}>
          <Text style={{ fontSize: 24, fontWeight: '700', color: '#111827' }}>{title}</Text>
          {subtitle && (
            <Text style={{ fontSize: 14, color: '#4B5563', marginTop: 4 }}>{subtitle}</Text>
          )}
        </View>
        {rightComponent}
      </View>
    </View>
  );
};

export default SectionHeader;