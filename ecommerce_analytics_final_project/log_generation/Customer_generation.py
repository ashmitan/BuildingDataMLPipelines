from faker import Faker
import pandas as pd
import numpy as np
import os

def create_customers():
    cust_lst = []
    faker = Faker()
    for i in range(700):
        cust_lst.append(faker.simple_profile(sex=None))

    DFC = pd.DataFrame(cust_lst)
    DFC["Cust_id"] = DFC.index.values
    DFC["Probability"] = np.random.dirichlet(np.ones(700), size=1)[0]
    return DFC

# # prepares probabilites of already created product data
# def product():
#     dfp = pd.read_csv("Product.csv")
#     dfp["prod_id"] = dfp.index.values
#     dfp["Probability"] = np.random.dirichlet(np.ones(42), size=1)[0]
#     return dfp




DFC = create_customers()
DFC.to_csv("Customers.csv")

# DFP=  product()
# DFP.to_csv("Products.csv")

