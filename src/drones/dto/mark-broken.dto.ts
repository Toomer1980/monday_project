import { IsString } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class MarkBrokenDto {
  @ApiProperty()
  @IsString()
  reason: string;
}
