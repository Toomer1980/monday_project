import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { AppModule } from '../src/app.module';
import { getAuthToken, createOrder } from './helpers/test-utils';

describe('Orders (e2e)', () => {
  let app: INestApplication;
  let enduserToken: string;
  let droneToken: string;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();

    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
      }),
    );

    await app.init();

    enduserToken = await getAuthToken(app, 'Orders Enduser', 'ENDUSER');
    droneToken = await getAuthToken(app, 'Orders Drone', 'DRONE');
  });

  afterAll(async () => {
    await app.close();
  });

  describe('POST /orders', () => {
    it('should create order as enduser', () => {
      return request(app.getHttpServer())
        .post('/orders')
        .set('Authorization', `Bearer ${enduserToken}`)
        .send({
          originLat: 40.7128,
          originLng: -74.0060,
          originAddress: '123 Main St',
          destinationLat: 40.7589,
          destinationLng: -73.9851,
          destinationAddress: '456 Broadway',
        })
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty('id');
          expect(res.body).toHaveProperty('orderNumber');
          expect(res.body.status).toBe('PENDING');
          expect(res.body.originLat).toBe(40.7128);
          expect(res.body.destinationLat).toBe(40.7589);
        });
    });

    it('should reject order creation by drone', () => {
      return request(app.getHttpServer())
        .post('/orders')
        .set('Authorization', `Bearer ${droneToken}`)
        .send({
          originLat: 40.7128,
          originLng: -74.0060,
          originAddress: '123 Main St',
          destinationLat: 40.7589,
          destinationLng: -73.9851,
          destinationAddress: '456 Broadway',
        })
        .expect(403);
    });

    it('should validate latitude bounds', () => {
      return request(app.getHttpServer())
        .post('/orders')
        .set('Authorization', `Bearer ${enduserToken}`)
        .send({
          originLat: 100, 
          originLng: -74.0060,
          originAddress: '123 Main St',
          destinationLat: 40.7589,
          destinationLng: -73.9851,
          destinationAddress: '456 Broadway',
        })
        .expect(400);
    });

    it('should validate required fields', () => {
      return request(app.getHttpServer())
        .post('/orders')
        .set('Authorization', `Bearer ${enduserToken}`)
        .send({
          originLat: 40.7128,
          
        })
        .expect(400);
    });
  });

  describe('GET /orders', () => {
    it('should get all orders for current user', async () => {
      
      await createOrder(app, enduserToken);

      return request(app.getHttpServer())
        .get('/orders')
        .set('Authorization', `Bearer ${enduserToken}`)
        .expect(200)
        .expect((res) => {
          expect(Array.isArray(res.body)).toBe(true);
          expect(res.body.length).toBeGreaterThan(0);
        });
    });

    it('should only show user own orders', async () => {
      const user1Token = await getAuthToken(app, 'User 1', 'ENDUSER');
      const user2Token = await getAuthToken(app, 'User 2', 'ENDUSER');

      await createOrder(app, user1Token);

      const response = await request(app.getHttpServer())
        .get('/orders')
        .set('Authorization', `Bearer ${user2Token}`)
        .expect(200);

      expect(response.body.length).toBe(0);
    });
  });

  describe('GET /orders/:id', () => {
    it('should get order details with ETA', async () => {
      const order = await createOrder(app, enduserToken);

      return request(app.getHttpServer())
        .get(`/orders/${order.id}`)
        .set('Authorization', `Bearer ${enduserToken}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.id).toBe(order.id);
          expect(res.body).toHaveProperty('status');
          expect(res.body).toHaveProperty('originAddress');
        });
    });

    it('should not allow viewing other users orders', async () => {
      const user1Token = await getAuthToken(app, 'View User 1', 'ENDUSER');
      const user2Token = await getAuthToken(app, 'View User 2', 'ENDUSER');

      const order = await createOrder(app, user1Token);

      return request(app.getHttpServer())
        .get(`/orders/${order.id}`)
        .set('Authorization', `Bearer ${user2Token}`)
        .expect(403);
    });

    it('should return 404 for non-existent order', () => {
      return request(app.getHttpServer())
        .get('/orders/00000000-0000-0000-0000-000000000000')
        .set('Authorization', `Bearer ${enduserToken}`)
        .expect(404);
    });
  });

  describe('DELETE /orders/:id', () => {
    it('should withdraw pending order', async () => {
      const order = await createOrder(app, enduserToken);

      return request(app.getHttpServer())
        .delete(`/orders/${order.id}`)
        .set('Authorization', `Bearer ${enduserToken}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.status).toBe('CANCELLED');
        });
    });

    it('should not withdraw other users orders', async () => {
      const user1Token = await getAuthToken(app, 'Del User 1', 'ENDUSER');
      const user2Token = await getAuthToken(app, 'Del User 2', 'ENDUSER');

      const order = await createOrder(app, user1Token);

      return request(app.getHttpServer())
        .delete(`/orders/${order.id}`)
        .set('Authorization', `Bearer ${user2Token}`)
        .expect(403);
    });
  });
});
