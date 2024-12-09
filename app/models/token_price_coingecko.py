import copy
import time
import datetime


class TokenPriceCoingecko:
    def __init__(self, _id=''):
        self.id = _id
        self.address = ''
        self.chainId = ''
        self.priceChangeLogs = dict()

    @classmethod
    def from_dict(cls, json_dict: dict):
        id_ = json_dict['_id']
        token_price_coingecko = TokenPriceCoingecko(id_)
        token_price_coingecko.address = json_dict['address']
        token_price_coingecko.chainId = json_dict['chainId']
        token_price_coingecko.priceChangeLogs = json_dict['priceChangeLogs']

        return token_price_coingecko

    def to_dict(self):
        return copy.deepcopy(self.__dict__)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

