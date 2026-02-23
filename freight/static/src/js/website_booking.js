odoo.define('booking_website.booking_website', [], function (require) {
'use strict';
// require('web.dom_ready');
$(document).ready(function ()
	{
	    $('#ocean_div').hide();
	    $('#land_div').hide();
	    $('#dng_info').hide();
	    $('#danger_info').hide();
	    $('#dng_info').hide();
	    $('input[type=datetime-local][name=date]').change(function() {
	        console.log("THISSSSSSSSSSS", this,this.value);
	        $('#new_date').val(this.value);
	    });
//        $( "#date_start" ).datepicker({changeMonth: true,
//                                        changeYear: true,
//                                        changeHour: true,
//                                        changeMinute: true,
//                                        dateFormat: "dd/mm/yy-H:M"   });
	    $('input[type=radio][name=transport]').change(function() {
            if (this.value == 'air') {
                console.log("AIR");
                $('#ocean_div').hide();
	            $('#land_div').hide();



	            $('#air_lbl_1').show()
	            $('#air_data_1').show()
	            $('#air_lbl_2').show()
	            $('#air_data_2').show()

	            $('#ocean_lbl_1').hide()
	            $('#ocean_data_1').hide()
	            $('#ocean_lbl_2').hide()
	            $('#ocean_data_2').hide()

	            $('#land_lbl_1').hide()
	            $('#land_data_1').hide()
	            $('#land_lbl_2').hide()
	            $('#land_data_2').hide()

            }
            else if (this.value == 'ocean') {
                console.log("OCEAN");
                $('#ocean_div').show();
	            $('#land_div').hide();

	            $('#air_lbl_1').hide()
	            $('#air_data_1').hide()
	            $('#air_lbl_2').hide()
	            $('#air_data_2').hide()
				$('#airline').prop('required',false);

	            $('#ocean_lbl_1').show()
	            $('#ocean_data_1').show()
	            $('#ocean_lbl_2').show()
	            $('#ocean_data_2').show()

                $('#land_lbl_1').hide()
	            $('#land_data_1').hide()
	            $('#land_lbl_2').hide()
	            $('#land_data_2').hide()


            }
            else if (this.value == 'land') {
                console.log("LAND");
                $('#ocean_div').hide();
	            $('#land_div').show();




	            $('#air_lbl_1').hide()
	            $('#air_data_1').hide()
	            $('#air_lbl_2').hide()
	            $('#air_data_2').hide()
				$('#airline').prop('required',false);

	            $('#ocean_lbl_1').hide()
	            $('#ocean_data_1').hide()
	            $('#ocean_lbl_2').hide()
	            $('#ocean_data_2').hide()

	            $('#land_lbl_1').show()
	            $('#land_data_1').show()
	            $('#land_lbl_2').show()
	            $('#land_data_2').show()
	            
	            $('#trucker').trigger('change')

            }
        });

        $('input[type=checkbox][name=danger]').change(function() {
            var a = $('#danger').is(":checked");
            if ($('#danger').is(":checked")){
                $('#danger_info').show();
                $('#dng_info').show();
                $("#dg_bool").after("<br />");
                $("#dng_info").after("<br />");
                $(".lbl_move_type").css("margin-top","40px")
                $("#danger").after("<br />");
            }
            else{
                $('#danger_info').hide();
                $('#dng_info').hide();
                $("#dng_info").next("br").remove();
                $("#dg_bool").next("br").remove();
                $(".lbl_move_type").css("margin-top","0px")
                $("#danger").next("br").remove();
            }
        });
        
        $('#trucker').change(function(){
            var trucker_number = $('#trucker').find(":selected").attr('data-truck_number')
            $("#trucker_number").val(trucker_number)
        
        })
    });

});
