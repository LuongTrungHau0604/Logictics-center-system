export type OrderStatus = 
  | 'pending' 
  | 'assigned' 
  | 'picked' 
  | 'delivering' 
  | 'delivered' 
  | 'failed';

export interface Order {
  id: string;
  orderCode: string;
  senderName?: string;
  senderPhone?: string;
  receiverName?: string;
  receiverPhone?: string;
  pickupAddress: string;
  deliveryAddress?: string;
  distanceKm: number;
  status: OrderStatus;
  eta?: string;
  pickupTime?: string;
  deliveryTime?: string;
  notes?: string;
  failureReason?: string;
  weight?: number;
  packageType?: string;
}

export interface Shift {
  id: string;
  type: 'pickup' | 'delivery';
  startTime: string;
  endTime: string;
  date: string;
  tasksCount: number;
}