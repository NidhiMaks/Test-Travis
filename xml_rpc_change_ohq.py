import xmlrpclib

url = 'localhost:8069'
database = 'db_boss_new'
server = xmlrpclib.ServerProxy("http://" + url + "/xmlrpc/object")
password = 'a'

# Search product based on internal reference
user_input = 'Y'
# print 'lal alal a'
while user_input != 'N':
    user_input = raw_input(
        "Enter internal reference of the product:")
    product_ids = server.execute(database, 1, password, 'product.product',
                                 'search', [('default_code', '=', user_input)])
    if product_ids:
        #         Search stock quants for the product
        product_quant_ids = server.execute(database, 1, password,
                                           'stock.quant', 'search', [
                                               ('product_id',
                                                '=', product_ids[0])])
        location_id = server.execute(
            database, 1, password, 'stock.location', 'search',
            [('name', '=', 'Stock')])
        new_updated_quantity = int(
            raw_input("Enter the new on hand quantity:"))

        new_OHQTY = 0
        if product_quant_ids:
            total_OHQ = 0
            total_quants = len(product_quant_ids)
            for product_quant_id in product_quant_ids:
                current_OHQ = server.execute(
                    database, 1, password, 'stock.quant', 'read',
                    product_quant_id, ['qty'])['qty']
#                 if current_OHQ > 0:
                total_OHQ += current_OHQ
        if new_updated_quantity < total_OHQ:
            new_OHQTY = new_updated_quantity - total_OHQ
            new_quant_id = server.execute(database, 1, password,
                                          'stock.quant', 'create',
                                          {'product_id': product_ids[0],
                                           'location_id': location_id[0],
                                           'qty': new_OHQTY})
        else:
            new_OHQTY = new_updated_quantity - total_OHQ
            new_quant_id = server.execute(database, 1, password,
                                          'stock.quant', 'create',
                                          {'product_id': product_ids[0],
                                           'location_id': location_id[0],
                                           'qty': new_OHQTY})
# Based on updated quantity, calculate the average cost of the product if
# it is applicable
        product_fields = server.execute(database, 1, password,
                                        'product.product', 'read',
                                        product_ids[0], ['cost_method',
                                                         'standard_price',
                                                         'qty_available'])
        if product_fields['cost_method'] == 'average':
            old_average_cost = (product_fields['qty_available'] *
                                product_fields['standard_price'])
            new_average_cost = (new_OHQTY *
                                product_fields['standard_price'])
#             new_average_cost = (new_OHQTY*200)
            new_combined_qty = (product_fields['qty_available'] +
                                new_OHQTY)
            new_average_cost1 = old_average_cost + new_average_cost
            final_average_cost = new_average_cost1 / new_combined_qty
            server.execute(database, 1, password, 'product.product',
                           'write', product_ids[0], {
                               'standard_price': final_average_cost})
print "The script is ended"
