import { ApiProperty } from '@nestjs/swagger';
import { OrderStatus } from '../../common/enums/order-status.enum';

export class OrderResponseDto {
  @ApiProperty()
  id: string;

  @ApiProperty()
  orderNumber: string;

  @ApiProperty()
  status: OrderStatus;

  @ApiProperty()
  originLat: number;

  @ApiProperty()
  originLng: number;

  @ApiProperty()
  originAddress: string;

  @ApiProperty()
  destinationLat: number;

  @ApiProperty()
  destinationLng: number;

  @ApiProperty()
  destinationAddress: string;

  @ApiProperty({ required: false })
  currentDroneLat?: number;

  @ApiProperty({ required: false })
  currentDroneLng?: number;

  @ApiProperty({ required: false })
  estimatedTimeMinutes?: number;

  @ApiProperty()
  createdAt: Date;
}
