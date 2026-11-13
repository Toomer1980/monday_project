import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { AppModule } from '../src/app.module';

describe('Authentication (e2e)', () => {
  let app: INestApplication;

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
  });

  afterAll(async () => {
    await app.close();
  });

  describe('POST /auth/register', () => {
    it('should register new enduser and return JWT', () => {
      const timestamp = Date.now();
      return request(app.getHttpServer())
        .post('/auth/register')
        .send({
          name: `enduser${timestamp}@example.com`,
          password: 'password123',
          userType: 'ENDUSER',
        })
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty('access_token');
          expect(res.body).toHaveProperty('user');
          expect(res.body.user.role).toBe('ENDUSER');
        });
    });

    it('should register drone and create drone record with droneId', () => {
      const timestamp = Date.now();
      return request(app.getHttpServer())
        .post('/auth/register')
        .send({
          name: `drone${timestamp}@example.com`,
          password: 'password123',
          userType: 'DRONE',
        })
        .expect(201)
        .expect((res) => {
          expect(res.body.user.role).toBe('DRONE');
          expect(res.body).toHaveProperty('droneId');
          expect(typeof res.body.droneId).toBe('string');
        });
    });

    it('should reject duplicate username', async () => {
      const timestamp = Date.now();
      const userData = {
        name: `duplicate${timestamp}@example.com`,
        password: 'password123',
        userType: 'ENDUSER',
      };

      await request(app.getHttpServer())
        .post('/auth/register')
        .send(userData)
        .expect(201);

      return request(app.getHttpServer())
        .post('/auth/register')
        .send(userData)
        .expect(409);
    });

    it('should reject weak password', () => {
      const timestamp = Date.now();
      return request(app.getHttpServer())
        .post('/auth/register')
        .send({
          name: `weakpass${timestamp}@example.com`,
          password: '123',
          userType: 'ENDUSER',
        })
        .expect(400);
    });
  });

  describe('POST /auth/login', () => {
    beforeAll(async () => {
      
      await request(app.getHttpServer())
        .post('/auth/register')
        .send({
          name: 'login-test@example.com',
          password: 'password123',
          userType: 'ENDUSER',
        });
    });

    it('should login with valid credentials', () => {
      return request(app.getHttpServer())
        .post('/auth/login')
        .send({
          name: 'login-test@example.com',
          password: 'password123',
        })
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty('access_token');
          expect(res.body.user.name).toBe('login-test@example.com');
        });
    });

    it('should login drone and include droneId in response', async () => {
      const timestamp = Date.now();
      const droneName = `drone-login${timestamp}@example.com`;

      
      await request(app.getHttpServer())
        .post('/auth/register')
        .send({
          name: droneName,
          password: 'password123',
          userType: 'DRONE',
        });

      
      return request(app.getHttpServer())
        .post('/auth/login')
        .send({
          name: droneName,
          password: 'password123',
        })
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty('access_token');
          expect(res.body).toHaveProperty('droneId');
          expect(typeof res.body.droneId).toBe('string');
          expect(res.body.user.role).toBe('DRONE');
        });
    });

    it('should reject invalid password', () => {
      return request(app.getHttpServer())
        .post('/auth/login')
        .send({
          name: 'login-test@example.com',
          password: 'wrongpassword',
        })
        .expect(401);
    });

    it('should reject non-existent user', () => {
      return request(app.getHttpServer())
        .post('/auth/login')
        .send({
          name: 'nonexistent@example.com',
          password: 'password123',
        })
        .expect(401);
    });

    it('should reject missing password', () => {
      return request(app.getHttpServer())
        .post('/auth/login')
        .send({
          name: 'login-test@example.com',
        })
        .expect(400);
    });
  });

  describe('JWT Protection', () => {
    it('should reject requests without token', () => {
      return request(app.getHttpServer())
        .get('/orders')
        .expect(401);
    });

    it('should reject invalid token', () => {
      return request(app.getHttpServer())
        .get('/orders')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);
    });
  });
});
