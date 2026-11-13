import { UserRole } from '../../common/enums/user-role.enum';
export declare class RegisterDto {
    name: string;
    password: string;
    userType: UserRole;
}
