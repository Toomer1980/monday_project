import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { AppModule } from '../src/app.module';
import { getAuthToken, createOrder } from './helpers/test-utils';

describe('Admin (e2e)', () => {
  let app: INestApplication;
  let adminToken: string;
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

    adminToken = await getAuthToken(app, 'Admin Test', 'ADMIN');
    enduserToken = await getAuthToken(app, 'Admin Enduser', 'ENDUSER');
    droneToken = await getAuthToken(app, 'Admin Drone', 'DRONE');
  });

  afterAll(async () => {
    await app.close();
  });

  describe('GET /admin/orders', () => {
    it('should get all orders as admin', async () => {
      
      await createOrder(app, enduserToken);

      return request(app.getHttpServer())
        .get('/admin/orders')
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(200)
        .expect((res) => {
          expect(Array.isArray(res.body)).toBe(true);
          expect(res.body.length).toBeGreaterThan(0);
          expect(res.body[0]).toHaveProperty('customer');
        });
    });

    it('should reject non-admin access', () => {
      return request(app.getHttpServer())
        .get('/admin/orders')
        .set('Authorization', `Bearer ${enduserToken}`)
        .expect(403);
    });
  });

  describe('PATCH /admin/orders/:id/origin', () => {
    it('should update order origin', async () => {
      const order = await createOrder(app, enduserToken);

      return request(app.getHttpServer())
        .patch(`/admin/orders/${order.id}/origin`)
        .set('Authorization', `Bearer ${adminToken}`)
        .send({
          lat: 41.0000,
          lng: -75.0000,
          address: 'New Origin Address',
        })
        .expect(200)
        .expect((res) => {
          expect(res.body.originLat).toBe(41.0000);
          expect(res.body.originAddress).toBe('New Origin Address');
        });
    });

    it('should reject non-admin', async () => {
      const order = await createOrder(app, enduserToken);

      return request(app.getHttpServer())
        .patch(`/admin/orders/${order.id}/origin`)
        .set('Authorization', `Bearer ${enduserToken}`)
        .send({ lat: 41.0000 })
        .expect(403);
    });
  });

  describe('PATCH /admin/orders/:id/destination', () => {
    it('should update order destination', async () => {
      const order = await createOrder(app, enduserToken);

      return request(app.getHttpServer())
        .patch(`/admin/orders/${order.id}/destination`)
        .set('Authorization', `Bearer ${adminToken}`)
        .send({
          lat: 42.0000,
          lng: -76.0000,
          address: 'New Destination',
        })
        .expect(200)
        .expect((res) => {
          expect(res.body.destinationLat).toBe(42.0000);
          expect(res.body.destinationAddress).toBe('New Destination');
        });
    });
  });

  describe('GET /admin/drones', () => {
    it('should get all drones', () => {
      return request(app.getHttpServer())
        .get('/admin/drones')
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(200)
        .expect((res) => {
          expect(Array.isArray(res.body)).toBe(true);
          expect(res.body.length).toBeGreaterThan(0);
          expect(res.body[0]).toHaveProperty('user');
          expect(res.body[0]).toHaveProperty('status');
        });
    });

    it('should reject non-admin', () => {
      return request(app.getHttpServer())
        .get('/admin/drones')
        .set('Authorization', `Bearer ${droneToken}`)
        .expect(403);
    });
  });

  describe('POST /admin/drones/:id/mark-broken', () => {
    it('should mark drone as broken', async () => {
      const testDrone = await getAuthToken(app, 'Admin Break Drone', 'DRONE');
      const testUser = await getAuthToken(app, 'Admin Break User', 'ENDUSER');

      
      const drones = await request(app.getHttpServer())
        .get('/admin/drones')
        .set('Authorization', `Bearer ${adminToken}`);

      const drone = drones.body.find(d => d.user.name === 'Admin Break Drone');

      
      const order = await createOrder(app, testUser);
      await request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${testDrone}`);

      
      return request(app.getHttpServer())
        .post(`/admin/drones/${drone.id}/mark-broken`)
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(201)
        .expect((res) => {
          expect(res.body.status).toBe('BROKEN');
        });
    });
  });

  describe('POST /admin/drones/:id/mark-fixed', () => {
    it('should mark drone as fixed', async () => {
      const testDrone = await getAuthToken(app, 'Admin Fix Drone', 'DRONE');

      
      const drones = await request(app.getHttpServer())
        .get('/admin/drones')
        .set('Authorization', `Bearer ${adminToken}`);

      const drone = drones.body.find(d => d.user.name === 'Admin Fix Drone');

      
      await request(app.getHttpServer())
        .post(`/admin/drones/${drone.id}/mark-broken`)
        .set('Authorization', `Bearer ${adminToken}`);

      
      return request(app.getHttpServer())
        .post(`/admin/drones/${drone.id}/mark-fixed`)
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(201)
        .expect((res) => {
          expect(res.body.status).toBe('AVAILABLE');
        });
    });

    it('should reject non-admin', async () => {
      return request(app.getHttpServer())
        .post('/admin/drones/any-id/mark-fixed')
        .set('Authorization', `Bearer ${enduserToken}`)
        .expect(403);
    });
  });
});
