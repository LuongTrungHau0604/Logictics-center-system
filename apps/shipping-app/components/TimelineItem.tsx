import React from 'react';
import { View, Text } from 'react-native';
import { LucideIcon } from 'lucide-react-native';

interface TimelineItemProps {
  icon: LucideIcon;
  title: string;
  description: string;
  time?: string;
  isActive: boolean;
  isLast?: boolean;
}

const TimelineItem: React.FC<TimelineItemProps> = ({
  icon: Icon,
  title,
  description,
  time,
  isActive,
  isLast = false,
}) => {
  return (
    <View style={{ flexDirection: 'row' }}>
      {/* Timeline Line */}
      <View style={{ alignItems: 'center', marginRight: 16 }}>
        <View
          style={{
            width: 40,
            height: 40,
            borderRadius: 20,
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: isActive ? '#2563EB' : '#E5E7EB',
          }}
        >
          <Icon size={20} {...({ stroke: isActive ? '#FFFFFF' : '#9CA3AF' } as any)} />
        </View>
        {!isLast && (
          <View style={{ width: 2, flex: 1, marginVertical: 4, backgroundColor: isActive ? '#2563EB' : '#E5E7EB' }} />
        )}
      </View>

      {/* Content */}
      <View style={{ flex: 1, paddingBottom: 24 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
          <Text style={{ fontSize: 16, fontWeight: '600', color: isActive ? '#111827' : '#6B7280' }}>
            {title}
          </Text>
          {time && (
            <Text style={{ fontSize: 12, color: '#6B7280' }}>{time}</Text>
          )}
        </View>
        <Text style={{ fontSize: 14, color: '#4B5563' }}>{description}</Text>
      </View>
    </View>
  );
};

export default TimelineItem;