import { INestApplication } from '@nestjs/common';
import request from 'supertest';

export async function getAuthToken(
  app: INestApplication,
  name: string,
  userType: string,
  password: string = 'password123',
): Promise<string> {
  
  const registerResponse = await request(app.getHttpServer())
    .post('/auth/register')
    .send({ name, password, userType });

  
  if (registerResponse.status === 201) {
    return registerResponse.body.access_token;
  }

  
  if (registerResponse.status === 409) {
    const loginResponse = await request(app.getHttpServer())
      .post('/auth/login')
      .send({ name, password })
      .expect(200);

    return loginResponse.body.access_token;
  }

  
  throw new Error(`Failed to get auth token: ${registerResponse.status} - ${JSON.stringify(registerResponse.body)}`);
}

export async function createOrder(
  app: INestApplication,
  token: string,
  orderData?: any,
) {
  const defaultOrder = {
    originLat: 40.7128,
    originLng: -74.0060,
    originAddress: '123 Main St, NYC',
    destinationLat: 40.7589,
    destinationLng: -73.9851,
    destinationAddress: '456 Broadway, NYC',
  };

  const response = await request(app.getHttpServer())
    .post('/orders')
    .set('Authorization', `Bearer ${token}`)
    .send(orderData || defaultOrder)
    .expect(201);

  return response.body;
}

export function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
