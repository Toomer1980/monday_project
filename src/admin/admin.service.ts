import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { UpdateOrderLocationDto } from './dto/update-order-location.dto';
import { DroneStatus } from '../common/enums/drone-status.enum';
import { OrderStatus } from '../common/enums/order-status.enum';

@Injectable()
export class AdminService {
  constructor(private prisma: PrismaService) {}

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

  async updateOrderOrigin(orderId: string, updateDto: UpdateOrderLocationDto) {
    const order = await this.prisma.order.findUnique({
      where: { id: orderId },
    });

    if (!order) {
      throw new NotFoundException('Order not found');
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

  async updateOrderDestination(orderId: string, updateDto: UpdateOrderLocationDto) {
    const order = await this.prisma.order.findUnique({
      where: { id: orderId },
    });

    if (!order) {
      throw new NotFoundException('Order not found');
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

  async markDroneBroken(droneId: string) {
    const drone = await this.prisma.drone.findUnique({
      where: { id: droneId },
      include: { currentOrder: true },
    });

    if (!drone) {
      throw new NotFoundException('Drone not found');
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
          status: OrderStatus.PENDING_HANDOFF,
          assignedDroneId: null,
        },
      });
    }

    return this.prisma.drone.update({
      where: { id: droneId },
      data: {
        status: DroneStatus.BROKEN,
        currentOrderId: null,
      },
    });
  }

  async markDroneFixed(droneId: string) {
    const drone = await this.prisma.drone.findUnique({
      where: { id: droneId },
    });

    if (!drone) {
      throw new NotFoundException('Drone not found');
    }

    return this.prisma.drone.update({
      where: { id: droneId },
      data: {
        status: DroneStatus.AVAILABLE,
      },
    });
  }
}
