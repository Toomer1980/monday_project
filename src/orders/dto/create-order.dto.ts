import { IsString, IsNumber, IsNotEmpty, Min, Max } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateOrderDto {
  @ApiProperty({ example: 40.7128 })
  @IsNumber()
  @Min(-90)
  @Max(90)
  originLat: number;

  @ApiProperty({ example: -74.0060 })
  @IsNumber()
  @Min(-180)
  @Max(180)
  originLng: number;

  @ApiProperty({ example: '123 Main St, New York' })
  @IsString()
  @IsNotEmpty()
  originAddress: string;

  @ApiProperty({ example: 40.7589 })
  @IsNumber()
  @Min(-90)
  @Max(90)
  destinationLat: number;

  @ApiProperty({ example: -73.9851 })
  @IsNumber()
  @Min(-180)
  @Max(180)
  destinationLng: number;

  @ApiProperty({ example: '456 Broadway, New York' })
  @IsString()
  @IsNotEmpty()
  destinationAddress: string;
}
