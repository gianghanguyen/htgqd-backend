# from sanic import Blueprint, Request
# from sanic import exceptions
# from sanic.response import json
# from sanic_ext import openapi, validate
# from collections import OrderedDict

# from app.databases.redis_cached import get_cache, set_cache
# from app.models.project import AirdropInfoQuery, WalletListByFilterQuery
# from app.utils.logger_utils import get_logger

# from app.databases.dex_nft_mongodb import DexNftMongoDB
# from app.databases.klg_mongodb import KLGMongoDB

# TOKEN_PRICE_COINGECKO_NUM = 30
# MARKET_INFO_NUM = 720

# logger = get_logger('Wallet Airdrop Info blueprint')

# wallet_airdrop_info_bp = Blueprint('airdrop_info', url_prefix='/wallet-airdrop-info')


# @wallet_airdrop_info_bp.route('')
# @openapi.definition(
#     summary="Get wallet airdrop information",
#     tag="Airdrop Information"
# )
# @openapi.parameter("wallet", description="Wallet Address", location="query", required=True)
# @validate(query=AirdropInfoQuery)
# async def get_wallet_airdrop_info(request: Request, query: AirdropInfoQuery):

#     wallet = query.wallet.lower()

#     key = wallet
#     async with request.app.ctx.redis as r:
#         wallet_airdrop_info = await get_cache(r, 'wallet_airdrop_info_' + key)
#         if wallet_airdrop_info is None:
#             _dex_nft_db: DexNftMongoDB = request.app.ctx.dex_nft_db
#             wallet_airdrop_info_objs = _dex_nft_db.get_wallet_airdrop_info(filter_={
#                 'wallet': wallet
#             })
#             if len(wallet_airdrop_info_objs) > 0:
#                 wallet_airdrop_info = wallet_airdrop_info_objs[0].to_dict()
#             else:
#                 raise exceptions.NotFound(
#                     f"Could not find wallet {query.wallet} airdrop info"
#                 )
#             await set_cache(r, 'wallet_airdrop_info_' + key, wallet_airdrop_info)

#     return json({
#         query.wallet: wallet_airdrop_info
#     })

# @wallet_airdrop_info_bp.route('/check-trava-user')
# @openapi.definition(
#     summary="Check Trava user",
#     tag="Airdrop Information"
# )
# @openapi.parameter("wallet", description="Wallet Address", location="query", required=True)
# @validate(query=AirdropInfoQuery)
# async def check_trava_user(request: Request, query: AirdropInfoQuery):

#     wallet = query.wallet.lower()

#     key = wallet
#     async with request.app.ctx.redis as r:
#         trava_user = await get_cache(r, 'trava_user_' + key)
#         if trava_user is None:
#             _klg_db: KLGMongoDB = request.app.ctx.klg_db
#             trava_user_obj = _klg_db.get_wallet_klg(filter_={
#                 'tags': 'trava_users', 
#                 'address': wallet
#             })
#             if trava_user_obj is not None:
#                 trava_user = trava_user_obj.to_dict()['address']
#             else:
#                 trava_user = ''
#             await set_cache(r, 'trava_user_' + key, trava_user)
    
#     if trava_user == '':
#         return json(None)

#     return json({
#         'address': trava_user
#     })

# @wallet_airdrop_info_bp.route('/wallet-list-by-filter')
# @openapi.definition(
#     summary="Get wallet list by filter",
#     tag="Airdrop Information"
# )
# @openapi.parameter("liquidityVolumeCamelot", description="Liquidity Volume Camelot", location="query", required=False)
# @openapi.parameter("liquidityVolumeUniswap", description="Liquidity Volume Uniswap", location="query", required=False)
# @openapi.parameter("liquidityVolumePancakeswap", description="Liquidity Volume Pancakeswap", location="query", required=False)
# @openapi.parameter("tradingVolumeCamelot", description="Trading Volume Camelot", location="query", required=False)
# @openapi.parameter("tradingVolumeUniswap", description="Trading Volume Uniswap", location="query", required=False)
# @openapi.parameter("tradingVolumePancakeswap", description="Trading Volume Pancakeswap", location="query", required=False)
# @openapi.parameter("GRAILBalanceInUSD", description="GRAIL Balance In USD", location="query", required=False)
# @openapi.parameter("UNIBalanceInUSD", description="UNI Balance In USD", location="query", required=False)
# @openapi.parameter("CAKEBalanceInUSD", description="CAKE Balance In USD", location="query", required=False)
# @openapi.parameter("page", description="Page", location="query", required=False)
# @validate(query=WalletListByFilterQuery)
# async def get_wallet_list_by_filter(request: Request, query: WalletListByFilterQuery):
    
#     page = query.page
#     page_size = query.pageSize
#     wallet_query = OrderedDict(query)
#     wallet_query.pop('pageSize')
#     wallet_query.pop('page')
    
#     key = ''.join(['1' if value else '0' for value in wallet_query.values()])
#     async with request.app.ctx.redis as r:
#         wallet_list_by_filter = await get_cache(r, 'wallet_list_by_filter_' + str(page) + '_' + key)
#         if wallet_list_by_filter is None:
#             wallet_filter = dict()
#             for key, value in wallet_query.items():
#                 if value is True:
#                     wallet_filter[key] = {"$exists": True}
#             _dex_nft_db: DexNftMongoDB = request.app.ctx.dex_nft_db
#             wallet_objs = _dex_nft_db.get_wallet_list(filter_=wallet_filter, page_size=page_size, page=page)
#             wallet_list_by_filter = dict()
#             for wallet_obj in wallet_objs:
#                 wallet_dict = wallet_obj.to_dict()
#                 wallet_list_by_filter[wallet_obj.wallet] = dict()
#                 for key in wallet_filter.keys():
#                     wallet_list_by_filter[wallet_obj.wallet][key] = wallet_dict[key]
#             await set_cache(r, 'wallet_list_by_filter_' + str(page) + '_' + key, wallet_list_by_filter)
        
#         total_docs = await get_cache(r, 'total_docs_wallet_list' + key)
#         if total_docs is None:
#             wallet_filter = dict()
#             for key, value in wallet_query.items():
#                 if value is True:
#                     wallet_filter[key] = {"$exists": True}
#             _dex_nft_db: DexNftMongoDB = request.app.ctx.dex_nft_db
#             total_docs = _dex_nft_db.get_total_docs_wallet_list(filter_=wallet_filter)
#             await set_cache(r, 'total_docs_wallet_list' + key, total_docs)
        
#         current_page_range = str(page_size*(page-1)+1) + ' - ' + str(page_size*page)

#     return json({
#         'totalDocsOfQuery': total_docs,
#         'currentPageRange': current_page_range,
#         'walletList': wallet_list_by_filter
#     })