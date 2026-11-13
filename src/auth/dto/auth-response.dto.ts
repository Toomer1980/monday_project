import { ApiProperty } from '@nestjs/swagger';

export class AuthResponseDto {
  @ApiProperty()
  access_token: string;

  @ApiProperty()
  user: {
    id: string;
    name: string;
    role: string;
  };

  @ApiProperty({ required: false, description: 'Drone ID (only included for DRONE users)' })
  droneId?: string;
}
