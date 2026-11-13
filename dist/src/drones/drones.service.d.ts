import { PrismaService } from '../prisma/prisma.service';
import { UpdateLocationDto } from './dto/update-location.dto';
import { MarkFailedDto } from './dto/mark-failed.dto';
import { MarkBrokenDto } from './dto/mark-broken.dto';
export declare class DronesService {
    private prisma;
    constructor(prisma: PrismaService);
    getDrone(userId: string): Promise<{
        currentOrder: {
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
        } | null;
    } & {
        id: string;
        createdAt: Date;
        updatedAt: Date;
        serialNumber: string;
        status: import("@prisma/client").$Enums.DroneStatus;
        currentLat: number | null;
        currentLng: number | null;
        batteryLevel: number;
        userId: string;
        currentOrderId: string | null;
    }>;
    reserveJob(userId: string): Promise<{
        success: boolean;
        order: null;
        message: string;
    } | {
        success: boolean;
        order: {
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
        };
        message: string;
    }>;
    grabOrder(userId: string, orderId: string): Promise<{
        success: boolean;
        order: {
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
        };
        message: string;
    }>;
    updateLocation(userId: string, updateLocationDto: UpdateLocationDto): Promise<{
        success: boolean;
        drone: {
            id: string;
            currentLat: number;
            currentLng: number;
            status: import("@prisma/client").$Enums.DroneStatus;
            currentOrderId: string | null;
        };
        message: string;
    }>;
    markDelivered(userId: string, orderId: string): Promise<{
        success: boolean;
        message: string;
    }>;
    markFailed(userId: string, markFailedDto: MarkFailedDto): Promise<{
        success: boolean;
        message: string;
    }>;
    markBroken(userId: string, markBrokenDto: MarkBrokenDto): Promise<{
        success: boolean;
        message: string;
    }>;
    getCurrentOrder(userId: string): Promise<{
        hasOrder: boolean;
        order: {
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
        } | null;
        message: string;
    }>;
}
