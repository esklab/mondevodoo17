/** @odoo-module */
import { registry} from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted} = owl
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";

export class FreightDashboard extends Component {
    /**
     * Setup method to initialize required services and register event handlers.
     */
	setup() {
		this.action = useService("action");
		this.orm = useService("orm");
		this.rpc = this.env.services.rpc
		onWillStart(this.onWillStart);
		onMounted(this.onMounted);
	}
	/**
     * Event handler for the 'onWillStart' event.
     */
	async onWillStart() {
		await this.fetch_data();
	}
	 /**
     * Event handler for the 'onMounted' event.
     * Renders various components and charts after fetching data.
     */
	async onMounted() {
		// Render other components after fetching data
        this.graph();
        if(this.employee_data.operation_table.length){
            this.previewTable();
        }
        
	}

    fetch_data() {
		this.flag = 0
		var self = this;
		var def1 = jsonrpc('/get/tiles/data').then(function(result) {
			self.employee_data = result[0]
				
		});
		return $.when(def1);
	}

    action_my_profile(e) {
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("My Profile"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            res_id: this.employee_data.id,
            domain: [],
            context: {'edit': 'true'},
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'inline'
        }, options)
    }

    direct_shipment(e) {
        e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
        this.action.doAction({
            name: _t("Direct"),
            type: 'ir.actions.act_window',
            res_model: 'freight.operation',
            domain: [
                ["operation", "=", 'direct']
            ],
            context: {'search_default_operation': 'direct'},
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            search_view_id: this.employee_data.operation_search_view_id,
            target: 'current'
        }, options)
    }

    house_shipment(e) {
        e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
        this.action.doAction({
            name: _t("House"),
            type: 'ir.actions.act_window',
            res_model: 'freight.operation',
            domain: [
                ["operation", "=", 'house']
            ],
            context: {'search_default_operation': 'house'},
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            search_view_id: this.employee_data.operation_search_view_id,
            target: 'current'
        }, options)
    }

    master_shipment(e) {
        e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
        this.action.doAction({
            name: _t("Master"),
            type: 'ir.actions.act_window',
            res_model: 'freight.operation',
            domain: [
                ["operation", "=", 'master']
            ],
            context: {'search_default_operation': 'master'},
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            search_view_id: this.employee_data.operation_search_view_id,
            target: 'current'
        }, options)
    }

    action_invoice(e) {
        e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
        this.action.doAction({
            name: _t("Invoices"),
            type: 'ir.actions.act_window',
            res_model: 'account.move',
            domain: [
                ["move_type", "=", 'out_invoice']
            ],
            context: {'search_default_move_type': 'out_invoice'},
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            search_view_id: this.employee_data.invoice_search_view_id,
            target: 'current'
        }, options)
    }

    action_bills(e) {
        e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
        this.action.doAction({
            name: _t("Vendor Bills"),
            type: 'ir.actions.act_window',
            res_model: 'account.move',
            domain: [
                ["move_type", "=", 'in_invoice']
            ],
            context: {'search_default_move_type': 'in_invoice'},
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            search_view_id: this.employee_data.invoice_search_view_id,
            target: 'current'
        }, options)
    }

    action_ports(e) {
        e.stopPropagation();
		e.preventDefault();
		var options = {
			on_reverse_breadcrumb: this.on_reverse_breadcrumb,
		};
        this.action.doAction({
            name: _t("Ports"),
            type: 'ir.actions.act_window',
            res_model: 'freight.port',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            search_view_id: this.employee_data.freight_port_search_id,
            target: 'current'
        }, options)
    }

    generate_payroll_pdf(chart) {
        if (chart == 'bar'){
            var canvas = document.querySelector('#myChart');
        }
        else if (chart == 'pie') {
            var canvas = document.querySelector('#attendanceChart');
        }

        //creates image
        var canvasImg = canvas.toDataURL("image/jpeg", 1.0);
        var doc = new jsPDF('landscape');
        doc.setFontSize(20);
        doc.addImage(canvasImg, 'JPEG', 10, 10, 280, 150 );
        doc.save('report.pdf');
    }

    previewTable() {
        $('#operation_details').DataTable( {
            dom: 'Bfrtip',
            buttons: [
                'copy', 'csv', 'excel',
                {
                    extend: 'pdf',
                    footer: 'true',
                    orientation: 'landscape',
                    title:'Shipment Details',
                    text: 'PDF',
                    exportOptions: {
                        modifier: {
                            selected: true
                        }
                    }
                },
                {
                    extend: 'print',
                    exportOptions: {
                    columns: ':visible'
                    }
                },
            'colvis'
            ],
            columnDefs: [ {
                targets: -1,
                visible: false
            } ],
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            pageLength: 15,
        } );
    }

    // gives random color for charts
    getRandomColor() {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    graph() {
        var self = this
        var ctx = $('#myChart')
        // Fills the canvas with white background
        Chart.plugins.register({
            beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
            }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                //labels: ["January","February", "March", "April", "May", "June", "July", "August", "September",
                // "October", "November", "December"],
                labels: this.employee_data.operation_labels,
                datasets: [{
                    label: 'Operations',
                    data: this.employee_data.operation_dataset,
                    backgroundColor: bg_color_list,
                    borderColor: bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,this.employee_data.operation_dataset),
                            //min: 1000,
                            //max: 100000,
                            stepSize: this.employee_data.
                            operation_dataset.reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                            /this.employee_data.operation_dataset.length
                            }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'black'
                    }
                },
            },
        });
        //Pie Chart
        var piectx = $('#attendanceChart');
        bg_color_list = []
        for (var i=0;i<=this.employee_data.shipper_dataset.length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: this.employee_data.shipper_dataset,
                    backgroundColor: bg_color_list,
                    label: 'Attendance Pie'
                }],
                labels:this.employee_data.shipper_labels,
            },
            options: {
                responsive: true
            }
        });

    }
}
FreightDashboard.template = "FreightDashboard"
registry.category("actions").add("freight_dashboard", FreightDashboard)
