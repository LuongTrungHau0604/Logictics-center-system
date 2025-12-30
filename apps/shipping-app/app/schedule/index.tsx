import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react-native';
import ShiftCard from '@/components/ShiftCard';
import { scheduleData } from '@/lib/mockOrders';

export default function ScheduleScreen() {
  const [selectedDate, setSelectedDate] = useState('2024-11-15');

  // Mock week days
  const weekDays = [
    { date: '2024-11-11', day: 'Mon', dayNum: 11 },
    { date: '2024-11-12', day: 'Tue', dayNum: 12 },
    { date: '2024-11-13', day: 'Wed', dayNum: 13 },
    { date: '2024-11-14', day: 'Thu', dayNum: 14 },
    { date: '2024-11-15', day: 'Fri', dayNum: 15 },
    { date: '2024-11-16', day: 'Sat', dayNum: 16 },
    { date: '2024-11-17', day: 'Sun', dayNum: 17 },
  ];

  const todayShifts = scheduleData.filter(s => s.date === selectedDate);
  const totalTasks = todayShifts.reduce((sum, shift) => sum + shift.tasksCount, 0);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {/* Month Navigation */}
        <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <TouchableOpacity style={{ padding: 8 }} activeOpacity={0.7}>
            <ChevronLeft size={24} {...({ stroke: '#6B7280' } as any)} />
          </TouchableOpacity>
          
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Calendar size={20} {...({ stroke: '#2563EB' } as any)} />
            <Text style={{ fontSize: 18, fontWeight: '700', color: '#111827', marginLeft: 8 }}>
              November 2024
            </Text>
          </View>

          <TouchableOpacity style={{ padding: 8 }} activeOpacity={0.7}>
            <ChevronRight size={24} {...({ stroke: '#6B7280' } as any)} />
          </TouchableOpacity>
        </View>

        {/* Week View */}
        <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 16 }}>
          <Text style={{ fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 12 }}>
            This Week
          </Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              {weekDays.map((day) => {
                const isSelected = selectedDate === day.date;
                const isToday = day.date === '2024-11-15';
                let backgroundColor = '#f3f4f6';
                let borderColor = 'transparent';
                let dayTextColor = '#4b5563';
                let numberColor = '#111827';
                
                if (isSelected) {
                  backgroundColor = '#2563EB';
                  dayTextColor = '#fff';
                  numberColor = '#fff';
                } else if (isToday) {
                  backgroundColor = '#eff6ff';
                  borderColor = '#2563EB';
                  dayTextColor = '#2563EB';
                  numberColor = '#2563EB';
                }
                
                return (
                  <TouchableOpacity
                    onPress={() => setSelectedDate(day.date)}
                    style={{ alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12, borderRadius: 12, minWidth: 70, backgroundColor, borderWidth: isToday && !isSelected ? 1 : 0, borderColor }}
                    activeOpacity={0.7}
                  >
                    <Text style={{ fontSize: 12, marginBottom: 4, color: dayTextColor, fontWeight: isToday && !isSelected ? '600' : '400' }}>
                      {day.day}
                    </Text>
                    <Text style={{ fontSize: 20, fontWeight: '700', color: numberColor }}>
                      {day.dayNum}
                    </Text>
                    {isToday && !isSelected && (
                      <View style={{ width: 6, height: 6, backgroundColor: '#2563EB', borderRadius: 3, marginTop: 4 }} />
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>
          </ScrollView>
        </View>

        {/* Daily Summary */}
        <View style={{ borderRadius: 12, padding: 24, marginBottom: 16, backgroundColor: '#2563EB' }}>
          <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 14, marginBottom: 4 }}>
            {selectedDate === '2024-11-15' ? 'Today' : 'Selected Date'}
          </Text>
          <Text style={{ color: '#fff', fontSize: 32, fontWeight: '700', marginBottom: 16 }}>
            {totalTasks} Tasks
          </Text>
          <View style={{ flexDirection: 'row' }}>
            <View style={{ backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 8, paddingHorizontal: 16, paddingVertical: 8, marginRight: 12 }}>
              <Text style={{ color: '#fff', fontSize: 12 }}>
                {todayShifts.length} Shifts
              </Text>
            </View>
            {selectedDate === '2024-11-15' && (
              <View style={{ backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 8, paddingHorizontal: 16, paddingVertical: 8 }}>
                <Text style={{ color: '#fff', fontSize: 12 }}>Active</Text>
              </View>
            )}
          </View>
        </View>

        {/* Shifts List */}
        <View style={{ marginBottom: 16 }}>
          <Text style={{ fontSize: 18, fontWeight: '700', color: '#111827', marginBottom: 12 }}>
            Shifts for {selectedDate === '2024-11-15' ? 'Today' : 'Selected Day'}
          </Text>
          
          {todayShifts.length > 0 ? (
            todayShifts.map((shift) => (
              <ShiftCard shift={shift} />
            ))
          ) : (
            <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 32, alignItems: 'center' }}>
              <Text style={{ color: '#9ca3af', textAlign: 'center' }}>
                No shifts scheduled for this day
              </Text>
            </View>
          )}
        </View>

        {/* Weekly Summary */}
        <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 24, marginBottom: 24 }}>
          <Text style={{ fontSize: 18, fontWeight: '700', color: '#111827', marginBottom: 16 }}>
            Weekly Summary
          </Text>
          
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 }}>
            <Text style={{ color: '#374151' }}>Total Shifts:</Text>
            <Text style={{ fontWeight: '600', color: '#111827' }}>
              {scheduleData.length}
            </Text>
          </View>
          
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 }}>
            <Text style={{ color: '#374151' }}>Total Tasks:</Text>
            <Text style={{ fontWeight: '600', color: '#111827' }}>
              {scheduleData.reduce((sum, s) => sum + s.tasksCount, 0)}
            </Text>
          </View>
          
          <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
            <Text style={{ color: '#374151' }}>Avg Tasks/Shift:</Text>
            <Text style={{ fontWeight: '600', color: '#111827' }}>
              {Math.round(
                scheduleData.reduce((sum, s) => sum + s.tasksCount, 0) / 
                scheduleData.length
              )}
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}