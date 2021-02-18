print("梦沙河 黄金🐍舰队 \ MIRAGE ARMADA v2.0.1\n")  # 2021.2.18
import requests
import random
import time
import logging
from logging import handlers
from mirage_config import CONFIG_TOTEM, CONFIG_heroEquipmentLevel, CONFIG_TREASURES, CONFIG_STEAMID, TREASURES_LIST, \
    TOTEM_LIST, HTTP_PROXY, ALLMIGHT, CONFIG_SPARCOIN, EQUIPMENT_LIST


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter('%(message)s'))
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')
        th.setFormatter(format_str)
        self.logger.addHandler(sh)
        self.logger.addHandler(th)


log = Logger('mirage_armada.log', level='info')

MIRAGE_DOMIAN = "http://online.api.mirage.woaiwandota2.com//"
UA = "Valve/Steam HTTP Client 1.0 (570)"
HEADERS = {
    'User-Agent': UA,
    'Accept': 'text/html,*/*;q=0.9',
    'Accept-Charset': 'ISO-8859-1,utf-8,*;q=0.7',
    'Accept-Encoding': 'gzip,identity,*;q=0167103119'
}
PROXIES = HTTP_PROXY
MAP_CODE = "mirage_of_the_fall"
ACTION_ARCHIVE_LOAD = "player/load_player"  # 获取游戏存档
ACTION_ARCHIVE_SAVE = "player/update_player"
ACTION_ARCHIVE_NEW_MATCH = "archive/new_match"  # 保存游戏存档
ACTION_ARCHIVE_TOTEM = "totem/update_totem"  # 图腾数据存档

ACTION_ACCOUNT_LOAD = "account/load_account"  # -- 读取账号晶石数据
ACTION_ACCOUNT_GET_RECHARGE_URL = "recharge/payment_url"  # -- 支付链接
ACTION_ACCOUNT_GET_RECHARGE_MENU = "recharge/payment_menu"  # -- 请求支付菜单,哪些是双倍
ACTION_ACCOUNT_UPDATE_ACCOUNT = "/account/update_account"  # -- 更新货币

ACTION_STORE_LOAD_GOODS_LIST = "store/load_goods_list"  # -- 获取商品列表
ACTION_STORE_LOAD_ACCOUNT = "store/load_account"  # -- 获取玩家商品存档
ACTION_STORE_PAY_GOODS = "store/pay_goods"  # -- 支付商品
ACTION_STORE_ADD_CURRENCY = "store/add_currency"  # -- 增加自定义货币 [每天都有一定上限，在服务端设置]
ACTION_STORE_USED_GOODS = "store/used_goods"  # -- 使用商品
ACTION_STORE_LOAD_EXCHANGE_LIST = "store/load_day_config"  # -- 获取兑换列表


