import { Order, Shift } from './types';

export const pickupTasks: Order[] = [
  {
    id: '1',
    orderCode: 'PKG-2024-001',
    senderName: 'Nguyen Van A',
    senderPhone: '+84 901 234 567',
    pickupAddress: '123 Le Loi St, District 1, HCMC',
    distanceKm: 2.5,
    status: 'assigned',
    pickupTime: '09:00 AM',
    weight: 5.2,
    packageType: 'Box',
    notes: 'Fragile items - Handle with care'
  },
  {
    id: '2',
    orderCode: 'PKG-2024-002',
    senderName: 'Tran Thi B',
    senderPhone: '+84 902 345 678',
    pickupAddress: '456 Nguyen Hue Blvd, District 1, HCMC',
    distanceKm: 3.8,
    status: 'assigned',
    pickupTime: '10:30 AM',
    weight: 2.1,
    packageType: 'Envelope',
    notes: 'Documents - Keep dry'
  },
  {
    id: '3',
    orderCode: 'PKG-2024-003',
    senderName: 'Le Van C',
    senderPhone: '+84 903 456 789',
    pickupAddress: '789 Hai Ba Trung St, District 3, HCMC',
    distanceKm: 5.2,
    status: 'pending',
    pickupTime: '11:00 AM',
    weight: 8.5,
    packageType: 'Box',
    notes: 'Electronics - Signature required'
  },
  {
    id: '4',
    orderCode: 'PKG-2024-004',
    senderName: 'Pham Thi D',
    senderPhone: '+84 904 567 890',
    pickupAddress: '321 Vo Van Tan St, District 3, HCMC',
    distanceKm: 1.9,
    status: 'picked',
    pickupTime: '08:30 AM',
    weight: 3.2,
    packageType: 'Bag',
    notes: 'Fashion items'
  }
];

export const deliveryTasks: Order[] = [
  {
    id: '5',
    orderCode: 'DEL-2024-001',
    senderName: 'Hoang Van E',
    receiverName: 'Nguyen Thi F',
    receiverPhone: '+84 905 678 901',
    pickupAddress: '111 Pasteur St, District 1, HCMC',
    deliveryAddress: '222 Nguyen Trai St, District 5, HCMC',
    distanceKm: 4.3,
    status: 'picked',
    eta: '2:30 PM',
    weight: 4.5,
    packageType: 'Box',
    notes: 'Birthday gift - Deliver before 3 PM'
  },
  {
    id: '6',
    orderCode: 'DEL-2024-002',
    senderName: 'Dang Van G',
    receiverName: 'Tran Van H',
    receiverPhone: '+84 906 789 012',
    pickupAddress: '333 Tran Hung Dao St, District 1, HCMC',
    deliveryAddress: '444 Cach Mang Thang Tam St, District 10, HCMC',
    distanceKm: 6.8,
    status: 'delivering',
    eta: '3:15 PM',
    weight: 7.2,
    packageType: 'Box',
    notes: 'Office supplies'
  },
  {
    id: '7',
    orderCode: 'DEL-2024-003',
    senderName: 'Vu Van J',
    receiverName: 'Le Thi I',
    receiverPhone: '+84 907 890 123',
    pickupAddress: '555 Ly Thuong Kiet St, District 5, HCMC',
    deliveryAddress: '555 Le Hong Phong St, District 5, HCMC',
    distanceKm: 3.5,
    status: 'picked',
    eta: '4:00 PM',
    weight: 2.8,
    packageType: 'Envelope',
    notes: 'Legal documents - ID verification required'
  }
];

export const historyTasks: Order[] = [
  {
    id: '8',
    orderCode: 'HIS-2024-001',
    senderName: 'Vu Van J',
    receiverName: 'Phan Thi K',
    receiverPhone: '+84 908 901 234',
    pickupAddress: '666 Dien Bien Phu St, District 3, HCMC',
    deliveryAddress: '777 Ba Thang Hai St, District 10, HCMC',
    distanceKm: 5.5,
    status: 'delivered',
    pickupTime: '08:00 AM',
    deliveryTime: '09:45 AM',
    weight: 6.3,
    packageType: 'Box'
  },
  {
    id: '9',
    orderCode: 'HIS-2024-002',
    senderName: 'Bui Van L',
    receiverName: 'Do Thi M',
    receiverPhone: '+84 909 012 345',
    pickupAddress: '888 Ly Thai To St, District 10, HCMC',
    deliveryAddress: '999 Nguyen Dinh Chieu St, District 3, HCMC',
    distanceKm: 4.2,
    status: 'delivered',
    pickupTime: '10:00 AM',
    deliveryTime: '11:30 AM',
    weight: 3.7,
    packageType: 'Bag'
  },
  {
    id: '10',
    orderCode: 'HIS-2024-003',
    senderName: 'Ngo Van N',
    receiverName: 'Truong Thi O',
    receiverPhone: '+84 910 123 456',
    pickupAddress: '101 Nguyen Van Cu St, District 5, HCMC',
    deliveryAddress: '202 Hoang Van Thu St, Tan Binh District, HCMC',
    distanceKm: 7.8,
    status: 'failed',
    pickupTime: '01:00 PM',
    deliveryTime: '02:45 PM',
    failureReason: 'Receiver not available - No answer at door',
    weight: 5.1,
    packageType: 'Box'
  },
  {
    id: '11',
    orderCode: 'HIS-2024-004',
    senderName: 'Bui Van L',
    receiverName: 'Cao Van P',
    receiverPhone: '+84 911 234 567',
    pickupAddress: '202 Hoang Van Thu St, Tan Binh District, HCMC',
    deliveryAddress: '303 Vo Thi Sau St, District 3, HCMC',
    distanceKm: 2.9,
    status: 'delivered',
    pickupTime: '02:30 PM',
    deliveryTime: '03:15 PM',
    weight: 1.8,
    packageType: 'Envelope'
  },
  {
    id: '12',
    orderCode: 'HIS-2024-005',
    senderName: 'Ngo Van N',
    receiverName: 'Ly Thi Q',
    receiverPhone: '+84 912 345 678',
    pickupAddress: '101 Nguyen Van Cu St, District 5, HCMC',
    deliveryAddress: '404 Phan Xich Long St, Phu Nhuan District, HCMC',
    distanceKm: 6.3,
    status: 'failed',
    pickupTime: '11:00 AM',
    deliveryTime: '12:30 PM',
    failureReason: 'Wrong address - Building does not exist',
    weight: 4.2,
    packageType: 'Box'
  }
];

export const scheduleData: Shift[] = [
  {
    id: 's1',
    type: 'pickup',
    startTime: '08:00 AM',
    endTime: '12:00 PM',
    date: '2024-11-15',
    tasksCount: 8
  },
  {
    id: 's2',
    type: 'delivery',
    startTime: '01:00 PM',
    endTime: '06:00 PM',
    date: '2024-11-15',
    tasksCount: 12
  },
  {
    id: 's3',
    type: 'pickup',
    startTime: '08:00 AM',
    endTime: '12:00 PM',
    date: '2024-11-16',
    tasksCount: 6
  },
  {
    id: 's4',
    type: 'delivery',
    startTime: '01:00 PM',
    endTime: '06:00 PM',
    date: '2024-11-16',
    tasksCount: 10
  }
];