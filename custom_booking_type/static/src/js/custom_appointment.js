odoo.define('custom_booking_type.custom_appointment', function(require) {
    "use strict";

    $(document).ready(function () {
        $('#appointmentType').change(function () {
            let appointmentTypeId = $(this).val();
            let slotSelect = $('#slot');
            let resourceSelect = $('#resource');

            slotSelect.empty().append('<option value="">Sélectionner un créneau</option>');
            resourceSelect.empty().append('<option value="">Sélectionner une ressource</option>');

            if (appointmentTypeId) {
                $.get('/appointment/get_slots', { appointment_type_id: appointmentTypeId }, function (slots) {
                    slots.forEach(slot => {
                        slotSelect.append(`<option value="${slot.id}" data-resource-id="${slot.resource_id.id}">${slot.name}</option>`);
                    });
                });
            }
        });

        $('#slot').change(function () {
            let selectedSlot = $(this).find(':selected');
            let resourceId = selectedSlot.data('resource-id');
            let resourceSelect = $('#resource');

            resourceSelect.empty().append('<option value="">Sélectionner une ressource</option>');
            if (resourceId) {
                resourceSelect.append(`<option value="${resourceId}" selected>${selectedSlot.text()}</option>`);
            }
        });
    });
});
