import copy


class MarketInfo:
    def __init__(self, _id=''):
        self.id = _id
        self.chain_id = ''
        self.address = ''
        self.impliedAPY = dict()
        self.ptToAsset = dict()
        self.ytToAsset = dict()
        self.tradingVolume = dict()

    @classmethod
    def from_dict(cls, json_dict: dict):
        id_ = json_dict['_id']
        market_info = MarketInfo(id_)
        market_info.chain_id = json_dict['chain_id']
        market_info.address = json_dict['address']
        market_info.impliedAPY = json_dict['impliedAPY']
        market_info.ptToAsset = json_dict['ptToAsset']
        market_info.ytToAsset = json_dict['ytToAsset']
        market_info.tradingVolume = json_dict['tradingVolume']

        return market_info

    def to_dict(self):
        return copy.deepcopy(self.__dict__)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

