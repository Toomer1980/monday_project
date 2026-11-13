import { AdminService } from './admin.service';
import { UpdateOrderLocationDto } from './dto/update-order-location.dto';
export declare class AdminController {
    private adminService;
    constructor(adminService: AdminService);
    getAllOrders(): Promise<({
        customer: {
            id: string;
            name: string;
        };
        assignedDrone: {
            id: string;
            serialNumber: string;
            status: import("@prisma/client").$Enums.DroneStatus;
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
    updateOrderOrigin(id: string, updateDto: UpdateOrderLocationDto): Promise<{
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
    updateOrderDestination(id: string, updateDto: UpdateOrderLocationDto): Promise<{
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
    getAllDrones(): Promise<({
        user: {
            id: string;
            name: string;
        };
        currentOrder: {
            id: string;
            status: import("@prisma/client").$Enums.OrderStatus;
            orderNumber: string;
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
    })[]>;
    markDroneBroken(id: string): Promise<{
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
    markDroneFixed(id: string): Promise<{
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
}
