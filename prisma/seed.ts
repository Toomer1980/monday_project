import { PrismaClient, UserRole, OrderStatus, DroneStatus } from '@prisma/client';
import * as bcrypt from 'bcrypt';

const prisma = new PrismaClient();


const locations = [
  { name: 'Times Square', lat: 40.758, lng: -73.9855, address: '1560 Broadway, New York, NY 10036' },
  { name: 'Central Park', lat: 40.7829, lng: -73.9654, address: 'Central Park, New York, NY 10024' },
  { name: 'Empire State Building', lat: 40.7484, lng: -73.9857, address: '350 5th Ave, New York, NY 10118' },
  { name: 'Brooklyn Bridge', lat: 40.7061, lng: -73.9969, address: 'Brooklyn Bridge, New York, NY 10038' },
  { name: 'Statue of Liberty', lat: 40.6892, lng: -74.0445, address: 'Liberty Island, New York, NY 10004' },
  { name: 'Wall Street', lat: 40.7074, lng: -74.0113, address: '11 Wall St, New York, NY 10005' },
  { name: 'Grand Central', lat: 40.7527, lng: -73.9772, address: '89 E 42nd St, New York, NY 10017' },
  { name: 'Chelsea Market', lat: 40.7425, lng: -74.0061, address: '75 9th Ave, New York, NY 10011' },
  { name: 'SoHo', lat: 40.7233, lng: -74.0030, address: 'SoHo, New York, NY 10012' },
  { name: 'Union Square', lat: 40.7359, lng: -73.9911, address: 'Union Square, New York, NY 10003' },
];


function getRandomLocation() {
  return locations[Math.floor(Math.random() * locations.length)];
}


function getTwoRandomLocations() {
  const origin = getRandomLocation();
  let destination = getRandomLocation();
  while (destination.name === origin.name) {
    destination = getRandomLocation();
  }
  return { origin, destination };
}


function generateOrderNumber(index: number): string {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  return `ORD-${date}-${String(index).padStart(4, '0')}`;
}


async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10);
}


function addOffset(coord: number, maxOffset: number = 0.01): number {
  return coord + (Math.random() - 0.5) * maxOffset;
}

