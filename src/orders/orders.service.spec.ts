import { Test, TestingModule } from '@nestjs/testing';
import { OrdersService } from './orders.service';
import { PrismaService } from '../prisma/prisma.service';
import { OrderStatus } from '../common/enums/order-status.enum';
import { NotFoundException, ForbiddenException } from '@nestjs/common';

describe('OrdersService', () => {
  let service: OrdersService;
  let prisma: PrismaService;

  const mockPrismaService = {
    order: {
      create: jest.fn(),
      findMany: jest.fn(),
      findUnique: jest.fn(),
      update: jest.fn(),
    },
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        OrdersService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<OrdersService>(OrdersService);
    prisma = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('create', () => {
    it('should create order with PENDING status', async () => {
      const orderData = {
        originLat: 40.7128,
        originLng: -74.0060,
        originAddress: '123 Main St',
        destinationLat: 40.7589,
        destinationLng: -73.9851,
        destinationAddress: '456 Broadway',
      };

      const mockOrder = {
        id: 'order-123',
        orderNumber: 'ORD-123',
        customerId: 'user-123',
        status: OrderStatus.PENDING,
        ...orderData,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockPrismaService.order.create.mockResolvedValue(mockOrder);

      const result = await service.create('user-123', orderData);

      expect(result.status).toBe(OrderStatus.PENDING);
      expect(result.customerId).toBe('user-123');
      expect(mockPrismaService.order.create).toHaveBeenCalled();
    });

    it('should generate unique order number', async () => {
      const orderData = {
        originLat: 40.7128,
        originLng: -74.0060,
        originAddress: '123 Main St',
        destinationLat: 40.7589,
        destinationLng: -73.9851,
        destinationAddress: '456 Broadway',
      };

      mockPrismaService.order.create.mockResolvedValue({
        id: 'order-123',
        orderNumber: 'ORD-123',
        status: OrderStatus.PENDING,
        ...orderData,
      });

      await service.create('user-123', orderData);

      const createCall = mockPrismaService.order.create.mock.calls[0][0];
      expect(createCall.data.orderNumber).toMatch(/^ORD-/);
    });
  });

  describe('findByUser', () => {
    it('should return all orders for user', async () => {
      const mockOrders = [
        {
          id: 'order-1',
          customerId: 'user-123',
          status: OrderStatus.PENDING,
          assignedDrone: null,
        },
        {
          id: 'order-2',
          customerId: 'user-123',
          status: OrderStatus.DELIVERED,
          assignedDrone: null,
        },
      ];

      mockPrismaService.order.findMany.mockResolvedValue(mockOrders);

      const result = await service.findByUser('user-123');

      expect(result).toHaveLength(2);
      expect(mockPrismaService.order.findMany).toHaveBeenCalledWith({
        where: { customerId: 'user-123' },
        include: expect.any(Object),
        orderBy: { createdAt: 'desc' },
      });
    });
  });

  describe('findOne', () => {
    it('should return order with ETA when drone assigned', async () => {
      const mockOrder = {
        id: 'order-123',
        customerId: 'user-123',
        destinationLat: 40.7589,
        destinationLng: -73.9851,
        assignedDrone: {
          id: 'drone-123',
          currentLat: 40.7128,
          currentLng: -74.0060,
          status: 'BUSY',
        },
      };

      mockPrismaService.order.findUnique.mockResolvedValue(mockOrder);

      const result = await service.findOne('order-123', 'user-123');

      expect(result).toHaveProperty('estimatedTimeMinutes');
      expect(typeof result.estimatedTimeMinutes).toBe('number');
      expect(result.estimatedTimeMinutes).toBeGreaterThan(0);
    });

    it('should throw NotFoundException when order not found', async () => {
      mockPrismaService.order.findUnique.mockResolvedValue(null);

      await expect(
        service.findOne('nonexistent', 'user-123'),
      ).rejects.toThrow(NotFoundException);
    });

    it('should throw ForbiddenException when user does not own order', async () => {
      const mockOrder = {
        id: 'order-123',
        customerId: 'other-user',
      };

      mockPrismaService.order.findUnique.mockResolvedValue(mockOrder);

      await expect(
        service.findOne('order-123', 'user-123'),
      ).rejects.toThrow(ForbiddenException);
    });
  });

  describe('withdraw', () => {
    it('should cancel PENDING order', async () => {
      const mockOrder = {
        id: 'order-123',
        customerId: 'user-123',
        status: OrderStatus.PENDING,
      };

      mockPrismaService.order.findUnique.mockResolvedValue(mockOrder);
      mockPrismaService.order.update.mockResolvedValue({
        ...mockOrder,
        status: OrderStatus.CANCELLED,
      });

      const result = await service.withdraw('order-123', 'user-123');

      expect(result.status).toBe(OrderStatus.CANCELLED);
    });

    it('should not allow withdrawing picked up order', async () => {
      const mockOrder = {
        id: 'order-123',
        customerId: 'user-123',
        status: OrderStatus.PICKED_UP,
      };

      mockPrismaService.order.findUnique.mockResolvedValue(mockOrder);

      await expect(
        service.withdraw('order-123', 'user-123'),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should not allow withdrawing other users orders', async () => {
      const mockOrder = {
        id: 'order-123',
        customerId: 'other-user',
        status: OrderStatus.PENDING,
      };

      mockPrismaService.order.findUnique.mockResolvedValue(mockOrder);

      await expect(
        service.withdraw('order-123', 'user-123'),
      ).rejects.toThrow(ForbiddenException);
    });
  });

  describe('ETA calculation (Haversine formula)', () => {
    it('should calculate distance correctly', async () => {
      
      const mockOrder = {
        id: 'order-123',
        customerId: 'user-123',
        destinationLat: 40.7589,
        destinationLng: -73.9851,
        assignedDrone: {
          id: 'drone-123',
          currentLat: 40.7128,
          currentLng: -74.0060,
          status: 'BUSY',
        },
      };

      mockPrismaService.order.findUnique.mockResolvedValue(mockOrder);

      const result = await service.findOne('order-123', 'user-123');

      
      expect(result.estimatedTimeMinutes).toBeGreaterThan(0);
      expect(result.estimatedTimeMinutes).toBeLessThan(20);
    });

    it('should return null ETA when no drone assigned', async () => {
      const mockOrder = {
        id: 'order-123',
        customerId: 'user-123',
        assignedDrone: null,
      };

      mockPrismaService.order.findUnique.mockResolvedValue(mockOrder);

      const result = await service.findOne('order-123', 'user-123');

      expect(result.estimatedTimeMinutes).toBeNull();
    });
  });
});
