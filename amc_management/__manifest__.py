{
    'name': 'AMC Management',
    'author' : 'Abdulhadi',
    'website' : 'https://tctenterprise.com/',
    'version': '16.0.1.0.0',
    'category' : 'Amc',
    'summary' : 'An Annual Maintenance Contract (AMC) is a type of service agreement that provides ongoing maintenance and support for a specific equipment or asset. It is typically used to ensure that the equipment or asset is kept in good working order and is regularly serviced and inspected.',
    'depends' : ['mail','sale_management','hr','sale','maintenance','board','base','web','website_slides'],
    'data' : [
        'security/ir.model.access.csv',
        'wizard/cancel_ticket_view.xml',
        'data/sequence.xml',
        'data/scheduledaction.xml',
        'data/duration.xml',
        'data/auto_cancel.xml',
        'data/second_escalation.xml',
        'data/work_in_progress.xml',
        'data/waiting_for_vendor.xml',
        'data/resolved.xml',
        'data/amc_assigned.xml',
        'data/waiting_for_customer.xml',
        'data/first_escalation.xml',
        'data/helpdesk_template.xml',
        'data/mail_template_data.xml',
        'views/menu.xml',
        # 'views/dashboard.xml',
        'views/amc.xml',
        # 'views/contracts.xml',
        'views/onlyamc.xml',
        'views/liveamc.xml',
        'views/expired_amc.xml',
        'views/service_desk.xml',
        'views/open_tickets.xml',
        'views/assigned_tickets.xml',
        'views/wip_tickets.xml',
        'views/resolved_tickets.xml',
        'views/wfv_tickets.xml',
        'views/wfc_tickets.xml',
        'views/done_tickets.xml',
        'views/sale_order.xml',
        'views/sla_monitor.xml',
        'views/upload_asset.xml',
        'views/passfields.xml',
        # 'views/knowledge_base_product.xml',
        'views/domain.xml',
        'views/brand.xml',
        'views/category.xml',
        'views/knowledge_base.xml',
        'views/eng.xml',
        'views/product_summary.xml',
        'views/sale_summary.xml',

        # 'views/css.xml',
        'report/amc_template.xml',
        'report/report.xml',

    ],
    'demo' :[],
    'qweb' :[],
    'assets': {
        'web.assets_backend': [
            'amc_management/static/src/css/custom_styles.css',
        ],

    'images': ['static/description/ong.png'],
    'license': 'OPL-1',   
    'installable': True,
    'auto_install': False,
    'application': True,
    },



}
