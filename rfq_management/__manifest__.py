{
    'name': 'Sales Purchase Updates',
    'author' : 'Abdulhadi',
    'website' : 'https://tctenterprise.com/',
    'category' : 'Sales Purchase Udpates',
    'summary' : 'Sales Price Update from Purchase Module.',
    'depends' : ['mail','sale_management','hr','sale','maintenance','base',],
    'data' : [
        'security/ir.models.access.csv',
        'data/product_price_template.xml',
        'views/product_summary.xml',
        'views/sale_summary.xml',

        # 'views/css.xml',


    ],
    'demo' :[],
    'qweb' :[],
    'assets': {
        'web.assets_backend': [
            # 'amc_management/static/src/css/custom_styles.css',
            # 'amc_management/static/src/components/**/*.js',
            # 'amc_management/static/src/components/**/*.xml',
            # 'amc_management/static/src/components/**/*.scss'
        ],

    },



}
