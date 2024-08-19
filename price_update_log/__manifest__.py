{
    'name': 'Price Updation Log',
    'author' : 'Abdulhadi',
    'website' : 'https://tctenterprise.com/',
    'category' : 'Price Updation',
    'summary' : 'In products module, a new tab price update logs records the update in price ,cost and supplier price'
                'directly from sale order line. the updated values will also be relfected on product template model'
                ,
    'depends' : ['hr','sale','product','base',],
    'data' : [

        'security/ir.model.access.csv',
        'views/supplier_price.xml',
        'views/supplier_price_update_log.xml',
        # 'views/supp_log.xml',

        # 'views/css.xml',


    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}




