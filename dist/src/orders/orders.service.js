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
exports.OrdersService = void 0;
const common_1 = require("@nestjs/common");
const prisma_service_1 = require("../prisma/prisma.service");
const order_status_enum_1 = require("../common/enums/order-status.enum");
let OrdersService = class OrdersService {
    prisma;
    constructor(prisma) {
        this.prisma = prisma;
    }
    async create(userId, createOrderDto) {
        const orderNumber = `ORD-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const order = await this.prisma.order.create({
            data: {
                orderNumber,
                customerId: userId,
                originLat: createOrderDto.originLat,
                originLng: createOrderDto.originLng,
                originAddress: createOrderDto.originAddress,
                destinationLat: createOrderDto.destinationLat,
                destinationLng: createOrderDto.destinationLng,
                destinationAddress: createOrderDto.destinationAddress,
                status: order_status_enum_1.OrderStatus.PENDING,
            },
        });
        return order;
    }
    async findByUser(userId) {
        return this.prisma.order.findMany({
            where: { customerId: userId },
            include: {
                assignedDrone: {
                    select: {
                        id: true,
                        currentLat: true,
                        currentLng: true,
                        status: true,
                    },
                },
            },
            orderBy: { createdAt: 'desc' },
        });
    }
    async findOne(orderId, userId) {
        const order = await this.prisma.order.findUnique({
            where: { id: orderId },
            include: {
                assignedDrone: {
                    select: {
                        id: true,
                        currentLat: true,
                        currentLng: true,
                        status: true,
                    },
                },
            },
        });
        if (!order) {
            throw new common_1.NotFoundException('Order not found');
        }
        if (order.customerId !== userId) {
            throw new common_1.ForbiddenException('You can only view your own orders');
        }
        let estimatedTimeMinutes = null;
        if (order.assignedDrone && order.assignedDrone.currentLat && order.assignedDrone.currentLng) {
            estimatedTimeMinutes = this.calculateETA(order.assignedDrone.currentLat, order.assignedDrone.currentLng, order.destinationLat, order.destinationLng);
        }
        return {
            ...order,
            currentDroneLat: order.assignedDrone?.currentLat,
            currentDroneLng: order.assignedDrone?.currentLng,
            estimatedTimeMinutes,
        };
    }
    async withdraw(orderId, userId) {
        const order = await this.prisma.order.findUnique({
            where: { id: orderId },
        });
        if (!order) {
            throw new common_1.NotFoundException('Order not found');
        }
        if (order.customerId !== userId) {
            throw new common_1.ForbiddenException('You can only withdraw your own orders');
        }
        if (order.status !== order_status_enum_1.OrderStatus.PENDING) {
            throw new common_1.ForbiddenException('Can only withdraw orders that have not been picked up');
        }
        return this.prisma.order.update({
            where: { id: orderId },
            data: { status: order_status_enum_1.OrderStatus.CANCELLED },
        });
    }
    calculateETA(fromLat, fromLng, toLat, toLng) {
        const R = 6371;
        const dLat = this.toRad(toLat - fromLat);
        const dLon = this.toRad(toLng - fromLng);
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(this.toRad(fromLat)) * Math.cos(this.toRad(toLat)) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const distance = R * c;
        const speed = 50;
        const timeInHours = distance / speed;
        return Math.round(timeInHours * 60);
    }
    toRad(degrees) {
        return degrees * (Math.PI / 180);
    }
};
exports.OrdersService = OrdersService;
exports.OrdersService = OrdersService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [prisma_service_1.PrismaService])
], OrdersService);
//# sourceMappingURL=orders.service.js.map