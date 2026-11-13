import { OrdersService } from './orders.service';
import { CreateOrderDto } from './dto/create-order.dto';
export declare class OrdersController {
    private ordersService;
    constructor(ordersService: OrdersService);
    create(user: any, createOrderDto: CreateOrderDto): Promise<{
        id: string;
        createdAt: Date;
        updatedAt: Date;
        status: import("@prisma/client").$Enums.OrderStatus;
        orderNumber: string;
        originLat: number;
        originLng: number;
        originAddress: string;
        destinationLat: number;
        destinationLng: number;
        destinationAddress: string;
        pickedUpAt: Date | null;
        deliveredAt: Date | null;
        failedAt: Date | null;
        failureReason: string | null;
        customerId: string;
        assignedDroneId: string | null;
    }>;
    findAll(user: any): Promise<({
        assignedDrone: {
            id: string;
            status: import("@prisma/client").$Enums.DroneStatus;
            currentLat: number | null;
            currentLng: number | null;
        } | null;
    } & {
        id: string;
        createdAt: Date;
        updatedAt: Date;
        status: import("@prisma/client").$Enums.OrderStatus;
        orderNumber: string;
        originLat: number;
        originLng: number;
        originAddress: string;
        destinationLat: number;
        destinationLng: number;
        destinationAddress: string;
        pickedUpAt: Date | null;
        deliveredAt: Date | null;
        failedAt: Date | null;
        failureReason: string | null;
        customerId: string;
        assignedDroneId: string | null;
    })[]>;
    findOne(user: any, id: string): Promise<{
        currentDroneLat: number | null | undefined;
        currentDroneLng: number | null | undefined;
        estimatedTimeMinutes: number | null;
        assignedDrone: {
            id: string;
            status: import("@prisma/client").$Enums.DroneStatus;
            currentLat: number | null;
            currentLng: number | null;
        } | null;
        id: string;
        createdAt: Date;
        updatedAt: Date;
        status: import("@prisma/client").$Enums.OrderStatus;
        orderNumber: string;
        originLat: number;
        originLng: number;
        originAddress: string;
        destinationLat: number;
        destinationLng: number;
        destinationAddress: string;
        pickedUpAt: Date | null;
        deliveredAt: Date | null;
        failedAt: Date | null;
        failureReason: string | null;
        customerId: string;
        assignedDroneId: string | null;
    }>;
    withdraw(user: any, id: string): Promise<{
        id: string;
        createdAt: Date;
        updatedAt: Date;
        status: import("@prisma/client").$Enums.OrderStatus;
        orderNumber: string;
        originLat: number;
        originLng: number;
        originAddress: string;
        destinationLat: number;
        destinationLng: number;
        destinationAddress: string;
        pickedUpAt: Date | null;
        deliveredAt: Date | null;
        failedAt: Date | null;
        failureReason: string | null;
        customerId: string;
        assignedDroneId: string | null;
    }>;
}
