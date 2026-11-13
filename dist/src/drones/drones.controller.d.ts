import { DronesService } from './drones.service';
import { UpdateLocationDto } from './dto/update-location.dto';
import { GrabOrderDto } from './dto/grab-order.dto';
import { MarkDeliveredDto } from './dto/mark-delivered.dto';
import { MarkFailedDto } from './dto/mark-failed.dto';
import { MarkBrokenDto } from './dto/mark-broken.dto';
export declare class DronesController {
    private dronesService;
    constructor(dronesService: DronesService);
    reserveJob(user: any): Promise<{
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
    grabOrder(user: any, grabOrderDto: GrabOrderDto): Promise<{
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
    updateLocation(user: any, updateLocationDto: UpdateLocationDto): Promise<{
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
    markDelivered(user: any, markDeliveredDto: MarkDeliveredDto): Promise<{
        success: boolean;
        message: string;
    }>;
    markFailed(user: any, markFailedDto: MarkFailedDto): Promise<{
        success: boolean;
        message: string;
    }>;
    markBroken(user: any, markBrokenDto: MarkBrokenDto): Promise<{
        success: boolean;
        message: string;
    }>;
    getCurrentOrder(user: any): Promise<{
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
