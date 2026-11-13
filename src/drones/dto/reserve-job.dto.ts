import { ApiProperty } from '@nestjs/swagger';

export class ReserveJobResponseDto {
  @ApiProperty()
  success: boolean;

  @ApiProperty()
  order: any;

  @ApiProperty()
  message: string;
}
