import { Controller, Get, Patch, Post, Param, Body } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { AdminService } from './admin.service';
import { Roles } from '../common/decorators/roles.decorator';
import { UserRole } from '../common/enums/user-role.enum';
import { UpdateOrderLocationDto } from './dto/update-order-location.dto';

@ApiTags('Admin')
@ApiBearerAuth()
@Controller('admin')
export class AdminController {
  constructor(private adminService: AdminService) {}

  @Get('orders')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Get all orders in bulk (Admin only)' })
  async getAllOrders() {
    return this.adminService.getAllOrders();
  }

  @Patch('orders/:id/origin')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Update order origin (Admin only)' })
  async updateOrderOrigin(
    @Param('id') id: string,
    @Body() updateDto: UpdateOrderLocationDto,
  ) {
    return this.adminService.updateOrderOrigin(id, updateDto);
  }

  @Patch('orders/:id/destination')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Update order destination (Admin only)' })
  async updateOrderDestination(
    @Param('id') id: string,
    @Body() updateDto: UpdateOrderLocationDto,
  ) {
    return this.adminService.updateOrderDestination(id, updateDto);
  }

  @Get('drones')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Get list of all drones (Admin only)' })
  async getAllDrones() {
    return this.adminService.getAllDrones();
  }

  @Post('drones/:id/mark-broken')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Mark drone as broken (Admin only)' })
  async markDroneBroken(@Param('id') id: string) {
    return this.adminService.markDroneBroken(id);
  }

  @Post('drones/:id/mark-fixed')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Mark drone as fixed (Admin only)' })
  async markDroneFixed(@Param('id') id: string) {
    return this.adminService.markDroneFixed(id);
  }
}
