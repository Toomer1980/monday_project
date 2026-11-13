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
exports.AdminService = void 0;
const common_1 = require("@nestjs/common");
const prisma_service_1 = require("../prisma/prisma.service");
const drone_status_enum_1 = require("../common/enums/drone-status.enum");
const order_status_enum_1 = require("../common/enums/order-status.enum");
let AdminService = class AdminService {
    prisma;
    constructor(prisma) {
        this.prisma = prisma;
    }
    async getAllOrders() {
        return this.prisma.order.findMany({
            include: {
                customer: {
                    select: {
                        id: true,
                        name: true,
                    },
                },
                assignedDrone: {
                    select: {
                        id: true,
                        serialNumber: true,
                        status: true,
                    },
                },
            },
            orderBy: { createdAt: 'desc' },
        });
    }
    async updateOrderOrigin(orderId, updateDto) {
        const order = await this.prisma.order.findUnique({
            where: { id: orderId },
        });
        if (!order) {
            throw new common_1.NotFoundException('Order not found');
        }
        return this.prisma.order.update({
            where: { id: orderId },
            data: {
                ...(updateDto.lat !== undefined && { originLat: updateDto.lat }),
                ...(updateDto.lng !== undefined && { originLng: updateDto.lng }),
                ...(updateDto.address && { originAddress: updateDto.address }),
            },
        });
    }
    async updateOrderDestination(orderId, updateDto) {
        const order = await this.prisma.order.findUnique({
            where: { id: orderId },
        });
        if (!order) {
            throw new common_1.NotFoundException('Order not found');
        }
        return this.prisma.order.update({
            where: { id: orderId },
            data: {
                ...(updateDto.lat !== undefined && { destinationLat: updateDto.lat }),
                ...(updateDto.lng !== undefined && { destinationLng: updateDto.lng }),
                ...(updateDto.address && { destinationAddress: updateDto.address }),
            },
        });
    }
    async getAllDrones() {
        return this.prisma.drone.findMany({
            include: {
                user: {
                    select: {
                        id: true,
                        name: true,
                    },
                },
                currentOrder: {
                    select: {
                        id: true,
                        orderNumber: true,
                        status: true,
                    },
                },
            },
            orderBy: { createdAt: 'desc' },
        });
    }
    async markDroneBroken(droneId) {
        const drone = await this.prisma.drone.findUnique({
            where: { id: droneId },
            include: { currentOrder: true },
        });
        if (!drone) {
            throw new common_1.NotFoundException('Drone not found');
        }
        if (drone.currentOrderId && drone.currentOrder) {
            await this.prisma.orderHandoff.create({
                data: {
                    orderId: drone.currentOrder.id,
                    fromDroneId: drone.id,
                    handoffLat: drone.currentLat || drone.currentOrder.originLat,
                    handoffLng: drone.currentLng || drone.currentOrder.originLng,
                    reason: 'Admin marked as broken',
                },
            });
            await this.prisma.order.update({
                where: { id: drone.currentOrder.id },
                data: {
                    status: order_status_enum_1.OrderStatus.PENDING_HANDOFF,
                    assignedDroneId: null,
                },
            });
        }
        return this.prisma.drone.update({
            where: { id: droneId },
            data: {
                status: drone_status_enum_1.DroneStatus.BROKEN,
                currentOrderId: null,
            },
        });
    }
    async markDroneFixed(droneId) {
        const drone = await this.prisma.drone.findUnique({
            where: { id: droneId },
        });
        if (!drone) {
            throw new common_1.NotFoundException('Drone not found');
        }
        return this.prisma.drone.update({
            where: { id: droneId },
            data: {
                status: drone_status_enum_1.DroneStatus.AVAILABLE,
            },
        });
    }
};
exports.AdminService = AdminService;
exports.AdminService = AdminService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [prisma_service_1.PrismaService])
], AdminService);
//# sourceMappingURL=admin.service.js.map