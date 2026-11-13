import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { OrderStatus } from '../common/enums/order-status.enum';
import { DroneStatus } from '../common/enums/drone-status.enum';
import { UpdateLocationDto } from './dto/update-location.dto';
import { MarkFailedDto } from './dto/mark-failed.dto';
import { MarkBrokenDto } from './dto/mark-broken.dto';

@Injectable()
export class DronesService {
  constructor(private prisma: PrismaService) {}

  async getDrone(userId: string) {
    const drone = await this.prisma.drone.findUnique({
      where: { userId },
      include: { currentOrder: true },
    });

    if (!drone) {
      throw new NotFoundException('Drone not found');
    }

    return drone;
  }

  async reserveJob(userId: string) {
    const drone = await this.getDrone(userId);

    if (drone.status !== DroneStatus.AVAILABLE) {
      throw new BadRequestException('Drone must be available to reserve a job');
    }

    if (drone.currentOrderId) {
      throw new BadRequestException('Drone already has an active order');
    }

    
    const availableOrder = await this.prisma.order.findFirst({
      where: {
        OR: [
          { status: OrderStatus.PENDING },
          { status: OrderStatus.PENDING_HANDOFF },
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
        status: OrderStatus.ASSIGNED,
      },
    });

    await this.prisma.drone.update({
      where: { id: drone.id },
      data: {
        currentOrderId: updatedOrder.id,
        status: DroneStatus.BUSY,
      },
    });

    return {
      success: true,
      order: updatedOrder,
      message: 'Order reserved successfully',
    };
  }

  async grabOrder(userId: string, orderId: string) {
    const drone = await this.getDrone(userId);

    const order = await this.prisma.order.findUnique({
      where: { id: orderId },
    });

    if (!order) {
      throw new NotFoundException('Order not found');
    }

    if (order.assignedDroneId !== drone.id) {
      throw new BadRequestException('Order is not assigned to this drone');
    }

    if (order.status !== OrderStatus.ASSIGNED) {
      throw new BadRequestException('Order must be in ASSIGNED status');
    }

    const updatedOrder = await this.prisma.order.update({
      where: { id: orderId },
      data: {
        status: OrderStatus.PICKED_UP,
        pickedUpAt: new Date(),
      },
    });

    return {
      success: true,
      order: updatedOrder,
      message: 'Order picked up successfully',
    };
  }

  async updateLocation(userId: string, updateLocationDto: UpdateLocationDto) {
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

      if (order && order.status === OrderStatus.PICKED_UP) {
        await this.prisma.order.update({
          where: { id: drone.currentOrderId },
          data: { status: OrderStatus.IN_TRANSIT },
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

  async markDelivered(userId: string, orderId: string) {
    const drone = await this.getDrone(userId);

    const order = await this.prisma.order.findUnique({
      where: { id: orderId },
    });

    if (!order) {
      throw new NotFoundException('Order not found');
    }

    if (order.assignedDroneId !== drone.id) {
      throw new BadRequestException('Order is not assigned to this drone');
    }

    await this.prisma.order.update({
      where: { id: orderId },
      data: {
        status: OrderStatus.DELIVERED,
        deliveredAt: new Date(),
      },
    });

    
    await this.prisma.drone.update({
      where: { id: drone.id },
      data: {
        currentOrderId: null,
        status: DroneStatus.AVAILABLE,
      },
    });

    return {
      success: true,
      message: 'Order marked as delivered',
    };
  }

  async markFailed(userId: string, markFailedDto: MarkFailedDto) {
    const drone = await this.getDrone(userId);

    const order = await this.prisma.order.findUnique({
      where: { id: markFailedDto.orderId },
    });

    if (!order) {
      throw new NotFoundException('Order not found');
    }

    if (order.assignedDroneId !== drone.id) {
      throw new BadRequestException('Order is not assigned to this drone');
    }

    await this.prisma.order.update({
      where: { id: markFailedDto.orderId },
      data: {
        status: OrderStatus.FAILED,
        failedAt: new Date(),
        failureReason: markFailedDto.reason,
      },
    });

    
    await this.prisma.drone.update({
      where: { id: drone.id },
      data: {
        currentOrderId: null,
        status: DroneStatus.AVAILABLE,
      },
    });

    return {
      success: true,
      message: 'Order marked as failed',
    };
  }

  async markBroken(userId: string, markBrokenDto: MarkBrokenDto) {
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
            status: OrderStatus.PENDING_HANDOFF,
            assignedDroneId: null, 
          },
        });
      }
    }

    
    await this.prisma.drone.update({
      where: { id: drone.id },
      data: {
        status: DroneStatus.BROKEN,
        currentOrderId: null,
      },
    });

    return {
      success: true,
      message: 'Drone marked as broken. Order handoff created if applicable.',
    };
  }

  async getCurrentOrder(userId: string) {
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
}
