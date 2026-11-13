import { Controller, Post, Get, Delete, Body, Param } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiResponse } from '@nestjs/swagger';
import { OrdersService } from './orders.service';
import { CreateOrderDto } from './dto/create-order.dto';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { Roles } from '../common/decorators/roles.decorator';
import { UserRole } from '../common/enums/user-role.enum';

@ApiTags('Orders')
@ApiBearerAuth()
@Controller('orders')
export class OrdersController {
  constructor(private ordersService: OrdersService) {}

  @Post()
  @Roles(UserRole.ENDUSER)
  @ApiOperation({ summary: 'Create new order (Enduser only)' })
  async create(
    @CurrentUser() user: any,
    @Body() createOrderDto: CreateOrderDto,
  ) {
    return this.ordersService.create(user.id, createOrderDto);
  }

  @Get()
  @Roles(UserRole.ENDUSER)
  @ApiOperation({ summary: 'Get all orders for current user (Enduser only)' })
  async findAll(@CurrentUser() user: any) {
    return this.ordersService.findByUser(user.id);
  }

  @Get(':id')
  @Roles(UserRole.ENDUSER)
  @ApiOperation({ summary: 'Get order details with progress and ETA (Enduser only)' })
  async findOne(@CurrentUser() user: any, @Param('id') id: string) {
    return this.ordersService.findOne(id, user.id);
  }

  @Delete(':id')
  @Roles(UserRole.ENDUSER)
  @ApiOperation({ summary: 'Withdraw order (only if not picked up) (Enduser only)' })
  async withdraw(@CurrentUser() user: any, @Param('id') id: string) {
    return this.ordersService.withdraw(id, user.id);
  }
}
