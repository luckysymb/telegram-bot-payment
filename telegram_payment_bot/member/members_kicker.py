# Copyright (c) 2021 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#
# Imports
#
import time

import pyrogram

from telegram_payment_bot.bot.bot_config_types import BotConfigTypes
from telegram_payment_bot.config.config_object import ConfigObject
from telegram_payment_bot.logger.logger import Logger
from telegram_payment_bot.member.members_payment_getter import MembersPaymentGetter
from telegram_payment_bot.member.members_username_getter import MembersUsernameGetter
from telegram_payment_bot.misc.ban_helper import BanHelper
from telegram_payment_bot.misc.chat_members import ChatMembersList


#
# Classes
#

# Constants for members kicker class
class MembersKickerConst:
    # Sleep time
    SLEEP_TIME_SEC: float = 0.01


# Members kicker class
class MembersKicker:

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    ban_helper: BanHelper
    members_payment_getter: MembersPaymentGetter
    members_username_getter: MembersUsernameGetter

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger) -> None:
        self.client = client
        self.config = config
        self.logger = logger
        self.ban_helper = BanHelper(client)
        self.members_payment_getter = MembersPaymentGetter(client, config, logger)
        self.members_username_getter = MembersUsernameGetter(client, config)

    # Kick all members with expired payment
    def KickAllWithExpiredPayment(self,
                                  chat: pyrogram.types.Chat) -> ChatMembersList:
        no_payment_members = self.members_payment_getter.GetAllMembersWithExpiredPayment(chat)
        if no_payment_members.Any():
            self.__KickMultiple(chat, no_payment_members)
        return no_payment_members

    # Kick single member if expired payment
    def KickSingleIfExpiredPayment(self,
                                   chat: pyrogram.types.Chat,
                                   user: pyrogram.types.User) -> bool:
        payment_expired = self.members_payment_getter.IsSingleMemberExpired(chat, user)
        if payment_expired:
            self.__KickSingle(chat, user)
        return payment_expired

    # Kick all members with no username
    def KickAllWithNoUsername(self,
                              chat: pyrogram.types.Chat) -> ChatMembersList:
        no_username_members = self.members_username_getter.GetAllWithNoUsername(chat)
        if no_username_members.Any():
            self.__KickMultiple(chat, no_username_members)
        return no_username_members

    # Kick single member if no username
    def KickSingleIfNoUsername(self,
                               chat: pyrogram.types.Chat,
                               user: pyrogram.types.User) -> bool:
        no_username = user.username is None
        if no_username:
            self.__KickSingle(chat, user)
        return no_username

    # Kick single
    def __KickSingle(self,
                     chat: pyrogram.types.Chat,
                     user: pyrogram.types.User) -> None:
        if not self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            self.ban_helper.KickUser(chat, user)
        else:
            self.logger.GetLogger().info("Test mode ON: no member was kicked")

    # Kick multiple
    def __KickMultiple(self,
                       chat: pyrogram.types.Chat,
                       members: ChatMembersList) -> None:
        if not self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            for member in members:
                self.ban_helper.KickUser(chat, member.user)
                time.sleep(MembersKickerConst.SLEEP_TIME_SEC)
        else:
            self.logger.GetLogger().info("Test mode ON: no member was kicked")
