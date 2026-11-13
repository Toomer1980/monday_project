import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { AppModule } from '../src/app.module';
import { getAuthToken, createOrder } from './helpers/test-utils';

describe('Drones (e2e)', () => {
  let app: INestApplication;
  let droneToken: string;
  let enduserToken: string;

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

    droneToken = await getAuthToken(app, 'Test Drone Beta', 'DRONE');
    enduserToken = await getAuthToken(app, 'Drone Test User', 'ENDUSER');
  });

  afterAll(async () => {
    await app.close();
  });

  describe('POST /drones/reserve-job', () => {
    it('should reserve available job', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `ReserveD${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `ReserveU${timestamp}`, 'ENDUSER');

      await createOrder(app, testUser);

      return request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${testDrone}`)
        .expect(201)
        .expect((res) => {
          expect(res.body.success).toBe(true);
          expect(res.body).toHaveProperty('order');
          expect(res.body.order.status).toBe('ASSIGNED');
        });
    });

    it('should reject reserve when drone is busy', async () => {
      const timestamp = Date.now();
      const drone1 = await getAuthToken(app, `Busy1D${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `BusyU${timestamp}`, 'ENDUSER');

      await createOrder(app, testUser);

      const res1 = await request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${drone1}`)
        .expect(201);

      expect(res1.body.success).toBe(true);
      expect(res1.body.order).toBeDefined();

      return request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${drone1}`)
        .expect(400)
        .expect((res) => {
          expect(res.body.message).toContain('Drone must be available');
        });
    });

    it('should reject non-drone users', async () => {
      return request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${enduserToken}`)
        .expect(403);
    });
  });

  describe('POST /drones/grab-order', () => {
    it('should pickup assigned order', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `GrabD${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `GrabU${timestamp}`, 'ENDUSER');

      await createOrder(app, testUser);

      const reserveResponse = await request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${testDrone}`)
        .expect(201);

      const orderId = reserveResponse.body.order.id;

      return request(app.getHttpServer())
        .post('/drones/grab-order')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({ orderId })
        .expect(201)
        .expect((res) => {
          expect(res.body.success).toBe(true);
          expect(res.body.order.status).toBe('PICKED_UP');
        });
    });

    it('should reject grabbing unassigned order', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `RejectD${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `RejectU${timestamp}`, 'ENDUSER');

      const order = await createOrder(app, testUser);

      return request(app.getHttpServer())
        .post('/drones/grab-order')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({ orderId: order.id })
        .expect(400);
    });
  });

  describe('POST /drones/heartbeat', () => {
    it('should update drone location', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `HeartbeatD${timestamp}`, 'DRONE');

      return request(app.getHttpServer())
        .post('/drones/heartbeat')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({
          lat: 40.7300,
          lng: -74.0100,
        })
        .expect(201)
        .expect((res) => {
          expect(res.body.success).toBe(true);
          expect(res.body.drone.currentLat).toBe(40.7300);
          expect(res.body.drone.currentLng).toBe(-74.0100);
        });
    });

    it('should validate coordinates', () => {
      return request(app.getHttpServer())
        .post('/drones/heartbeat')
        .set('Authorization', `Bearer ${droneToken}`)
        .send({
          lat: 200, 
          lng: -74.0100,
        })
        .expect(400);
    });
  });

  describe('POST /drones/mark-delivered', () => {
    it('should mark order as delivered', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `DeliverD${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `DeliverU${timestamp}`, 'ENDUSER');

      await createOrder(app, testUser);

      const reserveResponse = await request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${testDrone}`)
        .expect(201);

      const orderId = reserveResponse.body.order.id;

      await request(app.getHttpServer())
        .post('/drones/grab-order')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({ orderId })
        .expect(201);

      return request(app.getHttpServer())
        .post('/drones/mark-delivered')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({ orderId })
        .expect(201)
        .expect((res) => {
          expect(res.body.success).toBe(true);
        });
    });
  });

  describe('POST /drones/mark-failed', () => {
    it('should mark order as failed', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `FailD${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `FailU${timestamp}`, 'ENDUSER');

      await createOrder(app, testUser);

      const reserveResponse = await request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${testDrone}`)
        .expect(201);

      const orderId = reserveResponse.body.order.id;

      await request(app.getHttpServer())
        .post('/drones/grab-order')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({ orderId })
        .expect(201);

      return request(app.getHttpServer())
        .post('/drones/mark-failed')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({
          orderId,
          reason: 'Weather conditions',
        })
        .expect(201)
        .expect((res) => {
          expect(res.body.success).toBe(true);
        });
    });
  });

  describe('POST /drones/mark-broken (Critical Handoff)', () => {
    it('should create handoff when drone breaks with order', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `BrokenD${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `BrokenU${timestamp}`, 'ENDUSER');

      await createOrder(app, testUser);

      const reserveResponse = await request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${testDrone}`)
        .expect(201);

      const orderId = reserveResponse.body.order.id;

      await request(app.getHttpServer())
        .post('/drones/grab-order')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({ orderId })
        .expect(201);

      return request(app.getHttpServer())
        .post('/drones/mark-broken')
        .set('Authorization', `Bearer ${testDrone}`)
        .send({ reason: 'Battery failure' })
        .expect(201)
        .expect((res) => {
          expect(res.body.success).toBe(true);
          expect(res.body.message).toContain('handoff');
        });
    });

    it('should allow another drone to pickup handoff order', async () => {
      const timestamp = Date.now();
      const drone1 = await getAuthToken(app, `Handoff1D${timestamp}`, 'DRONE');
      const drone2 = await getAuthToken(app, `Handoff2D${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `HandoffU${timestamp}`, 'ENDUSER');

      await createOrder(app, testUser);

      const reserveResponse = await request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${drone1}`)
        .expect(201);

      const orderId = reserveResponse.body.order.id;

      await request(app.getHttpServer())
        .post('/drones/grab-order')
        .set('Authorization', `Bearer ${drone1}`)
        .send({ orderId })
        .expect(201);

      await request(app.getHttpServer())
        .post('/drones/mark-broken')
        .set('Authorization', `Bearer ${drone1}`)
        .send({ reason: 'Battery dead' })
        .expect(201);

      return request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${drone2}`)
        .expect(201)
        .expect((res) => {
          expect(res.body.success).toBe(true);
          expect(res.body.order.status).toBe('ASSIGNED');
        });
    });
  });

  describe('GET /drones/current-order', () => {
    it('should get current order details', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `CurrentD${timestamp}`, 'DRONE');
      const testUser = await getAuthToken(app, `CurrentU${timestamp}`, 'ENDUSER');

      await createOrder(app, testUser);

      await request(app.getHttpServer())
        .post('/drones/reserve-job')
        .set('Authorization', `Bearer ${testDrone}`)
        .expect(201);

      return request(app.getHttpServer())
        .get('/drones/current-order')
        .set('Authorization', `Bearer ${testDrone}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.hasOrder).toBe(true);
          expect(res.body.order).toBeDefined();
        });
    });

    it('should return no order when none assigned', async () => {
      const timestamp = Date.now();
      const testDrone = await getAuthToken(app, `NoOrderD${timestamp}`, 'DRONE');

      return request(app.getHttpServer())
        .get('/drones/current-order')
        .set('Authorization', `Bearer ${testDrone}`)
        .expect(200)
        .expect((res) => {
          expect(res.body.hasOrder).toBe(false);
        });
    });
  });
});
