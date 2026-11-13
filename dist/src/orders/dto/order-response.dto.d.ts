import { OrderStatus } from '../../common/enums/order-status.enum';
export declare class OrderResponseDto {
    id: string;
    orderNumber: string;
    status: OrderStatus;
    originLat: number;
    originLng: number;
    originAddress: string;
    destinationLat: number;
    destinationLng: number;
    destinationAddress: string;
    currentDroneLat?: number;
    currentDroneLng?: number;
    estimatedTimeMinutes?: number;
    createdAt: Date;
}
