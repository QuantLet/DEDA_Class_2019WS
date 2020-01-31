# -*- coding: utf-8 -*-
"""
Created on Thu Dec 5 12:19:36 2019

@author: David
"""

import pandas as pd

# =============================================================================
# Load Data Sources
# address, owner, category
# =============================================================================
wallets = pd.DataFrame()

adr_walletexplorer = pd.read_csv("../data/wallets_walletexplorer.csv", index_col=False)
wallets = wallets.append(adr_walletexplorer)

adr_bitinfocharts = pd.read_csv("../data/wallets_bitinfochart.csv", index_col=False)
wallets = wallets.append(adr_bitinfocharts)

adr_cryptoground = pd.read_csv("../data/wallets_cryptoground.csv", index_col=False)
wallets = wallets.append(adr_cryptoground)

adr_bitinfocharts_missing = pd.read_csv("../data/wallets_bitinfochart_no_numbers.csv", index_col=False)
wallets = wallets.append(adr_bitinfocharts_missing)

wallets = wallets.dropna()
wallets = wallets[['address', 'owner', 'category']]
wallets = wallets.drop_duplicates(subset='address')

# =============================================================================
# Recategorize specific categories
# =============================================================================
wallets.loc[wallets.owner == 'MiddleEarthMarketplace', 'category'] = 'Service'
wallets.loc[wallets.owner == 'AbraxasMarket', 'category'] = 'Service'
wallets.loc[wallets.owner == 'PandoraOpenMarket', 'category'] = 'Service'
wallets.loc[wallets.owner == 'AgoraMarket', 'category'] = 'Service'
wallets.loc[wallets.owner == 'SilkRoad2Market', 'category'] = 'Service'
wallets.loc[wallets.owner == 'BabylonMarket', 'category'] = 'Service'
wallets.loc[wallets.owner == 'SilkRoadMarketplace', 'category'] = 'Service'
wallets.loc[wallets.owner == 'CannabisRoadMarket', 'category'] = 'Service'
wallets.loc[wallets.owner == 'BlackBankMarket', 'category'] = 'Service'
wallets.loc[wallets.owner == 'EvolutionMarket', 'category'] = 'Service'
wallets.loc[wallets.owner == 'SheepMarketplace', 'category'] = 'Service'
wallets.loc[wallets.owner == 'BlueSkyMarketplace', 'category'] = 'Service'
wallets.loc[wallets.owner == 'Instawallet.org', 'category'] = 'Service'
wallets.loc[wallets.owner == 'BitElfin.com', 'category'] = 'Service'
wallets.loc[wallets.owner == 'Coin-Sweeper.com', 'category'] = 'Service'
wallets.loc[wallets.owner == 'CoinHub.cz', 'category'] = 'Service'
wallets.loc[wallets.owner == 'CoinHub.cz', 'category'] = 'Service'
wallets.loc[wallets.owner == 'CoinHub.cz', 'category'] = 'Service'

