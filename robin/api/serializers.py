# -*- coding: utf-8 -*-
import logging

from rest_framework import serializers

from statistics.models import Repository, Pull, Commit, Comment
# from accounts.models import Merchant
# from products.models import Product
# from .api_helpers import query_date_validator, merchant_products_unique_ids

logger = logging.getLogger(__name__)


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ('pk','owner', 'repo')


# class ProductSerializer(serializers.ModelSerializer):
#     key_word = serializers.CharField(required=False)

#     class Meta:
#         model = Product
#         fields = ('product_name', 'unique_id', 'key_word', 'sales_time')


# class MerchantSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Merchant
#         fields = ('merchant_number', 'merchant_name', 'tax_type')

#     def validate(self, data):
#         if not Merchant.obejcts.is_exist(merchant_number=data['merchant_number']):
#             raise serializers.ValidationError("merchant does not exist.")
#         return data


# class MerchantProductsSerializer(serializers.Serializer):
#     merchant_number = serializers.CharField(required=True)
#     query_start_date = serializers.DateField(required=True)
#     query_end_date = serializers.DateField(required=True)

#     class Meta:
#         fields = ('merchant_number', 'query_start_date', 'query_end_date')

#     def validate(self, data):
#         unique_ids = merchant_products_unique_ids(data['merchant_number'])
#         for unique_id in unique_ids:
#             query_date_validator(
#                 unique_id, data['query_start_date'], data['query_end_date'])
#         return data


# class ProductSalesSerializer(serializers.Serializer):
#     unique_id = serializers.CharField(required=True)
#     query_start_date = serializers.DateField(required=True)
#     query_end_date = serializers.DateField(required=True)

#     class Meta:
#         fields = ('unique_id', 'query_start_date', 'query_end_date')

#     def validate(self, data):
#         # 找到每个unique_id对应的合同
#         for unique_id in set(data['unique_id'].split(',')):
#             query_date_validator(
#                 unique_id, data['query_start_date'], data['query_end_date'])

#         return data


# class ProductMonthlySaleSerializer(serializers.Serializer):
#     query_start_date = serializers.DateField(required=True)
#     query_end_date = serializers.DateField(required=True)

#     class Meta:
#         fields = ('query_start_date', 'query_end_date')

#     # add validation?
