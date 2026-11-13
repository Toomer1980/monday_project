import { Injectable, NotFoundException, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateOrderDto } from './dto/create-order.dto';
import { OrderStatus } from '../common/enums/order-status.enum';

@Injectable()
export class OrdersService {
  constructor(private prisma: PrismaService) {}

  async create(userId: string, createOrderDto: CreateOrderDto) {
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
        status: OrderStatus.PENDING,
      },
    });

    return order;
  }

  async findByUser(userId: string) {
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

  async findOne(orderId: string, userId: string) {
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
      throw new NotFoundException('Order not found');
    }

    if (order.customerId !== userId) {
      throw new ForbiddenException('You can only view your own orders');
    }

    
    let estimatedTimeMinutes = null;
    if (order.assignedDrone && order.assignedDrone.currentLat && order.assignedDrone.currentLng) {
      estimatedTimeMinutes = this.calculateETA(
        order.assignedDrone.currentLat,
        order.assignedDrone.currentLng,
        order.destinationLat,
        order.destinationLng,
      );
    }

    return {
      ...order,
      currentDroneLat: order.assignedDrone?.currentLat,
      currentDroneLng: order.assignedDrone?.currentLng,
      estimatedTimeMinutes,
    };
  }

  async withdraw(orderId: string, userId: string) {
    const order = await this.prisma.order.findUnique({
      where: { id: orderId },
    });

    if (!order) {
      throw new NotFoundException('Order not found');
    }

    if (order.customerId !== userId) {
      throw new ForbiddenException('You can only withdraw your own orders');
    }

    if (order.status !== OrderStatus.PENDING) {
      throw new ForbiddenException('Can only withdraw orders that have not been picked up');
    }

    return this.prisma.order.update({
      where: { id: orderId },
      data: { status: OrderStatus.CANCELLED },
    });
  }

  private calculateETA(fromLat: number, fromLng: number, toLat: number, toLng: number): number {
    
    const R = 6371; 
    const dLat = this.toRad(toLat - fromLat);
    const dLon = this.toRad(toLng - fromLng);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRad(fromLat)) * Math.cos(this.toRad(toLat)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;

    
    const speed = 50;
    const timeInHours = distance / speed;
    return Math.round(timeInHours * 60); 
  }

  private toRad(degrees: number): number {
    return degrees * (Math.PI / 180);
  }
}
