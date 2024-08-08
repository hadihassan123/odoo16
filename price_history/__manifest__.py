{
    'name': 'Price History',
    'author' : 'Abdulhadi',
    'website' : 'https://tctenterprise.com/',
    'category' : 'Price History',
    'summary' : 'In products module it displays the price history of the product'
                'In purchase module it displays the least price details of the prodcuts present in purchase order line'
                ,
    'depends' : ['hr','sale','purchase','base',],
    'data' : [

        'security/ir.model.access.csv',
        'views/product_log_price.xml',
        'views/purchase_price_history.xml',

        # 'views/css.xml',


    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}




