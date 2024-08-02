{
    'name': 'Segregated Summary for Sale Orders',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds segregated summary fields for storable products and services in sale orders.',
    'description': """
        This module enhances the sale order form by adding fields to display
        segregated summaries of storable products and services, including
        total costs and margins.
    """,
    'author': 'Abdulhadi',
        'website' : 'https://tctenterprise.com/',
    'depends': ['sale'],
    'data': [
        'views/segregated_summary.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
