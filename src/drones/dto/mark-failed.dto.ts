import { IsString } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class MarkFailedDto {
  @ApiProperty()
  @IsString()
  orderId: string;

  @ApiProperty()
  @IsString()
  reason: string;
}
