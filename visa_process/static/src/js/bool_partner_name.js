odoo.define('your_module.custom_boolean_widget', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    var FieldBoolean = basic_fields.FieldBoolean;

    var FieldCustomBoolean = FieldBoolean.extend({
        _render: function () {
            this._super.apply(this, arguments);
            var self = this;
            this.updateCustomBooleanDisplay();

            this.$el.on('click', function () {
                self._setValue(!self.value);
                self.updateCustomBooleanDisplay();
            });

            this.fieldManager.on('field_changed:client_id', this, function () {
                self.updateCustomBooleanDisplay();
            });
        },

        updateCustomBooleanDisplay: function () {
            if (this.recordData.client_id) {
                this.$el.text("Partner: " + this.recordData.client_id.name);
            } else {
                this.$el.text("No Partner Selected");
            }
        },
    });

    field_registry.add('custom_boolean', FieldCustomBoolean);

});