class Armada:
    def __init__(self, sid):
        self.r = requests
        self.steamid = sid
        self.player = {}

        self.log = Logger(str(self.steamid) + ".log", level='info')

    def load_player(self):
        self.log.logger.info("<-------------load_Player------------->\n")
        data = {"steamId": self.steamid, "mapCode": MAP_CODE, "randomCode": self.random8int(),
                "serverKey": self.random64hex()}
        res = self.r.post(MIRAGE_DOMIAN + ACTION_ARCHIVE_LOAD, json=data, headers=HEADERS, proxies=PROXIES)
        self.player = res.json()

        if self.player['code'] == 200 and 'data' in self.player:
            log.logger.info(str(self.steamid) + " 存档读取成功!")
            with open(str(self.steamid) + ".json", "a+", encoding="utf-8") as pd:
                pd.write(str(time.time()) + " = " + res.text + "\n")
            self.log.logger.info("\n<-------------获取已有宝物------------->")
            tre = "\n"
            for i, d in enumerate(self.player['data']['treasures']):  # 遍历已有宝物
                if self.player['data']['treasures'][i] is not None:
                    tre += " | " + TREASURES_LIST[d['treasureId'] - 1][1]
            self.log.logger.info(tre)

            self.log.logger.info("\n<-------------获取图腾等级------------->")
            tt = ""
            for i, d in enumerate(TOTEM_LIST):
                tt += "\n" + TOTEM_LIST[d] + "：" + str(self.player['data']['totem'][d]) + " 级"
            self.log.logger.info(tt)  # 图腾

            self.log.logger.info("\n<-------------获取遗物等级------------->")
            eq = ""
            for i, d in enumerate(EQUIPMENT_LIST):
                eq += "\n" + EQUIPMENT_LIST[d] + "：" + str(self.player['data'][d]) + " 级"
            self.log.logger.info(eq)  # 遗物
        elif self.player['code'] == 200 and 'data' not in self.player:
            log.logger.info("未找到游戏存档，请先进行一场游戏!")
        else:
            log.logger.info(res.text)
            log.logger.info(str(self.steamid) + " 存档读取失败!")
        return

    def update_totem(self):
        self.log.logger.info("\n<-------------modify_TotemLevel------------->\n")
        totem = self.player['data']['totem']
        for i, d in enumerate(CONFIG_TOTEM):
            totem[d] = CONFIG_TOTEM[d]

        data = {"randomCode": self.random8int(), "rows": totem, "steamId": self.steamid,
                "mapCode": MAP_CODE, "serverKey": self.random64hex()}
        res = self.r.post(MIRAGE_DOMIAN + ACTION_ARCHIVE_TOTEM, json=data, headers=HEADERS, proxies=PROXIES)
        res_data = res.json()
        if res_data['code'] == 200:
            self.log.logger.info("修改图腾数据成功")
        else:
            self.log.logger.info(res.text)
            self.log.logger.info("修改图腾数据失败")
        return

    def update_player(self, modify_hel=False, modify_tre=False):
        self.log.logger.info("\n<-------------modify_Player------------->\n")
        p = self.player['data']
        if modify_tre:
            treasures = CONFIG_TREASURES
            random.shuffle(treasures)
        else:
            treasures = p['treasures']

        if modify_hel:
            hel = CONFIG_heroEquipmentLevel
        else:
            hel = p
        data = {"randomCode": self.random8int(),
                "rows": {"heroEquipmentArmor": hel['heroEquipmentArmor'],
                         "treasures": treasures,
                         "onceBoxNumber": p['onceBoxNumber'],
                         "heroEquipmentHead": hel['heroEquipmentHead'],
                         "compensationLevel": p['compensationLevel'], "mapRewardsCount": p['mapRewardsCount'],
                         "itemAdvancedMaterialsKey": p['itemAdvancedMaterialsKey'],
                         "heroEquipmentHeadExp": p['heroEquipmentHeadExp'],
                         "itemAdvancedMaterialsEyes": p['itemAdvancedMaterialsEyes'],
                         "itemAdvancedMaterialsCane": p['itemAdvancedMaterialsCane'], "killYanmo": p['killYanmo'],
                         "heroEquipmentSpeciaiweaponExp": p['heroEquipmentSpeciaiweaponExp'],
                         "allUniversalExp": p['allUniversalExp'], "mapExp": p['mapExp'], "passLevel": p['passLevel'],
                         "heroEquipmentMainweaponExp": p['heroEquipmentMainweaponExp'],
                         "itemCallMaterialsHeart": p['itemCallMaterialsHeart'],
                         "heroEquipmentArmorExp": p['heroEquipmentArmorExp'], "killBoss": p['killBoss'],
                         "heroEquipmentSpeciaiweapon": hel['heroEquipmentSpeciaiweapon'],
                         "itemAdvancedMaterialsJewelry": p['itemAdvancedMaterialsJewelry'],
                         "heroEquipmentLegguardExp": p['heroEquipmentLegguardExp'],
                         "heroEquipmentShoesExp": p['heroEquipmentShoesExp'],
                         "heroEquipmentLeg": hel['heroEquipmentLeg'],
                         "mapLevel": p['mapLevel'],
                         "heroEquipmentMainweapon": hel['heroEquipmentMainweapon'],
                         "itemAdvancedMaterialsZhui": p['itemAdvancedMaterialsZhui'], "relicsExp": p['relicsExp'],
                         "itemAdvancedMaterialsChochma": p['itemAdvancedMaterialsChochma'],
                         "universalExp": p['universalExp'], "heroEquipmentLegExp": p['heroEquipmentLegExp'],
                         "levelRewardsLists": p['levelRewardsLists'],
                         "itemCallMaterialsRighthand": p['itemCallMaterialsRighthand'],
                         "itemAdvancedMaterialsTianping": p['itemAdvancedMaterialsTianping'],
                         "itemCallMaterialsLefthand": p['itemCallMaterialsLefthand'],
                         "itemCallMaterialsEyes": p['itemCallMaterialsEyes'],
                         "itemCallMaterialsSoul": p['itemCallMaterialsSoul'],
                         "heroEquipmentShoes": hel['heroEquipmentShoes'],
                         "heroEquipmentLegguard": hel['heroEquipmentLegguard'],
                         "useHeroExp": p['useHeroExp']},
                "steamId": self.steamid,
                "mapCode": MAP_CODE,
                "serverKey": self.random64hex()}
        res = self.r.post(MIRAGE_DOMIAN + ACTION_ARCHIVE_SAVE, json=data, headers=HEADERS, proxies=PROXIES)
        res_data = res.json()
        if res_data['code'] == 200:
            self.log.logger.info("修改存档数据成功")
        else:
            self.log.logger.info(res.text)
            self.log.logger.info("修改存档数据失败")
        return

    def update_coin(self):
        # 修改💎数量，可以为负数
        self.log.logger.info("\n<-------------modify_SparCoin------------->\n")
        quantity = CONFIG_SPARCOIN
        data = {"randomCode": self.random8int(), "typeCoin": 1, "steamId": self.steamid, "mapCode": MAP_CODE,
                "quantity": quantity, "serverKey": self.random64hex()}
        res = self.r.post(MIRAGE_DOMIAN + ACTION_ACCOUNT_UPDATE_ACCOUNT, json=data, headers=HEADERS, proxies=PROXIES)
        res_data = res.json()
        if res_data['code'] == 200:
            if quantity > 0:
                log.logger.info(
                    "增加💎 " + str(quantity) + " 元，当前余额 💴：" + str(res_data['data']['bullCoin']) + "  💎：" + str(
                        res_data['data']['sparCoin']))
            elif quantity < 0:
                log.logger.info(
                    "减少💎 " + str(quantity) + " 元，当前余额 💴：" + str(res_data['data']['bullCoin']) + "  💎：" + str(
                        res_data['data']['sparCoin']))
            else:
                log.logger.info(
                    "当前余额 💴：" + str(res_data['data']['bullCoin']) + "  💎：" + str(res_data['data']['sparCoin']))
        else:
            self.log.logger.info(res.text)
            self.log.logger.info("修改💎数据失败")

        return

    def random8int(self):
        return str(random.randint(0, 99999999)).zfill(8)

    def random64hex(self):
        return "".join([random.choice("0123456789abcdef") for i in range(64)])


armada = Armada(sid=CONFIG_STEAMID)
armada.load_player()

if ALLMIGHT['modify_heroEquipmentLevel'] or ALLMIGHT['modify_TREASURES']:
    armada.update_player(modify_hel=ALLMIGHT['modify_heroEquipmentLevel'], modify_tre=ALLMIGHT['modify_TREASURES'])
if ALLMIGHT['modify_TOTEMLevel']:
    armada.update_totem()
if ALLMIGHT['modify_SPARCOIN']:
    armada.update_coin()
if ALLMIGHT['modify_heroEquipmentLevel'] or ALLMIGHT['modify_TREASURES'] or ALLMIGHT['modify_TOTEMLevel'] or ALLMIGHT[
    'modify_SPARCOIN']:
    armada.load_player()
