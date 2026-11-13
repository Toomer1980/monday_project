import { IsString, IsNotEmpty } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class MarkDeliveredDto {
  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  orderId: string;
}
