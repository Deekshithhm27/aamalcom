odoo.define('visa_process.document_preview', function (require) {
    'use strict';

    var core = require('web.core');
    var FormRenderer = require('web.FormRenderer');
    var fieldRegistry = require('web.field_registry');

    var QWeb = core.qweb;

    var FieldBinaryPreview = fieldRegistry.get('binary').extend({
        supportedFieldTypes: ['binary'],
        template: 'FieldBinaryPreview',
    });

    FormRenderer.include({
        _renderField: function (node) {
            var $el = this._super.apply(this, arguments);
            if (node.tag === 'field' && node.attrs.widget === 'document_preview') {
                var field = this.state.fields[node.attrs.name];
                if (field && field.value) {
                    $el.replaceWith(QWeb.render('FieldBinaryPreview', {widget: field}));
                }
            }
            return $el;
        },
    });

    fieldRegistry.add('document_preview', FieldBinaryPreview);

    return FieldBinaryPreview;
});