async function main() {
  console.log('Starting database seed...\n');

  
  console.log('Clearing existing data...');
  await prisma.locationHistory.deleteMany();
  await prisma.orderHandoff.deleteMany();
  await prisma.order.deleteMany();
  await prisma.drone.deleteMany();
  await prisma.user.deleteMany();
  console.log('Existing data cleared\n');

  
  const hashedPassword = await hashPassword('password123');

  
  console.log('Creating admin users...');
  const admins = await Promise.all([
    prisma.user.create({
      data: {
        name: 'admin@dronedelivery.com',
        password: hashedPassword,
        role: UserRole.ADMIN,
      },
    }),
    prisma.user.create({
      data: {
        name: 'admin.support@dronedelivery.com',
        password: hashedPassword,
        role: UserRole.ADMIN,
      },
    }),
  ]);
  console.log(`Created ${admins.length} admin users\n`);

  
  console.log('Creating end users...');
  const endusers = await Promise.all([
    prisma.user.create({
      data: {
        name: 'john.doe@example.com',
        password: hashedPassword,
        role: UserRole.ENDUSER,
      },
    }),
    prisma.user.create({
      data: {
        name: 'jane.smith@example.com',
        password: hashedPassword,
        role: UserRole.ENDUSER,
      },
    }),
    prisma.user.create({
      data: {
        name: 'bob.johnson@example.com',
        password: hashedPassword,
        role: UserRole.ENDUSER,
      },
    }),
    prisma.user.create({
      data: {
        name: 'alice.williams@example.com',
        password: hashedPassword,
        role: UserRole.ENDUSER,
      },
    }),
    prisma.user.create({
      data: {
        name: 'charlie.brown@example.com',
        password: hashedPassword,
        role: UserRole.ENDUSER,
      },
    }),
  ]);
  console.log(`Created ${endusers.length} end users\n`);

  
  console.log('Creating drones...');
  const droneUsers = await Promise.all([
    prisma.user.create({
      data: {
        name: 'drone.alpha@dronedelivery.com',
        password: hashedPassword,
        role: UserRole.DRONE,
      },
    }),
    prisma.user.create({
      data: {
        name: 'drone.beta@dronedelivery.com',
        password: hashedPassword,
        role: UserRole.DRONE,
      },
    }),
    prisma.user.create({
      data: {
        name: 'drone.gamma@dronedelivery.com',
        password: hashedPassword,
        role: UserRole.DRONE,
      },
    }),
    prisma.user.create({
      data: {
        name: 'drone.delta@dronedelivery.com',
        password: hashedPassword,
        role: UserRole.DRONE,
      },
    }),
    prisma.user.create({
      data: {
        name: 'drone.epsilon@dronedelivery.com',
        password: hashedPassword,
        role: UserRole.DRONE,
      },
    }),
  ]);

  const drones = await Promise.all([
    
    prisma.drone.create({
      data: {
        userId: droneUsers[0].id,
        serialNumber: 'DRN-ALPHA-001',
        status: DroneStatus.AVAILABLE,
        batteryLevel: 95.5,
        currentLat: 40.7580,
        currentLng: -73.9855,
      },
    }),
    
    prisma.drone.create({
      data: {
        userId: droneUsers[1].id,
        serialNumber: 'DRN-BETA-002',
        status: DroneStatus.BUSY,
        batteryLevel: 78.3,
        currentLat: 40.7425,
        currentLng: -74.0061,
      },
    }),
    
    prisma.drone.create({
      data: {
        userId: droneUsers[2].id,
        serialNumber: 'DRN-GAMMA-003',
        status: DroneStatus.AVAILABLE,
        batteryLevel: 88.7,
        currentLat: 40.7527,
        currentLng: -73.9772,
      },
    }),
    
    prisma.drone.create({
      data: {
        userId: droneUsers[3].id,
        serialNumber: 'DRN-DELTA-004',
        status: DroneStatus.BROKEN,
        batteryLevel: 45.2,
        currentLat: 40.7233,
        currentLng: -74.0030,
      },
    }),
    
    prisma.drone.create({
      data: {
        userId: droneUsers[4].id,
        serialNumber: 'DRN-EPSILON-005',
        status: DroneStatus.MAINTENANCE,
        batteryLevel: 0,
        currentLat: null,
        currentLng: null,
      },
    }),
  ]);
  console.log(`Created ${drones.length} drones\n`);

  
  console.log('Creating orders...');

  
  const pendingOrders = [];
  for (let i = 0; i < 3; i++) {
    const { origin, destination } = getTwoRandomLocations();
    const customer = endusers[Math.floor(Math.random() * endusers.length)];
    const order = await prisma.order.create({
      data: {
        orderNumber: generateOrderNumber(i + 1),
        customerId: customer.id,
        originLat: origin.lat,
        originLng: origin.lng,
        originAddress: origin.address,
        destinationLat: destination.lat,
        destinationLng: destination.lng,
        destinationAddress: destination.address,
        status: OrderStatus.PENDING,
      },
    });
    pendingOrders.push(order);
  }

  
  const assignedLocs = getTwoRandomLocations();
  const assignedOrder = await prisma.order.create({
    data: {
      orderNumber: generateOrderNumber(4),
      customerId: endusers[0].id,
      originLat: assignedLocs.origin.lat,
      originLng: assignedLocs.origin.lng,
      originAddress: assignedLocs.origin.address,
      destinationLat: assignedLocs.destination.lat,
      destinationLng: assignedLocs.destination.lng,
      destinationAddress: assignedLocs.destination.address,
      status: OrderStatus.ASSIGNED,
      assignedDroneId: drones[1].id,
    },
  });

  
  await prisma.drone.update({
    where: { id: drones[1].id },
    data: { currentOrderId: assignedOrder.id },
  });

  
  const transitLocs = getTwoRandomLocations();
  const transitOrder = await prisma.order.create({
    data: {
      orderNumber: generateOrderNumber(5),
      customerId: endusers[1].id,
      originLat: transitLocs.origin.lat,
      originLng: transitLocs.origin.lng,
      originAddress: transitLocs.origin.address,
      destinationLat: transitLocs.destination.lat,
      destinationLng: transitLocs.destination.lng,
      destinationAddress: transitLocs.destination.address,
      status: OrderStatus.IN_TRANSIT,
      assignedDroneId: drones[1].id,
      pickedUpAt: new Date(Date.now() - 15 * 60 * 1000), 
    },
  });

  
  const locationHistoryPoints = 5;
  for (let i = 0; i < locationHistoryPoints; i++) {
    const progress = i / locationHistoryPoints;
    const lat = transitLocs.origin.lat + (transitLocs.destination.lat - transitLocs.origin.lat) * progress;
    const lng = transitLocs.origin.lng + (transitLocs.destination.lng - transitLocs.origin.lng) * progress;

    await prisma.locationHistory.create({
      data: {
        droneId: drones[1].id,
        lat: addOffset(lat, 0.001),
        lng: addOffset(lng, 0.001),
        timestamp: new Date(Date.now() - (locationHistoryPoints - i) * 3 * 60 * 1000), 
      },
    });
  }

  
  const deliveredOrders = [];
  for (let i = 0; i < 5; i++) {
    const { origin, destination } = getTwoRandomLocations();
    const customer = endusers[Math.floor(Math.random() * endusers.length)];
    const drone = drones[Math.floor(Math.random() * 3)]; 

    const order = await prisma.order.create({
      data: {
        orderNumber: generateOrderNumber(6 + i),
        customerId: customer.id,
        originLat: origin.lat,
        originLng: origin.lng,
        originAddress: origin.address,
        destinationLat: destination.lat,
        destinationLng: destination.lng,
        destinationAddress: destination.address,
        status: OrderStatus.DELIVERED,
        assignedDroneId: drone.id,
        pickedUpAt: new Date(Date.now() - (2 + i) * 60 * 60 * 1000), 
        deliveredAt: new Date(Date.now() - (1 + i) * 60 * 60 * 1000),
      },
    });
    deliveredOrders.push(order);
  }

  
  const failedLocs = getTwoRandomLocations();
  const failedOrder = await prisma.order.create({
    data: {
      orderNumber: generateOrderNumber(11),
      customerId: endusers[2].id,
      originLat: failedLocs.origin.lat,
      originLng: failedLocs.origin.lng,
      originAddress: failedLocs.origin.address,
      destinationLat: failedLocs.destination.lat,
      destinationLng: failedLocs.destination.lng,
      destinationAddress: failedLocs.destination.address,
      status: OrderStatus.FAILED,
      assignedDroneId: drones[3].id,
      pickedUpAt: new Date(Date.now() - 3 * 60 * 60 * 1000),
      failedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      failureReason: 'Severe weather conditions prevented safe delivery',
    },
  });

  
  const handoffLocs = getTwoRandomLocations();
  const handoffOrder = await prisma.order.create({
    data: {
      orderNumber: generateOrderNumber(12),
      customerId: endusers[3].id,
      originLat: handoffLocs.origin.lat,
      originLng: handoffLocs.origin.lng,
      originAddress: handoffLocs.origin.address,
      destinationLat: handoffLocs.destination.lat,
      destinationLng: handoffLocs.destination.lng,
      destinationAddress: handoffLocs.destination.address,
      status: OrderStatus.PENDING_HANDOFF,
      pickedUpAt: new Date(Date.now() - 45 * 60 * 1000), 
    },
  });

  
  await prisma.orderHandoff.create({
    data: {
      orderId: handoffOrder.id,
      fromDroneId: drones[3].id,
      handoffLat: 40.7300,
      handoffLng: -74.0000,
      reason: 'Drone battery critical - emergency landing required',
      completed: false,
    },
  });

  console.log(`Created 12 orders in various states:`);
  console.log(`   - ${pendingOrders.length} PENDING`);
  console.log(`   - 1 ASSIGNED`);
  console.log(`   - 1 IN_TRANSIT`);
  console.log(`   - ${deliveredOrders.length} DELIVERED`);
  console.log(`   - 1 FAILED`);
  console.log(`   - 1 PENDING_HANDOFF\n`);

  
  console.log('Seed Summary:');
  console.log('================');
  console.log(`${admins.length} Admins`);
  console.log(`${endusers.length} End Users`);
  console.log(`${drones.length} Drones`);
  console.log(`   - 2 Available`);
  console.log(`   - 1 Busy`);
  console.log(`   - 1 Broken`);
  console.log(`   - 1 In Maintenance`);
  console.log(`12 Orders`);
  console.log(`1 Order Handoff`);
  console.log(`${locationHistoryPoints} Location History Points`);
  console.log('\nDatabase seeded successfully!');
  console.log('\nTest Credentials (all passwords: password123):');
  console.log('   Admin: admin@dronedelivery.com');
  console.log('   User: john.doe@example.com');
  console.log('   Drone: drone.alpha@dronedelivery.com');
}

main()
  .catch((e) => {
    console.error('Error seeding database:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