wallets.loc[wallets.owner == 'DiceBitco', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'Just-Dice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'CryptoBounty.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'Betcoins.net', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'BtcDice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'BetsOfBitco.in', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'PinballCoin.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'Playt.in', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'EveryDice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'BetcoinDice.tm', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'SuzukiDice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'Bitcoin-Roulette.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'DiceOnCrack.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'Ice-Dice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'DiceBitco.in', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'Justcoin.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'DaDice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'DaDice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'DaDice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'DaDice.com', 'category'] = 'Gambling'
wallets.loc[wallets.owner == 'Cloudbet.com', 'category'] = 'Gambling'

wallets.loc[wallets.owner == 'Comkort.com', 'category'] = 'Exchange'
wallets.loc[wallets.owner == 'Bitcash.cz', 'category'] = 'Exchange'
wallets.loc[wallets.owner == 'BitcoinWeBank.com', 'category'] = 'Exchange'
wallets.loc[wallets.owner == 'BtcExchange.ro', 'category'] = 'Exchange'
wallets.loc[wallets.owner == 'MasterXchange.com', 'category'] = 'Exchange'
wallets.loc[wallets.owner == 'Crypto-Trade.com', 'category'] = 'Exchange'
wallets.loc[wallets.owner == 'Coin.mx', 'category'] = 'Exchange'
wallets.loc[wallets.owner == 'MintPal.com', 'category'] = 'Exchange'

wallets.loc[wallets.owner == 'ASICMiner', 'category'] = 'Pools'
wallets.loc[wallets.owner == 'MinersCenter.com', 'category'] = 'Pools'
wallets.loc[wallets.owner == 'CryptcoMiner.com', 'category'] = 'Pools'
wallets.loc[wallets.owner == 'Cryptomine.io', 'category'] = 'Pools'
wallets.loc[wallets.owner == '50BTC.com', 'category'] = 'Pools'
wallets.loc[wallets.owner == 'Polmine.pl', 'category'] = 'Pools'
wallets.loc[wallets.owner == 'bitmain.com', 'category'] = 'Pools'
wallets.loc[wallets.owner == 'F2Pool', 'category'] = 'Pools'

wallets.loc[wallets.owner == 'BitLaunder.com', 'category'] = 'Mixer'
wallets.loc[wallets.owner == 'HelixMixer', 'category'] = 'Mixer'
wallets.loc[wallets.owner == 'BitcoinFog', 'category'] = 'Mixer'

#change specific owner and category values
wallets.loc[wallets.owner == 'Xapo.com-2', 'owner'] = 'Xapo.com'
wallets.loc[wallets.owner == 'Bitfinex.com', 'owner'] = 'Bitfinex'
wallets.loc[wallets.owner == 'DPR Seized Coins 2', 'category'] = 'Service'
wallets.loc[wallets.owner == 'F2Pool', 'category'] = 'Pools'
wallets.loc[wallets.owner == 'HaoBTC.com', 'category'] = 'Exchange'
wallets.loc[wallets.owner == 'Xapo.com', 'category'] = 'Exchange'
wallets.loc[wallets.category == 'Pools', 'category'] = 'Mining'
wallets.loc[wallets.category == 'Services', 'category'] = 'Service'
wallets.loc[wallets.owner == 'Xapo.com-2', 'owner'] = 'Xapo.com'
wallets.loc[wallets.owner == 'BTCC.com-old2', 'owner'] = 'BTCC.com'
wallets.loc[wallets.owner == 'BTCC.com-old', 'owner'] = 'BTCC.com'

#Change duplicate name
wallets.loc[wallets['owner'].str.contains('HelixMixer'), 'owner'] = 'HelixMixer'
wallets.loc[wallets['owner'].str.contains('Bitstamp'), 'owner'] = 'Bitstamp'
wallets.loc[wallets['owner'].str.contains('BitPay.com'), 'owner'] = 'BitPay.com'
wallets.loc[wallets['owner'].str.contains('Bitfinex'), 'owner'] = 'Bitfinex'
wallets.loc[wallets['owner'].str.contains('Binance'), 'owner'] = 'Binance'
wallets.loc[wallets['owner'].str.contains('Cryptsy'), 'owner'] = 'Cryptsy'
wallets.loc[wallets['owner'].str.contains('Coincheck'), 'owner'] = 'Coincheck'
wallets.loc[wallets['owner'].str.contains('Xapo.com'), 'owner'] = 'Xapo.com'
wallets.loc[wallets['owner'].str.contains('BTCC.com'), 'owner'] = 'BTCC.com'
wallets.loc[wallets['owner'].str.contains('Poloniex'), 'owner'] = 'Poloniex'
wallets.loc[wallets['owner'].str.contains('Coincheck'), 'owner'] = 'Coincheck'

#Remove Historic
wallets = wallets[wallets['category'] != 'Historic']


# =============================================================================
# Export data to CSV
# =============================================================================
wallet_owners = pd.DataFrame()
wallet_owners = wallets.groupby(['owner', 'category']).agg(['count'], as_index=False).reset_index()
wallet_owners.columns = ['owner', 'category', 'count']
wallet_owners.to_csv("btc_wallets_owner.csv", index = False)

#Export to csv
wallets.to_csv("btc_wallets.csv", index = False)

