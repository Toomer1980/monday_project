import { IsEnum } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';
import { DroneStatus } from '../../common/enums/drone-status.enum';

export class MarkDroneStatusDto {
  @ApiProperty({ enum: DroneStatus })
  @IsEnum(DroneStatus)
  status: DroneStatus;
}
