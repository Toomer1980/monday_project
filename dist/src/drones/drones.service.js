"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DronesService = void 0;
const common_1 = require("@nestjs/common");
const prisma_service_1 = require("../prisma/prisma.service");
const order_status_enum_1 = require("../common/enums/order-status.enum");
const drone_status_enum_1 = require("../common/enums/drone-status.enum");
let DronesService = class DronesService {
    prisma;
    constructor(prisma) {
        this.prisma = prisma;
    }
    async getDrone(userId) {
        const drone = await this.prisma.drone.findUnique({
            where: { userId },
            include: { currentOrder: true },
        });
        if (!drone) {
            throw new common_1.NotFoundException('Drone not found');
        }
        return drone;
    }
    async reserveJob(userId) {
        const drone = await this.getDrone(userId);
        if (drone.status !== drone_status_enum_1.DroneStatus.AVAILABLE) {
            throw new common_1.BadRequestException('Drone must be available to reserve a job');
        }
        if (drone.currentOrderId) {
            throw new common_1.BadRequestException('Drone already has an active order');
        }
        const availableOrder = await this.prisma.order.findFirst({
            where: {
                OR: [
                    { status: order_status_enum_1.OrderStatus.PENDING },
                    { status: order_status_enum_1.OrderStatus.PENDING_HANDOFF },
                ],
                assignedDroneId: null,
            },
            orderBy: { createdAt: 'asc' },
        });
        if (!availableOrder) {
            return {
                success: false,
                order: null,
                message: 'No available orders',
            };
        }
        const updatedOrder = await this.prisma.order.update({
            where: { id: availableOrder.id },
            data: {
                assignedDroneId: drone.id,
                status: order_status_enum_1.OrderStatus.ASSIGNED,
            },
        });
        await this.prisma.drone.update({
            where: { id: drone.id },
            data: {
                currentOrderId: updatedOrder.id,
                status: drone_status_enum_1.DroneStatus.BUSY,
            },
        });
        return {
            success: true,
            order: updatedOrder,
            message: 'Order reserved successfully',
        };
    }
    async grabOrder(userId, orderId) {
        const drone = await this.getDrone(userId);
        const order = await this.prisma.order.findUnique({
            where: { id: orderId },
        });
        if (!order) {
            throw new common_1.NotFoundException('Order not found');
        }
        if (order.assignedDroneId !== drone.id) {
            throw new common_1.BadRequestException('Order is not assigned to this drone');
        }
        if (order.status !== order_status_enum_1.OrderStatus.ASSIGNED) {
            throw new common_1.BadRequestException('Order must be in ASSIGNED status');
        }
        const updatedOrder = await this.prisma.order.update({
            where: { id: orderId },
            data: {
                status: order_status_enum_1.OrderStatus.PICKED_UP,
                pickedUpAt: new Date(),
            },
        });
        return {
            success: true,
            order: updatedOrder,
            message: 'Order picked up successfully',
        };
    }
    async updateLocation(userId, updateLocationDto) {
        const drone = await this.getDrone(userId);
        await this.prisma.drone.update({
            where: { id: drone.id },
            data: {
                currentLat: updateLocationDto.lat,
                currentLng: updateLocationDto.lng,
            },
        });
        await this.prisma.locationHistory.create({
            data: {
                droneId: drone.id,
                lat: updateLocationDto.lat,
                lng: updateLocationDto.lng,
            },
        });
        if (drone.currentOrderId) {
            const order = await this.prisma.order.findUnique({
                where: { id: drone.currentOrderId },
            });
            if (order && order.status === order_status_enum_1.OrderStatus.PICKED_UP) {
                await this.prisma.order.update({
                    where: { id: drone.currentOrderId },
                    data: { status: order_status_enum_1.OrderStatus.IN_TRANSIT },
                });
            }
        }
        return {
            success: true,
            drone: {
                id: drone.id,
                currentLat: updateLocationDto.lat,
                currentLng: updateLocationDto.lng,
                status: drone.status,
                currentOrderId: drone.currentOrderId,
            },
            message: 'Location updated successfully',
        };
    }
    async markDelivered(userId, orderId) {
        const drone = await this.getDrone(userId);
        const order = await this.prisma.order.findUnique({
            where: { id: orderId },
        });
        if (!order) {
            throw new common_1.NotFoundException('Order not found');
        }
        if (order.assignedDroneId !== drone.id) {
            throw new common_1.BadRequestException('Order is not assigned to this drone');
        }
        await this.prisma.order.update({
            where: { id: orderId },
            data: {
                status: order_status_enum_1.OrderStatus.DELIVERED,
                deliveredAt: new Date(),
            },
        });
        await this.prisma.drone.update({
            where: { id: drone.id },
            data: {
                currentOrderId: null,
                status: drone_status_enum_1.DroneStatus.AVAILABLE,
            },
        });
        return {
            success: true,
            message: 'Order marked as delivered',
        };
    }
    async markFailed(userId, markFailedDto) {
        const drone = await this.getDrone(userId);
        const order = await this.prisma.order.findUnique({
            where: { id: markFailedDto.orderId },
        });
        if (!order) {
            throw new common_1.NotFoundException('Order not found');
        }
        if (order.assignedDroneId !== drone.id) {
            throw new common_1.BadRequestException('Order is not assigned to this drone');
        }
        await this.prisma.order.update({
            where: { id: markFailedDto.orderId },
            data: {
                status: order_status_enum_1.OrderStatus.FAILED,
                failedAt: new Date(),
                failureReason: markFailedDto.reason,
            },
        });
        await this.prisma.drone.update({
            where: { id: drone.id },
            data: {
                currentOrderId: null,
                status: drone_status_enum_1.DroneStatus.AVAILABLE,
            },
        });
        return {
            success: true,
            message: 'Order marked as failed',
        };
    }
    async markBroken(userId, markBrokenDto) {
        const drone = await this.getDrone(userId);
        if (drone.currentOrderId) {
            const order = await this.prisma.order.findUnique({
                where: { id: drone.currentOrderId },
            });
            if (order) {
                await this.prisma.orderHandoff.create({
                    data: {
                        orderId: order.id,
                        fromDroneId: drone.id,
                        handoffLat: drone.currentLat || order.originLat,
                        handoffLng: drone.currentLng || order.originLng,
                        reason: markBrokenDto.reason,
                    },
                });
                await this.prisma.order.update({
                    where: { id: order.id },
                    data: {
                        status: order_status_enum_1.OrderStatus.PENDING_HANDOFF,
                        assignedDroneId: null,
                    },
                });
            }
        }
        await this.prisma.drone.update({
            where: { id: drone.id },
            data: {
                status: drone_status_enum_1.DroneStatus.BROKEN,
                currentOrderId: null,
            },
        });
        return {
            success: true,
            message: 'Drone marked as broken. Order handoff created if applicable.',
        };
    }
    async getCurrentOrder(userId) {
        const drone = await this.getDrone(userId);
        if (!drone.currentOrderId) {
            return {
                hasOrder: false,
                order: null,
                message: 'No active order',
            };
        }
        const order = await this.prisma.order.findUnique({
            where: { id: drone.currentOrderId },
        });
        return {
            hasOrder: true,
            order,
            message: 'Current order retrieved',
        };
    }
};
exports.DronesService = DronesService;
exports.DronesService = DronesService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [prisma_service_1.PrismaService])
], DronesService);
//# sourceMappingURL=drones.service.js.map