import { IsString, IsNotEmpty } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class GrabOrderDto {
  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  orderId: string;
}
