"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DronesController = void 0;
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const drones_service_1 = require("./drones.service");
const current_user_decorator_1 = require("../common/decorators/current-user.decorator");
const roles_decorator_1 = require("../common/decorators/roles.decorator");
const user_role_enum_1 = require("../common/enums/user-role.enum");
const update_location_dto_1 = require("./dto/update-location.dto");
const grab_order_dto_1 = require("./dto/grab-order.dto");
const mark_delivered_dto_1 = require("./dto/mark-delivered.dto");
const mark_failed_dto_1 = require("./dto/mark-failed.dto");
const mark_broken_dto_1 = require("./dto/mark-broken.dto");
let DronesController = class DronesController {
    dronesService;
    constructor(dronesService) {
        this.dronesService = dronesService;
    }
    async reserveJob(user) {
        return this.dronesService.reserveJob(user.id);
    }
    async grabOrder(user, grabOrderDto) {
        return this.dronesService.grabOrder(user.id, grabOrderDto.orderId);
    }
    async updateLocation(user, updateLocationDto) {
        return this.dronesService.updateLocation(user.id, updateLocationDto);
    }
    async markDelivered(user, markDeliveredDto) {
        return this.dronesService.markDelivered(user.id, markDeliveredDto.orderId);
    }
    async markFailed(user, markFailedDto) {
        return this.dronesService.markFailed(user.id, markFailedDto);
    }
    async markBroken(user, markBrokenDto) {
        return this.dronesService.markBroken(user.id, markBrokenDto);
    }
    async getCurrentOrder(user) {
        return this.dronesService.getCurrentOrder(user.id);
    }
};
exports.DronesController = DronesController;
__decorate([
    (0, common_1.Post)('reserve-job'),
    (0, roles_decorator_1.Roles)(user_role_enum_1.UserRole.DRONE),
    (0, swagger_1.ApiOperation)({ summary: 'Reserve an available job (Drone only)' }),
    __param(0, (0, current_user_decorator_1.CurrentUser)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], DronesController.prototype, "reserveJob", null);
__decorate([
    (0, common_1.Post)('grab-order'),
    (0, roles_decorator_1.Roles)(user_role_enum_1.UserRole.DRONE),
    (0, swagger_1.ApiOperation)({ summary: 'Grab/pickup an assigned order (Drone only)' }),
    __param(0, (0, current_user_decorator_1.CurrentUser)()),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object, grab_order_dto_1.GrabOrderDto]),
    __metadata("design:returntype", Promise)
], DronesController.prototype, "grabOrder", null);
__decorate([
    (0, common_1.Post)('heartbeat'),
    (0, roles_decorator_1.Roles)(user_role_enum_1.UserRole.DRONE),
    (0, swagger_1.ApiOperation)({ summary: 'Update location and get status (Drone only)' }),
    __param(0, (0, current_user_decorator_1.CurrentUser)()),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object, update_location_dto_1.UpdateLocationDto]),
    __metadata("design:returntype", Promise)
], DronesController.prototype, "updateLocation", null);
__decorate([
    (0, common_1.Post)('mark-delivered'),
    (0, roles_decorator_1.Roles)(user_role_enum_1.UserRole.DRONE),
    (0, swagger_1.ApiOperation)({ summary: 'Mark order as delivered (Drone only)' }),
    __param(0, (0, current_user_decorator_1.CurrentUser)()),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object, mark_delivered_dto_1.MarkDeliveredDto]),
    __metadata("design:returntype", Promise)
], DronesController.prototype, "markDelivered", null);
__decorate([
    (0, common_1.Post)('mark-failed'),
    (0, roles_decorator_1.Roles)(user_role_enum_1.UserRole.DRONE),
    (0, swagger_1.ApiOperation)({ summary: 'Mark order as failed (Drone only)' }),
    __param(0, (0, current_user_decorator_1.CurrentUser)()),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object, mark_failed_dto_1.MarkFailedDto]),
    __metadata("design:returntype", Promise)
], DronesController.prototype, "markFailed", null);
__decorate([
    (0, common_1.Post)('mark-broken'),
    (0, roles_decorator_1.Roles)(user_role_enum_1.UserRole.DRONE),
    (0, swagger_1.ApiOperation)({ summary: 'Mark drone as broken and create order handoff (Drone only)' }),
    __param(0, (0, current_user_decorator_1.CurrentUser)()),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object, mark_broken_dto_1.MarkBrokenDto]),
    __metadata("design:returntype", Promise)
], DronesController.prototype, "markBroken", null);
__decorate([
    (0, common_1.Get)('current-order'),
    (0, roles_decorator_1.Roles)(user_role_enum_1.UserRole.DRONE),
    (0, swagger_1.ApiOperation)({ summary: 'Get details of currently assigned order (Drone only)' }),
    __param(0, (0, current_user_decorator_1.CurrentUser)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], DronesController.prototype, "getCurrentOrder", null);
exports.DronesController = DronesController = __decorate([
    (0, swagger_1.ApiTags)('Drones'),
    (0, swagger_1.ApiBearerAuth)(),
    (0, common_1.Controller)('drones'),
    __metadata("design:paramtypes", [drones_service_1.DronesService])
], DronesController);
//# sourceMappingURL=drones.controller.js.map