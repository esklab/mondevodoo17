odoo.define('pos_custom_floor_background.FloorScreen', function(require) {
    'use strict';

    const FloorScreen = require('pos_restaurant.FloorScreen');
    const { patch } = require('web.utils');

    patch(FloorScreen.prototype, 'pos_custom_floor_background.FloorScreen', {
        onPatched() {
            this._super(...arguments);
            this._updateBackground();
        },

        onMounted() {
            this._super(...arguments);
            this._updateBackground();
        },

        selectFloor(floor) {
            this._super(...arguments);
            this._updateBackground();
        },

        _updateBackground() {
            if (this.activeFloor && this.activeFloor.background_image) {
                this.floorMapRef.el.style.backgroundImage = 
                    `url('/web/image?model=restaurant.floor&id=${this.activeFloor.id}&field=background_image')`;
                this.floorMapRef.el.style.backgroundSize = 'cover';
                this.floorMapRef.el.style.backgroundPosition = 'center';
                this.floorMapRef.el.style.backgroundRepeat = 'no-repeat';
                this.floorMapRef.el.style.backgroundColor = '';
            } else {
                this.floorMapRef.el.style.backgroundImage = '';
                this.floorMapRef.el.style.background = this.state.floorBackground;
            }
        }
    });
});