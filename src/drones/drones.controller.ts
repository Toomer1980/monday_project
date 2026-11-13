import { Controller, Post, Get, Body } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { DronesService } from './drones.service';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { Roles } from '../common/decorators/roles.decorator';
import { UserRole } from '../common/enums/user-role.enum';
import { UpdateLocationDto } from './dto/update-location.dto';
import { GrabOrderDto } from './dto/grab-order.dto';
import { MarkDeliveredDto } from './dto/mark-delivered.dto';
import { MarkFailedDto } from './dto/mark-failed.dto';
import { MarkBrokenDto } from './dto/mark-broken.dto';

@ApiTags('Drones')
@ApiBearerAuth()
@Controller('drones')
export class DronesController {
  constructor(private dronesService: DronesService) {}

  @Post('reserve-job')
  @Roles(UserRole.DRONE)
  @ApiOperation({ summary: 'Reserve an available job (Drone only)' })
  async reserveJob(@CurrentUser() user: any) {
    return this.dronesService.reserveJob(user.id);
  }

  @Post('grab-order')
  @Roles(UserRole.DRONE)
  @ApiOperation({ summary: 'Grab/pickup an assigned order (Drone only)' })
  async grabOrder(@CurrentUser() user: any, @Body() grabOrderDto: GrabOrderDto) {
    return this.dronesService.grabOrder(user.id, grabOrderDto.orderId);
  }

  @Post('heartbeat')
  @Roles(UserRole.DRONE)
  @ApiOperation({ summary: 'Update location and get status (Drone only)' })
  async updateLocation(@CurrentUser() user: any, @Body() updateLocationDto: UpdateLocationDto) {
    return this.dronesService.updateLocation(user.id, updateLocationDto);
  }

  @Post('mark-delivered')
  @Roles(UserRole.DRONE)
  @ApiOperation({ summary: 'Mark order as delivered (Drone only)' })
  async markDelivered(@CurrentUser() user: any, @Body() markDeliveredDto: MarkDeliveredDto) {
    return this.dronesService.markDelivered(user.id, markDeliveredDto.orderId);
  }

  @Post('mark-failed')
  @Roles(UserRole.DRONE)
  @ApiOperation({ summary: 'Mark order as failed (Drone only)' })
  async markFailed(@CurrentUser() user: any, @Body() markFailedDto: MarkFailedDto) {
    return this.dronesService.markFailed(user.id, markFailedDto);
  }

  @Post('mark-broken')
  @Roles(UserRole.DRONE)
  @ApiOperation({ summary: 'Mark drone as broken and create order handoff (Drone only)' })
  async markBroken(@CurrentUser() user: any, @Body() markBrokenDto: MarkBrokenDto) {
    return this.dronesService.markBroken(user.id, markBrokenDto);
  }

  @Get('current-order')
  @Roles(UserRole.DRONE)
  @ApiOperation({ summary: 'Get details of currently assigned order (Drone only)' })
  async getCurrentOrder(@CurrentUser() user: any) {
    return this.dronesService.getCurrentOrder(user.id);
  }
}
