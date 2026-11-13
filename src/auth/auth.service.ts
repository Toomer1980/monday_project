import { Injectable, UnauthorizedException, ConflictException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { PrismaService } from '../prisma/prisma.service';
import { LoginDto } from './dto/login.dto';
import { RegisterDto } from './dto/register.dto';
import { UserRole } from '../common/enums/user-role.enum';
import * as bcrypt from 'bcrypt';

@Injectable()
export class AuthService {
  constructor(
    private prisma: PrismaService,
    private jwtService: JwtService,
  ) {}

  async register(registerDto: RegisterDto) {
    const existingUser = await this.prisma.user.findFirst({
      where: {
        name: registerDto.name,
      },
    });

    if (existingUser) {
      throw new ConflictException('User with this name already exists');
    }

    const hashedPassword = await bcrypt.hash(registerDto.password, 10);

    const user = await this.prisma.user.create({
      data: {
        name: registerDto.name,
        password: hashedPassword,
        role: registerDto.userType,
      },
    });

    let droneId: string | undefined;
    if (registerDto.userType === UserRole.DRONE) {
      const drone = await this.prisma.drone.create({
        data: {
          userId: user.id,
        },
      });
      droneId = drone.id;
    }

    const payload = {
      sub: user.id,
      name: user.name,
      role: user.role,
    };

    const response: any = {
      access_token: this.jwtService.sign(payload),
      user: {
        id: user.id,
        name: user.name,
        role: user.role,
      },
    };

    if (droneId) {
      response.droneId = droneId;
    }

    return response;
  }

  async login(loginDto: LoginDto) {
    const user = await this.prisma.user.findFirst({
      where: {
        name: loginDto.name,
      },
    });

    if (!user) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const isPasswordValid = await bcrypt.compare(loginDto.password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    let droneId: string | undefined;
    if (user.role === UserRole.DRONE) {
      const drone = await this.prisma.drone.findUnique({
        where: { userId: user.id },
      });
      if (drone) {
        droneId = drone.id;
      }
    }

    const payload = {
      sub: user.id,
      name: user.name,
      role: user.role,
    };

    const response: any = {
      access_token: this.jwtService.sign(payload),
      user: {
        id: user.id,
        name: user.name,
        role: user.role,
      },
    };

    if (droneId) {
      response.droneId = droneId;
    }

    return response;
  }
}
